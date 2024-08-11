import functools
from urllib.parse import unquote as unquote_urlencoded

from metrics.serialization.metrics import (
    serialize_history,
    serialize_many_snapshots,
    serialize_snapshot,
)
from metrics.util.validation import parse_schema, validate_route_parameter
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from shared.config.metrics import ALLOW_METRIC_MODIFY_HTTP

blueprint = Blueprint("metrics", "/metrics")


def normalize_metric_namespace(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs) -> str:
        kwargs["metric_namespace"] = unquote_urlencoded(kwargs["metric_namespace"])
        return func(
            *args,
            **kwargs
        )
    return wrapped

@blueprint.route("/", methods=["GET"])
async def list_metrics(request: Request):
    metrics = None
    if "metric" in request.args:
        metrics = request.args.getlist("metric")
    snapshots = await request.app.ctx.metric_store.get_snapshots(metrics)
    return json(serialize_many_snapshots(snapshots))


@blueprint.route("/<metric_namespace>", methods=["PUT"])
@normalize_metric_namespace
async def update_metric(request: Request, metric_namespace: str):
    if not ALLOW_METRIC_MODIFY_HTTP:
        return json(
            {"error": "Metric modification via HTTP has been disabled."}, status=403
        )

    await request.app.ctx.metric_store.update_metric(
        metric_namespace,
        request.json["time"],
        # TODO: maybe do value spec checking here or allow mal-formed requests
        request.json["fields"],
    )
    return json({"status": "created"}, status=201)


@blueprint.route("/<metric_namespace>/snapshot", methods=["GET"])
@normalize_metric_namespace
async def get_snapshot(request: Request, metric_namespace: str):
    snapshots = await request.app.ctx.metric_store.get_snapshots([metric_namespace])
    _, time, values_dict = snapshots[0]
    return json(serialize_snapshot(metric_namespace, time, values_dict))


def _validate_history_mode(history_mode: str) -> bool:
    return history_mode in ["time", "absolute"]


@blueprint.route("/<metric_namespace>/history/<history_mode>", methods=["GET"])
@normalize_metric_namespace
# @validate_route_parameter(*_metric_validation_parameters)
@validate_route_parameter(
    "history_mode",
    _validate_history_mode,
    "Supported history modes are 'time' and 'absolute'",
)
@parse_schema(parameters="request.gethistory.parameters")
async def get_history(request: Request, metric_namespace: str, history_mode: str):
    start = request.args.get("start")
    stop = start + request.args.get("length")
    history_slice = slice(start, stop, 1)

    if history_mode == "time":
        history = await request.app.ctx.metric_store.get_time_history(
            metric_namespace, history_slice
        )
    else:
        raise NotImplementedError("Still need to implement 'absolute' history.")
    return json(serialize_history(metric_namespace, history))
