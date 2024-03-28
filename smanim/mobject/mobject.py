from abc import ABC
from typing import List

from smanim.typing import Point3D
from smanim.utils.logger import logger


class Mobject(ABC):
    "base class for all objects that take up space"

    def __init__(self, points: List[Point3D], z_index: int = 0, **kwargs):
        self._setup_bbox(points)
        self.z_index = z_index

        self.submobjects: List[Mobject] = []

    def _setup_bbox(self, points):
        # 9 point bbox
        pass

    def add(self, *mobjects):
        for mobject in mobjects:
            if mobject is self:
                logger.error("Cannot add mobject to itself")
            if mobject in self.submobjects:
                logger.warning(f"Mobject already added: {mobject}")
            else:
                self.submobjects.append(mobject)

    def remove(self, *mobjects):
        for mobject in mobjects:
            if mobject is self:
                logger.error("Cannot remove mobject from itself")
            if mobject not in self.submobjects:
                logger.warning(f"Mobject not found: {mobject}")
            else:
                self.submobjects.remove(mobject)

    def get_family(self):
        return [self] + [s.get_family() for s in self.submobjects]
