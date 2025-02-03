import math
from core.generators import DelayGenerator
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ConstantGenerator(DelayGenerator):
    value: int | float

    def generate(self):
        return self.value


@dataclass(frozen=True)
class ExponentialGenerator(DelayGenerator):
    mean: float

    def generate(self):
        return np.random.exponential(scale=self.mean)


@dataclass(frozen=True)
class NormalGenerator(DelayGenerator):
    mean: float
    dev: float

    def generate(self):
        return np.random.normal(loc=self.mean, scale=self.dev)


@dataclass(frozen=True)
class BoundedNormalGenerator(NormalGenerator):
    min: float
    max: float

    def generate(self):
        a = super().generate()
        return max(min(a, self.max), self.min)


@dataclass(frozen=True)
class LogNormalGenerator(NormalGenerator):
    def __post_init__(self):
        mu = math.log(self.mean**2 / math.sqrt(self.dev + self.mean**2))
        sigma = math.sqrt(math.log(1 + self.dev / self.mean**2))
        object.__setattr__(self, "mean", mu)
        object.__setattr__(self, "dev", sigma)

    def generate(self):
        return math.exp(super().generate())
