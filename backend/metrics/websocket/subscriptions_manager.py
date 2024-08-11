import json
from asyncio import AbstractEventLoop, Event
from collections import defaultdict

from aioredis import ConnectionsPool as RedisConnectionsPool
from aioredis.pubsub import Receiver
from metrics.serialization.metrics import serialize_snapshot
from metrics.views import apply_view, views_list
from sanic.log import logger
from sanic.websocket import ConnectionClosed, WebSocketConnection
from shared.store.store import MetricStore


class SocketUsage:
    def __init__(self, websocket: WebSocketConnection):
        self.websocket = websocket
        self.finished = Event()

    def __hash__(self):
        return hash(self.websocket)


def _build_redis_metric_subscriptions_key(metric_namespace: str) -> str:
    return f"metric-subscriptions:{metric_namespace}"


def _build_redis_view_subscriptions_key(view_namespace: str) -> str:
    return f"view-subscriptions:{view_namespace}"


def _build_redis_view_params_key(view_namespace: str) -> str:
    return f"view-subscription-params:{view_namespace}"


class SubscriptionsManager:
    def __init__(self, redis: RedisConnectionsPool, metric_store: MetricStore):
        super().__init__()

        self._redis = redis
        self._metric_store = metric_store

        self._listeners = defaultdict(set)

    @property
    def streaming_namespaces(self) -> set:
        return set(self._listeners.keys())

    async def run(self, loop: AbstractEventLoop) -> None:
        receiver = Receiver(loop=loop)
        await self._redis.subscribe(receiver.channel("new-metric"))
        await self._redis.subscribe(receiver.channel("value-update"))

        async for channel, message in receiver.iter(encoding="utf-8"):
            metric_namespace, time, values_dict = json.loads(message)
            if channel.name == b"new-metric":
                await self._push_new_metric(metric_namespace, time, values_dict)
            elif channel.name == b"value-update":
                await self._check_for_view_updates(metric_namespace)
                await self._push_metric_update(metric_namespace, time, values_dict)

    # Receive

    async def assign_listener(
        self, websocket: WebSocketConnection, streaming_namespace: str
    ) -> Event:
        socket_usage = SocketUsage(websocket)
        self._listeners[streaming_namespace].add(socket_usage)
        return socket_usage.finished

    async def remove_listener(
        self, websocket: WebSocketConnection, streaming_namespace: str
    ) -> None:
        self._listeners[streaming_namespace].remove(websocket)

    async def subscribe_namespace_to_metrics(
        self, streaming_namespace: str, *metric_namespaces
    ) -> None:
        pipe = self._redis.pipeline()
        for metric_namespace in metric_namespaces:
            pipe.sadd(
                _build_redis_metric_subscriptions_key(metric_namespace),
                streaming_namespace,
            )
        await pipe.execute()
        logger.info(
            "Subscribed '%s' to metrics '%s'", streaming_namespace, metric_namespaces
        )

    async def unsubscribe_namespace_from_metrics(
        self, streaming_namespace: str, *metric_namespaces
    ) -> None:
        pipe = self._redis.pipeline()
        for metric_namespace in metric_namespaces:
            pipe.srem(
                _build_redis_metric_subscriptions_key(metric_namespace),
                streaming_namespace,
            )
        await pipe.execute()
        logger.info(
            "Unsubscribed '%s' from metrics '%s'",
            streaming_namespace,
            metric_namespaces,
        )

    async def subscribe_namespace_to_views(
        self, streaming_namespace: str, *view_namespaces_and_parameters
    ) -> None:
        pipe = self._redis.pipeline()
        for view_namespace, view_params in view_namespaces_and_parameters:
            pipe.sadd(
                _build_redis_view_subscriptions_key(view_namespace),
                streaming_namespace,
            )
            pipe.hmset(
                _build_redis_view_params_key(view_namespace),
                streaming_namespace,
                json.dumps(view_params),
            )
        await pipe.execute()

        view_namespaces = [vnp[0] for vnp in view_namespaces_and_parameters]
        logger.info(
            "Subscribed '%s' to views '%s'", streaming_namespace, view_namespaces
        )

    async def unsubscribe_namespace_from_views(
        self, streaming_namespace: str, *view_namespaces
    ) -> None:
        pipe = self._redis.pipeline()
        for view_namespace in view_namespaces:
            pipe.srem(
                _build_redis_view_subscriptions_key(view_namespace),
                streaming_namespace,
            )
            pipe.hdel(
                _build_redis_view_params_key(view_namespace), streaming_namespace,
            )
        await pipe.execute()
        logger.info(
            "Unubscribed '%s' from views '%s'", streaming_namespace, view_namespaces
        )

    # Send

    async def _fetch_serialized_metrics(self) -> dict:
        if len(self.streaming_namespaces) == 0:
            return {}

        set_keys = [
            _build_redis_metric_subscriptions_key(streaming_namespace)
            for streaming_namespace in self.streaming_namespaces
        ]
        unique_metrics = await self._redis.sunion(*set_keys)

        serialized_metrics = {}
        for metric_namespace in unique_metrics:
            time, fields_dict = await self._metric_store.get_snapshot(metric_namespace)
            serialized_metrics[metric_namespace] = serialize_snapshot(
                metric_namespace, time, fields_dict
            )

        return serialized_metrics

    async def _send_to_namespace(self, streaming_namespace, payload):
        removed_listeners = []
        for socket_usage in self._listeners[streaming_namespace]:
            try:
                await socket_usage.websocket.send(payload)
            except ConnectionClosed:
                removed_listeners.append(socket_usage)
                socket_usage.finished.set()

        for listener in removed_listeners:
            self._listeners[streaming_namespace].remove(listener)

    async def _push_new_metric(
        self, metric_namespace: str, time: int, values_dict: dict
    ) -> None:
        message = serialize_snapshot(metric_namespace, time, values_dict)
        message["type"] = "new-metric"
        message = json.dumps(message)

        for streaming_namespace in self.streaming_namespaces:
            await self._send_to_namespace(streaming_namespace, message)

    async def _push_metric_update(
        self, metric_namespace: str, time: int, values_dict: dict
    ) -> None:
        subscribed_namespaces = await self._redis.smembers(
            _build_redis_metric_subscriptions_key(metric_namespace)
        )

        message = serialize_snapshot(metric_namespace, time, values_dict)
        message["type"] = "metric-update"
        message = json.dumps(message)

        for streaming_namespace in subscribed_namespaces:
            await self._send_to_namespace(streaming_namespace, message)

    # FIXME: view_class typing
    async def _push_view_update(self, view_namespace: str) -> None:
        subscribed_namespaces = await self._redis.smembers(
            _build_redis_view_subscriptions_key(view_namespace)
        )
        if len(subscribed_namespaces) == 0:
            return

        for streaming_namespace in subscribed_namespaces:
            view_params = json.loads(
                await self._redis.hget(
                    _build_redis_view_params_key(view_namespace), streaming_namespace,
                )
            )
            data = await apply_view(view_namespace, view_params, self._metric_store)
            data["type"] = "view-update"
            message = json.dumps(data)
            await self._send_to_namespace(streaming_namespace, message)

    async def _check_for_view_updates(self, metric_namespace: str) -> None:
        for view in views_list:
            if metric_namespace in view.DEPENDS_ON:
                await self._push_view_update(view.NAMESPACE)
