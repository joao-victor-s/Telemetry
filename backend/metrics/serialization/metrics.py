from typing import Iterable, Tuple

from shared.store.store import MetricFieldValues


def _serialize_single_value(time: int, fields_dict: dict) -> dict:
    if time is None and fields_dict is None:
        return None
    return {"time": time, "fields": fields_dict}


def serialize_many_snapshots(
    snapshots: Iterable[Tuple[str, int, MetricFieldValues]]
) -> dict:
    return {
        "metrics": {
            val[0]: _serialize_single_value(val[1], val[2]) for val in snapshots
        }
    }


def serialize_snapshot(metric_namespace: str, time: str, fields_dict: dict) -> dict:
    return {
        "namespace": metric_namespace,
        "snapshot": _serialize_single_value(time, fields_dict),
    }


def serialize_history(metric_namespace: str, history: list) -> dict:
    formatted_history = list(map(lambda item: _serialize_single_value(*item), history))
    return {"namespace": metric_namespace, "history": formatted_history}
