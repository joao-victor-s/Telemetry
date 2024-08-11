import time
from typing import Any, Dict, Tuple

from metrics.views.view import View


class CarMapView(View):
    NAMESPACE = "car_map"
    DISPLAY_NAME = "Car Map"
    DESCRIPTION = "A view of the car's local data"
    DEPENDS_ON = frozenset(
        [
            "slam.car_pos",
            "slam.cones",
            "path_planning.path",
            "emulator.car_pos",
            "emulator.vision_cones",
            "emulator.fov",
        ]
    )

    def __init__(self, delta=None, **kwargs) -> None:
        super().__init__()

        # TODO: this should maybe be done elsewhere
        if delta is None:
            delta = 10e12
        if isinstance(delta, list):
            delta = delta[0]
        if isinstance(delta, str):
            delta = int(delta)

        self.delta = delta

    def process(self, metrics_dict: Dict[str, Tuple[str, int, Any]]) -> Any:
        reference_time = time.time_ns() // 1000000
        min_required_time = reference_time - self.delta

        filtered_snapshots = []
        for snapshot in metrics_dict.values():
            namespace, metric_time, _ = snapshot

            if metric_time is None or metric_time < min_required_time:
                empty = [namespace, None, None]
                filtered_snapshots.append(empty)
                metrics_dict[namespace] = empty
            else:
                filtered_snapshots.append(snapshot)

        times = [snap[1] for snap in filtered_snapshots if snap[1] is not None]
        if len(times) > 0:
            min_time = min(times)
            max_time = max(times)
        else:
            min_time = None
            max_time = None

        return {
            "namespace": CarMapView.NAMESPACE,
            "meta": {"reference_time": reference_time, "tolerance_delta": self.delta,},
            "timespan": {"min": min_time, "max": max_time,},
            "values": {
                "supervisor": {
                    "pose": metrics_dict.get("slam.car_pos", [0, 0, None])[2],
                    "local_cones": metrics_dict.get("slam.cones", [0, 0, None])[2],
                    "path_points": metrics_dict.get("path_planning.path", [0, 0, None])[
                        2
                    ],
                },
                "emulator": {
                    "pose": metrics_dict.get("emulator.car_pos", [0, 0, None])[2],
                    "local_cones": metrics_dict.get(
                        "emulator.vision_cones", [0, 0, None]
                    )[2],
                    "fov": metrics_dict.get("emulator.fov", [0, 0, None])[2],
                },
            },
        }
