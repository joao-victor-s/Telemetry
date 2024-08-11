import asyncio
import json

from metrics.serialization.metrics import serialize_many_snapshots
from metrics.websocket.subscriptions_manager import SubscriptionsManager
from sanic import Blueprint
from sanic.request import Request
from sanic.websocket import WebSocketConnection
from shared.store.store import MetricStore

blueprint = Blueprint("streaming_ws", "/ws")


def build_error_response(code: int, message: str) -> dict:
    return json.dumps({"type": "error", "code": code, "message": message})


# TODO: refactor
async def _controller(
    streaming_namespace: str,
    websocket: WebSocketConnection,
    subscriptions_manager: SubscriptionsManager,
    metric_store: MetricStore,
) -> None:
    while True:
        message = await websocket.recv()
        try:
            args = json.loads(message)
        except ValueError:
            await websocket.send(
                build_error_response(400, "Could not parse command as JSON")
            )
            continue
        except Exception:  # pylint: disable=broad-except
            await websocket.send(build_error_response(500, "Internal server error"))
            continue

        command_type = args.get("type", None)

        if command_type == "update":
            await metric_store.update_metric(
                args["namespace"], args["time"], args["fields"]
            )
        elif command_type == "metric_subscribe":
            await subscriptions_manager.subscribe_namespace_to_metrics(
                streaming_namespace, *args["namespaces"]
            )
        elif command_type == "metric_unsubscribe":
            await subscriptions_manager.unsubscribe_namespace_from_metrics(
                streaming_namespace, *args["namespaces"]
            )
        elif command_type == "view_subscribe":
            view_namespaces_and_params = []
            for view_namespace, view_params in args["views"].items():
                view_namespaces_and_params.append((view_namespace, view_params))
            await subscriptions_manager.subscribe_namespace_to_views(
                streaming_namespace, *view_namespaces_and_params
            )
        elif command_type == "view_unsubscribe":
            await subscriptions_manager.unsubscribe_namespace_from_views(
                streaming_namespace, *args["namespaces"]
            )
        elif command_type == "snapshot":
            snapshots = await metric_store.get_snapshots(args.get("namespaces", None))
            response = serialize_many_snapshots(snapshots)
            response["type"] = "snapshot"
            await websocket.send(json.dumps(response))
        else:
            await websocket.send(build_error_response(400, "Invalid command type"))


async def _receiver(
    streaming_namespace: str,
    websocket: WebSocketConnection,
    subscriptions_manager: SubscriptionsManager,
) -> None:
    finished_event = await subscriptions_manager.assign_listener(
        websocket, streaming_namespace
    )
    await finished_event.wait()
    await subscriptions_manager.remove_listener(websocket, streaming_namespace)


@blueprint.websocket("/<streaming_namespace>")
async def socket(
    request: Request, websocket: WebSocketConnection, streaming_namespace: str
):
    controller_task = asyncio.ensure_future(
        _controller(
            streaming_namespace,
            websocket,
            request.app.ctx.subscriptions_manager,
            request.app.ctx.metric_store,
        )
    )
    receiver_task = asyncio.ensure_future(
        _receiver(streaming_namespace, websocket, request.app.ctx.subscriptions_manager)
    )
    tasks = asyncio.gather(controller_task, receiver_task)
    await tasks
