from abc import ABC, abstractmethod


class DelayGenerator(ABC):
    @abstractmethod
    def generate(self) -> float | int: ...
