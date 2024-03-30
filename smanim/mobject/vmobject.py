from typing import List, Tuple
from typing_extensions import Self

import numpy as np

from abc import ABC, abstractmethod
from smanim.constants import (
    DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
    DEFAULT_STROKE_WIDTH,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
)
from smanim.utils import logger
from smanim.utils.color import WHITE, ManimColor
from smanim.mobject.mobject import Mobject
from smanim.typing import InternalPoint3D_Array, Point3D, Point3D_Array, Vector3D
from smanim.utils.space_ops import rotation_matrix


# Note: text is not a VMobject, it's a non-vectorized SVG el
class VMobject(ABC, Mobject):
    """Base class for all objects represented by a path of bezier curves, with strokes or fills.
    `points` is a list of the points that form bezier curves.
    """

    points_per_curve = 4

    def __init__(
        self,
        stroke_color: ManimColor | None = None,
        stroke_opacity: float = 1.0,
        stroke_width: float | None = DEFAULT_STROKE_WIDTH,
        fill_color: ManimColor | None = None,
        fill_opacity: float | None = None,
        # When scaled, should dashes scale or remain the same size? Remain for now
        dashed: bool = False,
        default_stroke_color: ManimColor = WHITE,  # intended for use by subclasses
        **kwargs,
    ):
        # self.set_points(self.generate_points())
        self.points = self.generate_points()
        bounding_points: InternalPoint3D_Array = self.get_start_anchors()

        super().__init__(bounding_points=bounding_points, **kwargs)

        if not stroke_color and not fill_color:
            self._stroke_color = default_stroke_color
        self.default_stroke_color = default_stroke_color

        self._stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        self.stroke_width = stroke_width
        self._fill_color = fill_color
        self.fill_opacity = fill_opacity
        # Bug: Not quite evenly spaced, when it should be
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
        self.stroke_dasharray = "8 8" if dashed else "none"

    @abstractmethod
    def generate_points(self) -> InternalPoint3D_Array:
        pass

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, new_points: InternalPoint3D_Array):
        """Enforces invariant that bounding_points stay updated with VMobject points"""
        # `points` are read-only but can be reset via this function
        new_points.flags.writeable = False
        self._points = new_points
        # update the bounding box whenever points are moved
        super().set_bounding_points(self.get_start_anchors())

    # Point ops
    def get_start_anchors(self) -> InternalPoint3D_Array:
        return self.points[:: VMobject.points_per_curve]

    def get_end_anchors(self) -> InternalPoint3D_Array:
        return self.points[VMobject.points_per_curve - 1 :: VMobject.points_per_curve]

    def get_all_points(self) -> InternalPoint3D_Array:
        all_points = []
        for mob in self.get_family():
            all_points.extend(mob.points)
        return all_points

    def get_points_in_quads(
        self, points: Point3D_Array
    ) -> List[Tuple[Point3D, Point3D, Point3D, Point3D]]:
        assert len(points) % 4 == 0, "Points should be divisible by 4"
        return [tuple(points[i : i + 4]) for i in range(0, len(points), 4)]

    def append_points(self, new_points: Point3D_Array):
        if len(self.points) == 0:
            self.points = new_points
        else:
            self.points = np.append(self.points, new_points, axis=0)

    # Positioning ops
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
        if isinstance(point_or_mobject, Mobject):
            # Use of aligned edge deviates from original manim by placing at center, not `aligned_edge` point
            dest_pt = point_or_mobject.get_critical_point(ORIGIN)
        else:
            dest_pt = point_or_mobject
        cur_pt = self.get_critical_point(aligned_edge)
        self.shift(dest_pt - cur_pt)

        return self

    def shift(self, vector: Vector3D) -> Self:
        for mob in self.get_family():
            mob.points = mob.points + vector
        return self

    # Color ops
    def set_fill(self, color: ManimColor, opacity: float = 1.0, family=False) -> Self:
        self._fill_color = color
        self.fill_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_fill(color=color, opacity=opacity, family=True)
        return self

    @property
    def stroke_color(self):
        if self._stroke_color:
            return self._stroke_color
        if self._fill_color:
            return None
        # default appearance of VMobject is stroke with default color
        return self.default_stroke_color

    @stroke_color.setter
    def stroke_color(self, value):
        self._stroke_color = value

    @property
    def fill_color(self):
        if self._fill_color:
            return self._fill_color
        return None

    @fill_color.setter
    def fill_color(self, value):
        self._fill_color = value

    def set_stroke(
        self,
        color: ManimColor,
        width: float = DEFAULT_STROKE_WIDTH,
        opacity: float = 1.0,
        family=False,
    ) -> Self:
        self._stroke_color = color
        self.stroke_width = width
        self.stroke_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_stroke(color=color, width=width, opacity=opacity, family=True)
        return Self

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
            new_points = mob.points.copy()
            new_points -= about_point
            new_points = np.dot(new_points, rot_matrix.T)
            new_points += about_point
            mob.points = new_points
        return self

    def scale(self, factor: float) -> Self:
        for mob in self.get_family():
            mob.points = mob.points * factor
        return self

    def stretch(self, factor: float, dim: int) -> Self:
        for mob in self.get_family():
            new_points = mob.points.copy()
            new_points[:, dim] *= factor
            mob.points = new_points

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


class VGroup(VMobject):
    def __init__(self, *vmobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*vmobjects)

    def generate_points(self) -> InternalPoint3D_Array:  # override
        # VGroup is a shell for holding VMobjects so adds no points itself
        return []

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({", ".join(str(mob) for mob in self.submobjects)})'

    def __iter__(self):
        return iter(self.submobjects)

    def __getitem__(self, index: int) -> VMobject:
        return self.submobjects[index]

    def add(self, *vmobjects: VMobject) -> Self:
        to_add = []
        for vmobject in vmobjects:
            if not isinstance(vmobject, VMobject):
                logger.warning(f"Object must be VMobject to be added: {vmobject}")
            else:
                to_add.append(vmobject)
        super().add(*to_add)
        return self

    def set_fill(self, color: ManimColor, opacity: float = 1.0):
        super().set_fill(color=color, opacity=opacity, family=True)

    def set_stroke(
        self,
        color: ManimColor,
        width: float = DEFAULT_STROKE_WIDTH,
        opacity: float = 1.0,
    ):
        super().set_stroke(color=color, width=width, opacity=opacity, family=True)
