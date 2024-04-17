from __future__ import annotations
import bisect
from typing_extensions import Self

import numpy as np

from abc import ABC, abstractmethod
from smanim.constants import (
    DEFAULT_STROKE_WIDTH,
    ORIGIN,
    OUT,
    PI,
)
from smanim.mobject.group import Group
from smanim.mobject.transformable import TransformableMobject
from smanim.utils.bezier import interpolate
from smanim.utils.color import WHITE, ManimColor
from smanim.typing import (
    InternalPoint3D_Array,
    Point3D,
    Point3D_Array,
    QuadArray_Point3D,
    Vector3,
)
from smanim.utils.space_ops import mirror_vector

__all__ = ["VMobject", "VGroup"]


# Non-Example: text is not a VMobject, it's a non-vectorized SVG el
class VMobject(TransformableMobject, ABC):
    """Base class for all objects represented by a path of bezier curves, with strokes or fills.
    `points` is a list of the points that form bezier curves.
    """

    points_per_curve = 4

    def __init__(
        self,
        color: ManimColor | None = None,
        opacity: float | None = None,
        stroke_color: ManimColor | None = None,
        stroke_opacity: float | None = None,
        stroke_width: float | None = None,
        fill_color: ManimColor | None = None,
        fill_opacity: float | None = None,
        # When scaled, should dashes scale or remain the same size? Remain for now
        dashed: bool = False,
        default_stroke_color: (
            ManimColor | None
        ) = None,  # intended for use by subclasses, takes precedence over `default_fill_color`
        default_fill_color: ManimColor | None = None,  # intended for use by subclasses
        is_closed: bool = True,  # refers to whether the path is closed, used for determining bounding points in `points` setter and adding Z when drawing
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.is_closed = is_closed
        self.generate_points()

        # this VMobject base class chooses to set `fill_color` by default when `color` is set
        # Precedence: fill_color > color > default_fill_color, and same for stroke
        if fill_color is None and stroke_color is None:
            if color is not None:
                fill_color = color
                fill_opacity = fill_opacity or opacity or 1.0
            elif default_fill_color is None and default_stroke_color is not None:
                stroke_color = default_stroke_color
                stroke_opacity = stroke_opacity or opacity or 1.0
                stroke_width = stroke_width or 4.0
            else:
                fill_color = default_fill_color or WHITE
                fill_opacity = fill_opacity or 1.0
        else:
            if color:
                raise ValueError(
                    "Color cannot be set when `fill_color` or `stroke_color` is set."
                )
            if stroke_color is not None:
                stroke_opacity = stroke_opacity or 1.0
                stroke_width = DEFAULT_STROKE_WIDTH
            elif fill_color is not None:
                fill_opacity = fill_opacity or 1.0

        self._stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        self.stroke_width = stroke_width

        self._fill_color = fill_color
        self.fill_opacity = fill_opacity

        # Bug: Not quite evenly spaced, when it should be
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
        self.stroke_dasharray = "8 8" if dashed else "none"

    @abstractmethod
    def generate_points(self) -> None:
        """Generates and sets the VMobject's `points` with the points that form bezier curves"""
        pass

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, new_points: InternalPoint3D_Array):
        """Enforces invariant that `bounding_points` stay updated with VMobject `points`"""
        assert (
            len(new_points) % VMobject.points_per_curve == 0
        ), f"len(new_points) must be divisible by {VMobject.points_per_curve}"
        # `points` are read-only but can be reset via this function
        new_points.flags.writeable = False
        self._points = new_points
        # update the bounding box whenever points are moved
        bounding_points = self.get_start_anchors()
        if not self.is_closed and len(self._points) > 0:
            bounding_points = np.append(
                bounding_points, [self.get_end_anchors()[-1]], axis=0
            )
        self.bounding_points = bounding_points

    ## Point ops
    def get_start_anchors(self) -> InternalPoint3D_Array:
        return self._points[:: VMobject.points_per_curve]

    def get_end_anchors(self) -> InternalPoint3D_Array:
        return self._points[VMobject.points_per_curve - 1 :: VMobject.points_per_curve]

    def get_all_points(self) -> InternalPoint3D_Array:
        all_points = []
        for mob in self.get_family():
            all_points.extend(mob.points)
        return all_points

    def get_points_in_quads(self, points: Point3D_Array) -> QuadArray_Point3D:
        assert len(points) % 4 == 0, "Points should be divisible by 4"
        return [tuple(points[i : i + 4]) for i in range(0, len(points), 4)]

    def append_points(self, new_points: Point3D_Array):
        if len(self.points) == 0:
            self.points = new_points
        else:
            self.points = np.append(self.points, new_points, axis=0)

    ## Color ops
    def set_fill(
        self,
        color: ManimColor | None = None,
        opacity: float | None = None,
        family=False,
    ) -> Self:
        if color:
            self._fill_color = color
        if opacity:
            self.fill_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_fill(color=color, opacity=opacity, family=True)
        return self

    @property
    def stroke_color(self):
        return self._stroke_color

    @stroke_color.setter
    def stroke_color(self, value):
        self._stroke_color = value

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, value):
        self._fill_color = value

    def set_stroke(
        self,
        color: ManimColor | None = None,
        width: float | None = None,
        opacity: float | None = None,
        family=False,
    ) -> Self:
        if color:
            self._stroke_color = color
        if width:
            self.stroke_width = width
        if opacity:
            self.stroke_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_stroke(color=color, width=width, opacity=opacity, family=True)
        return Self

    # whether this vmobject will display a stroke
    def has_stroke(self):
        if self._stroke_color:
            return True
        if self._fill_color:
            return False
        return True

    # whether this vmobject will display a fill
    def has_fill(self):
        return self._fill_color is not None

    # sets stroke and/or fill color if they are showing
    def set_color(self, color: ManimColor, family: bool = True) -> Self:  # override
        if self.has_stroke():
            self.stroke_color = color
        if self.has_fill():
            self.fill_color = color
        if family:
            for mem in self.get_family()[1:]:
                mem.set_color(color=color, family=True)
        return self

    # sets stroke and/or fill opacity if they are showing
    def set_opacity(self, opacity: float, family: bool = True) -> Self:  # override
        if self._stroke_color:
            self.stroke_opacity = opacity
        elif self._fill_color:
            self.fill_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_opacity(opacity=opacity, family=True)
        return self

    def gen_bezier_quad_from_line(self, start: Point3D, end: Point3D) -> Point3D_Array:
        bezier_pts = [
            interpolate(start, end, a)
            for a in np.linspace(0, 1, VMobject.points_per_curve)
        ]
        return bezier_pts

    # TODO: Struggles with high-rate of change, needs debugging but using straight lines isn't that bad for now
    # Might need to use manims approach: lines => make_smooth
    def gen_bezier_quad_smooth_curve(
        self, last_h2: Point3D, last_a2: Point3D, new_anchor: Point3D
    ) -> Point3D_Array:
        """Returns 4 points representing a smooth curve based on the previous handle and anchor points.
        - last_h2: the second handle of the previous quad
        - last_a2: the second anchor of the previous quad"""
        if np.array_equal(last_a2, new_anchor):
            raise Exception("new anchor must be different than last anchor")
        last_tangent = last_a2 - last_h2
        handle1 = last_a2 + last_tangent
        to_anchor_vect = new_anchor - last_a2
        new_tangent = mirror_vector(last_tangent, to_anchor_vect)
        handle2 = new_anchor - new_tangent
        return [last_a2, handle1, handle2, new_anchor]

    def point_from_proportion(self, value: float):
        # This is an approximation with lines. The actual curve lengths are not calculated.
        if 0 > value > 1:
            raise ValueError("Proportion value must be between 0 and 1")
        lengths = [0]
        running_length = 0
        for p1, p2 in zip(self.points, self.points[1:]):
            running_length += np.linalg.norm(p2 - p1)
            lengths.append(running_length)

        total_length = lengths[-1]
        to_travel = value * total_length
        # for equal values, inserts before the first equal occurence
        index = bisect.bisect_left(lengths, to_travel)
        lower, upper = lengths[index - 1], lengths[index]
        # often, the points are evenly space and an exact point is found
        if np.isclose(to_travel, upper):
            return self.points[index]
        else:
            return interpolate(
                self.points[index - 1],
                self.points[index],
                (upper - to_travel) / (upper - lower),
            )

    ## Core transformations
    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = ORIGIN,
    ) -> Self:
        self.points = super().rotate_points(self.points, angle, axis, about_point)
        for mob in self.submobjects:
            mob.rotate(angle, axis, about_point)
        return self

    # FUTURE: Consider scaling the stroke_width, if it exists.
    def scale(self, factor: float, about_point: Point3D | None = ORIGIN) -> Self:
        self.points = super().scale_points(self.points, factor, about_point)
        for mob in self.submobjects:
            mob.scale(factor, about_point)
        return self

    def stretch(self, factor: float, dim: int) -> Self:
        self.points = super().stretch_points(self.points, factor, dim)
        for mob in self.submobjects:
            mob.stretch(factor, dim)
        return self

    def shift(self, vector: Vector3) -> Self:
        self.points = super().shift_points(self.points, vector)
        for mob in self.submobjects:
            mob.shift(vector)
        return self

    def rotate_in_place(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
    ) -> Self:
        return self.rotate(angle, axis, None)

    def scale_in_place(self, factor: float):
        # helper function to scale a vmobject in place (about the vmobject's center)
        return self.scale(factor, None)


class VGroup(Group, VMobject):
    def generate_points(self):
        self.points = np.empty((0, 3))

    def add(self, *vmobjects: VMobject, insert_at_front: bool = False) -> Self:
        to_add = []
        for vmobject in vmobjects:
            if not isinstance(vmobject, VMobject) and not isinstance(vmobject, VGroup):
                raise ValueError("Added item must be of type VMobject or VGroup")
            else:
                to_add.append(vmobject)
        super().add(*to_add, insert_at_front=insert_at_front)
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
