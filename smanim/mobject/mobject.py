from __future__ import annotations

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
from smanim.typing import (
    InternalPoint3D_Array,
    Point2D,
    Point3D,
    Vector3D,
)
from smanim.utils.logger import logger
from smanim.utils.space_ops import line_intersect


class Mobject:
    """base class for all objects that take up space.
    `bounding_points` represents the bounding polygon for this mobject.
    """

    def __init__(self, bounding_points: InternalPoint3D_Array, z_index: int = 0):
        self.bounding_points = bounding_points
        self.z_index = z_index
        self.submobjects: List[Mobject] = []

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

    def get_closest_intersecting_point(
        self, ray_origin: Point2D, ray_direction: Point2D
    ):
        """Return the closest intersecting point between a ray and the bounding polygon of this mobject.
        Handles rays shot from within or from outside the bounding polygon."""
        points_ahead = np.roll(self.bounding_points, -1, axis=0)
        line_segments = [(p1, p2) for p1, p2 in zip(self.bounding_points, points_ahead)]
        intersections_and_params = []
        for p1, p2 in line_segments:
            intersection, param = line_intersect(ray_origin, ray_direction, p1, p2)
            intersections_and_params.append(
                (intersection, param) if intersection is not None else (None, np.inf)
            )
        intersection, param = min(intersections_and_params, key=lambda x: x[1])
        if intersection is None:
            logger.warning("No intersection point found. Illegal ray input.")
            return self.get_center()
        return intersection

    @property
    def width(self):
        return (self.get_right() - self.get_left())[0]

    @property
    def height(self):
        return (self.get_top() - self.get_bottom())[1]

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
