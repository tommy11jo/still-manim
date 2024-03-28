from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from typing_extensions import Self

import numpy as np

from smanim.constants import (
    DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    DL,
    DOWN,
    DR,
    LEFT,
    ORIGIN,
    RIGHT,
    UL,
    UP,
    UR,
)
from smanim.typing import InternalPoint3D_Array, Point3D, Vector3D
from smanim.utils.logger import logger


class Mobject(ABC):
    """base class for all objects that take up space"""

    def __init__(self, z_index: int = 0):
        self.points = self.generate_points()
        self.z_index = z_index
        self.submobjects: List[Mobject] = []

    @abstractmethod
    def generate_points(self) -> InternalPoint3D_Array:
        """
        `points` attr can represent the svg path points for VMobjects and the "general shape" for text and image
        """
        pass

    # Grouping
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

    # Positioning
    def get_critical_point(self, direction: Vector3D):
        """9 point bbox: 4 corners, 4 edge points, 1 center"""
        if not (-1 <= direction[0] <= 1 and -1 <= direction[1] <= 1):
            raise ValueError(
                "direction must be [x, x] where x is -1, 0, 1. See constants.py for direction values."
            )
        direction = direction.astype(int)

        # Future: can create `bbox_stale` marker and reuse bbox values when object is not changed
        all_points = np.concatenate(np.array([mob.points for mob in self.get_family()]))
        x_min, y_min, _ = np.min(all_points, axis=0)
        x_max, y_max, _ = np.max(all_points, axis=0)
        x_mid, y_mid = x_min + (x_max - x_min) / 2, y_min + (y_max - y_min) / 2
        # bbox_dirs = [UL, UP, UR, RIGHT, DR, DOWN, DL, LEFT, ORIGIN]
        x_dir = [x_min, x_mid, x_max]
        y_dir = [y_min, y_mid, y_max]

        new_x = x_dir[direction[0] + 1]
        new_y = y_dir[direction[1] + 1]

        return np.array([new_x, new_y, 0])

    def get_top(self):
        return self.get_critical_point(UP)

    def get_bottom(self):
        return self.get_critical_point(DOWN)

    def get_left(self):
        return self.get_critical_point(LEFT)

    def get_center(self):
        return self.get_critical_point(ORIGIN)

    def get_corner(self, direction: Vector3D):
        if not any((direction == cdir).all() for cdir in [UL, UR, DR, DL]):
            raise ValueError("`direction` must be a corner")
        return self.get_critical_point(direction)

    def align_to(
        self,
        mobject_or_point: Mobject | Point3D,
        direction: Vector3D = ORIGIN,
    ) -> Self:
        if isinstance(mobject_or_point, Mobject):
            dest_pt = mobject_or_point.get_critical_point(direction)
        else:
            dest_pt = mobject_or_point
        cur_pt = self.get_critical_point(-direction)
        self.shift(dest_pt - cur_pt)
        return self

    def next_to(
        self,
        mobject_or_point: Mobject | Point3D,
        direction: Vector3D = RIGHT,
        aligned_edge: Vector3D = ORIGIN,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    ) -> Self:
        if (np.abs(direction) + np.abs(aligned_edge) >= 2).any():
            raise ValueError(
                "`direction` and `aligned edge` cannot be along the same axis"
            )
        if isinstance(mobject_or_point, Mobject):
            dest_pt = mobject_or_point.get_critical_point(direction + aligned_edge)
        else:
            dest_pt = mobject_or_point

        cur_pt = self.get_critical_point(-direction + aligned_edge)
        to_shift = (dest_pt - cur_pt) + direction * buff
        self.shift(to_shift)
        return self

    def move_to(
        self, point_or_mobject: Point3D | Mobject, aligned_edge: Vector3D = ORIGIN
    ) -> Self:
        # Test: using aligned edge only makes sense with mobject right
        if isinstance(point_or_mobject, Mobject):
            dest_pt = point_or_mobject.get_critical_point(aligned_edge)
        else:
            dest_pt = point_or_mobject
        cur_pt = self.get_critical_point(aligned_edge)
        self.shift(dest_pt - cur_pt)
        return self

    def shift(self, vector: Vector3D) -> Self:
        for mob in self.get_family():
            mob.points += vector
        return self
