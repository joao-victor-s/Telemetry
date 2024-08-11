import json
from typing import Iterable, Tuple, Union

from aioredis import ConnectionsPool
from shared.store.store import MetricFieldValues

from .store import MetricStore

METRICS_LIST_KEY = "all-metrics"


def _get_hash_key(namespace: str) -> str:
    return f"metric:value:{namespace}"


def _get_set_key(namespace: str) -> str:
    return f"metric:index:{namespace}"


class RedisMetricStore(MetricStore):
    def __init__(self, redis: ConnectionsPool):
        self._redis = redis

    async def update_metric(
        self, namespace: str, time: int, values_dict: MetricFieldValues
    ) -> None:
        pipe = self._redis.pipeline()
        pipe.sadd(METRICS_LIST_KEY, namespace)
        pipe.zadd(_get_set_key(namespace), time, time)
        pipe.hset(_get_hash_key(namespace), time, json.dumps(values_dict))

        redis_response = await pipe.execute()

        # pubsub
        pipe = self._redis.pipeline()
        event_payload = [namespace, time, values_dict]

        is_metric_new = redis_response[0]  # sadd response
        if is_metric_new:
            pipe.publish_json("new-metric", event_payload)

        pipe.publish_json("value-update", event_payload)

        await pipe.execute()

    async def get_snapshot(
        self, namespace: str
    ) -> Union[Tuple[int, MetricFieldValues], Tuple[None, None]]:
        time_tuple_list = await self._redis.zrange(
            _get_set_key(namespace), -1, -1, True
        )
        if len(time_tuple_list) < 1:
            return None, None

        time = int(time_tuple_list[0][1])
        raw_value = await self._redis.hget(_get_hash_key(namespace), time)
        return time, json.loads(raw_value)

    async def get_snapshots(
        self, namespaces: Union[None, Iterable[str]] = None
    ) -> Iterable[Tuple[str, int, MetricFieldValues]]:
        if not namespaces:
            namespaces = await self._redis.smembers(METRICS_LIST_KEY)

        pipe = self._redis.pipeline()
        for namespace in namespaces:
            pipe.zrange(_get_set_key(namespace), -1, -1, True)

        time_tuple_list_list = await pipe.execute()

        pipe = self._redis.pipeline()
        snapshots = []
        fetched = []
        for namespace, time_tuple_list in zip(namespaces, time_tuple_list_list):
            time = None
            if len(time_tuple_list) >= 1:
                time = time_tuple_list[0][1]
                pipe.hget(_get_hash_key(namespace), time)
                fetched.append((namespace, time))
            else:
                snapshots.append((namespace, time, None))

        results = await pipe.execute()

        for result, fetched in zip(results, fetched):
            namespace, time = fetched
            val = json.loads(result)
            snapshots.append((namespace, time, val))

        return snapshots

    async def get_time_history(
        self, namespace: str, time_slice: slice
    ) -> Iterable[Union[Tuple[int, MetricFieldValues], Tuple[None, None]]]:
        time_tuple_list = await self._redis.zrangebyscore(
            _get_set_key(namespace), time_slice.start, time_slice.stop, True
        )
        if len(time_tuple_list) < 1:
            return []

        pipe = self._redis.pipeline()
        for _, time in time_tuple_list:
            pipe.hget(_get_hash_key(namespace), time)

        results = await pipe.execute()

        return [
            (time_tuple[1], json.loads(val))
            for time_tuple, val in zip(time_tuple_list, results)
        ]
