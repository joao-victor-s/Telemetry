from abc import abstractmethod
from typing import Any, Dict, Tuple


class View:
    """Transforms a set of metrics into an arbitrary JSON object"""

    NAMESPACE = "abstract"
    DISPLAY_NAME = "Abstract view"
    DESCRIPTION = "An abstract view"
    DEPENDS_ON = frozenset()

    @classmethod
    def depends_on(cls):
        return cls.DEPENDS_ON

    @abstractmethod
    def process(self, metrics_dict: Dict[str, Tuple[str, int, Any]]) -> Any:
        pass
