from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable

if TYPE_CHECKING:
    from .element import Element


class Route:
    def __init__(self, element: Optional[Element], block_cond: Optional[Callable[[], bool]] = None):
        self.element = element
        self.block_cond = block_cond

    def is_blocked(self) -> bool:
        if self.block_cond is None:
            return False
        return self.block_cond()
