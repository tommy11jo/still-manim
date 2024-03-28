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
    OUT,
    PI,
    RIGHT,
    UL,
    UP,
    UR,
)
from smanim.typing import InternalPoint3D_Array, Point2D, Point3D, Vector3D
from smanim.utils.logger import logger
from smanim.utils.space_ops import rotation_matrix


class Mobject(ABC):
    """base class for all objects that take up space"""

    def __init__(self, z_index: int = 0):
        self.points = self.generate_points()
        self.z_index = z_index
        self.submobjects: List[Mobject] = []

    @abstractmethod
    def generate_points(self) -> InternalPoint3D_Array:
        """
        generated points represent the svg path points for VMobjects and the "general shape" for text and image objects
        """
        pass

    # Grouping
    def add(self, *mobjects: Mobject, insert_before=False):
        new_mobjects = []
        for mobject in mobjects:
            if mobject is self:
                logger.error("Cannot add mobject to itself")
            if mobject in self.submobjects:
                logger.warning(f"Mobject already added: {mobject}")
            else:
                new_mobjects.append(mobject)
        if not insert_before:
            self.submobjects.extend(new_mobjects)
        else:
            self.submobjects = new_mobjects + self.submobjects

    def remove(self, *mobjects):
        for mobject in mobjects:
            if mobject is self:
                logger.error("Cannot remove mobject from itself")
            if mobject not in self.submobjects:
                logger.warning(f"Mobject not found: {mobject}")
            else:
                self.submobjects.remove(mobject)

    def get_family(self):
        family = [self]
        for s in self.submobjects:
            family.extend(s.get_family())
        return family

    # Bounding Box Ops
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

    def get_right(self):
        return self.get_critical_point(RIGHT)

    def get_center(self):
        return self.get_critical_point(ORIGIN)

    def get_corner(self, direction: Vector3D):
        if not any((direction == cdir).all() for cdir in [UL, UR, DR, DL]):
            raise ValueError("`direction` must be a corner")
        return self.get_critical_point(direction)

    @property
    def width(self):
        return self.get_left() - self.get_right()

    @property
    def height(self):
        return self.get_top() - self.get_bottom()

    # Absolute Positioning
    def set_position(self, coord: Point2D | Point3D) -> Self:
        """Set the center of this mobject to `coord`."""
        if len(coord) == 2:
            coord = np.append(coord, 0)
        return self.shift(coord - self.get_center())

    def set_x(self, x: float) -> Self:
        """Set x value of the center of this mobject"""
        x_pt = self.get_center().copy()
        x_pt[0] = x
        return self.set_position(x_pt)

    def set_y(self, y: float) -> Self:
        """Set y value of the center of this mobject"""
        y_pt = self.get_center().copy()
        y_pt[1] = y
        return self.set_position(y_pt)

    # Relative Positioning
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

    # Transformations
    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3D = OUT,
        about_point: Point3D | None = None,
    ) -> Self:
        """Counter-clockwise rotation"""
        if about_point is None:
            about_point = self.get_critical_point(ORIGIN)
        rot_matrix = rotation_matrix(angle, axis)
        for mob in self.get_family():
            mob.points -= about_point
            mob.points = np.dot(mob.points, rot_matrix.T)
            mob.points += about_point
        return self

    def scale(self, factor: float) -> Self:
        for mob in self.get_family():
            mob.points *= factor
        return self

    def stretch(self, factor: float, dim: int) -> Self:
        for mob in self.get_family():
            mob.points[:, dim] = factor

    def stretch_to_fit_width(self, width: float, **kwargs) -> Self:
        old_length = self.width()
        if old_length == 0:
            return self
        self.stretch(width / old_length, dim=0)
        return self

    def stretch_to_fit_height(self, height: float, **kwargs) -> Self:
        old_length = self.height()
        if old_length == 0:
            return self
        self.stretch(height / old_length, dim=1)
        return self
