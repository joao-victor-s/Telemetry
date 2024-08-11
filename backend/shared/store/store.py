from abc import abstractmethod
from typing import Iterable, Mapping, Tuple, Union

MetricFieldType = Union[float, Iterable[float], Tuple[float]]

MetricFieldValues = Mapping[str, MetricFieldType]


class MetricStore:
    @abstractmethod
    async def update_metric(
        self, namespace: str, time: int, values_dict: MetricFieldValues
    ) -> None:
        pass

    @abstractmethod
    async def get_snapshots(
        self, namespaces: Union[None, Iterable[str]] = None
    ) -> Iterable[Tuple[str, int, MetricFieldValues]]:
        pass

    @abstractmethod
    async def get_time_history(
        self, namespace: str, time_slice: slice
    ) -> Iterable[Union[Tuple[int, MetricFieldValues], Tuple[None, None]]]:
        pass
