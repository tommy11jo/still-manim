from typing import List, Tuple
from typing_extensions import Self

import numpy as np

from abc import ABC, abstractmethod
from smanim.constants import (
    DEFAULT_STROKE_WIDTH,
    ORIGIN,
    OUT,
    PI,
)
from smanim.mobject.transformable import TransformableMobject
from smanim.utils.logger import log
from smanim.utils.color import WHITE, ManimColor
from smanim.typing import InternalPoint3D_Array, Point3D, Point3D_Array, Vector3


# Note: text is not a VMobject, it's a non-vectorized SVG el
class VMobject(TransformableMobject, ABC):
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

        if (
            default_fill_color is not None
            and fill_color is None
            and stroke_color is None
            and default_stroke_color is None
        ):
            fill_color = default_fill_color
            fill_opacity = 1.0
            self.default_stroke_color = None
        elif stroke_color is None and fill_color is None:
            self.default_stroke_color = default_stroke_color or WHITE
        else:
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
        if not self.is_closed:
            bounding_points = np.append(
                bounding_points, [self.get_end_anchors()[-1]], axis=0
            )
        super().set_bounding_points(bounding_points)

    # Point ops
    def get_start_anchors(self) -> InternalPoint3D_Array:
        return self._points[:: VMobject.points_per_curve]

    def get_end_anchors(self) -> InternalPoint3D_Array:
        return self._points[VMobject.points_per_curve - 1 :: VMobject.points_per_curve]

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

    # Core transformations
    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = None,
    ) -> Self:
        self.points = super().rotate_points(self.points, angle, axis, about_point)
        for mob in self.submobjects:
            # cannot just call super().rotate because this mobject might have different rotating functionality
            mob.rotate(angle, axis, about_point)
        return self

    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:
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


class VGroup(VMobject):
    def __init__(self, *vmobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*vmobjects)

    def generate_points(self) -> None:  # override
        # VGroup is a shell for holding VMobjects so adds no points itself
        self.points = np.array([])

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
                log.warning(f"Object must be VMobject to be added: {vmobject}")
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
