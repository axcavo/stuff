from abc import ABC, abstractmethod
from typing import Any


class AccessAdapter(ABC):
    identifier: str

    def __init__(self) -> None:
        if not hasattr(self, "identifier"):
            raise AttributeError("Adapter must define an identifier.")

    @abstractmethod
    def get(self, container: Any, key: str) -> Any:
        pass

    @abstractmethod
    def set(self, container: Any, key: str) -> None:
        pass

    @abstractmethod
    def contains(self, container: Any, key: str) -> bool:
        pass