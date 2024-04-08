from __future__ import annotations
from typing_extensions import Self
import numpy as np
from smanim.constants import ORIGIN, UP
from smanim.mobject.mobject import Mobject
from smanim.typing import InternalPoint3D_Array, Point3D, Vector3
from smanim.utils.space_ops import rotation_matrix

__all__ = ["TransformableMobject"]


class TransformableMobject(Mobject):
    # Core transformations
    def rotate_points(
        self,
        points: InternalPoint3D_Array,
        angle: float,
        axis: Vector3,
        about_point: Point3D,
    ) -> InternalPoint3D_Array:
        """Counter-clockwise rotation"""
        points = points.copy()
        if about_point is None:
            about_point = self.get_critical_point(ORIGIN)
        rot_matrix = rotation_matrix(angle, axis)
        points -= about_point
        points = np.dot(points, rot_matrix.T)
        points += about_point
        return points

    def scale_points(
        self,
        points: InternalPoint3D_Array,
        factor: float,
        about_point: Point3D,
    ) -> InternalPoint3D_Array:
        points = points.copy()
        if about_point is None:
            about_point = self.get_center()
        if np.array_equal(about_point, ORIGIN):
            points = points * factor
        else:
            points -= about_point
            points = points * factor
            points += about_point
        return points

    def stretch_points(
        self, points: InternalPoint3D_Array, factor: float, dim: int
    ) -> InternalPoint3D_Array:
        points = points.copy()
        points[:, dim] *= factor
        return points

    def shift_points(
        self, points: InternalPoint3D_Array, vector: Vector3
    ) -> InternalPoint3D_Array:
        points = points.copy()
        points += vector
        return points

    # More specific transformations that require core transformations
    def stretch_to_fit_width(self, width: float) -> Self:
        old_width = self.width
        if old_width == 0:
            return self
        self.stretch(width / old_width, dim=0)
        return self

    def stretch_to_fit_height(self, height: float) -> Self:
        old_height = self.height
        if old_height == 0:
            return self
        self.stretch(height / old_height, dim=1)
        return self

    def scale_to_fit_width(self, width: float) -> Self:
        old_width = self.width
        if old_width == 0:
            return self
        self.scale(width / old_width)
        return self

    def scale_to_fit_height(self, height: float) -> Self:
        old_height = self.height
        if old_height == 0:
            return self
        self.scale(height / old_height)
        return self

    # Frequently used patterns that depend on transformations
    def add_label(self, label: TransformableMobject, direction: Vector3 = UP, buff=0.0):
        label.stretch_to_fit_width(self.width)
        label.next_to(self, direction, buff=buff)
        self.add(label)
