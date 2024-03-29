from typing import List, Tuple
from typing_extensions import Self

import numpy as np

from smanim.constants import DEFAULT_STROKE_WIDTH
from smanim.utils import logger
from smanim.utils.color import WHITE, ManimColor
from smanim.mobject.mobject import Mobject
from smanim.typing import InternalPoint3D_Array, Point3D, Point3D_Array


# Note: text is not a VMobject, it's a non-vectorized SVG el
class VMobject(Mobject):
    """Base class for all objects represented by a path of bezier curves, with strokes or fills.
    The `points` attr of instances represents the points in the path of bezier curves.
    """

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
        super().__init__(**kwargs)

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

    # Point ops
    def get_start_anchors(self) -> Point3D_Array:
        return self.points[:: Mobject.points_per_curve]

    def get_end_anchors(self) -> Point3D_Array:
        return self.points[Mobject.points_per_curve - 1 :: Mobject.points_per_curve]

    def get_all_points(self):
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
    def set_fill(self, color: ManimColor, opacity: float = 1.0, family=False):
        self._fill_color = color
        self.fill_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_fill(color=color, opacity=opacity, family=True)

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
    ):
        self._stroke_color = color
        self.stroke_width = width
        self.stroke_opacity = opacity
        if family:
            for mem in self.get_family()[1:]:
                mem.set_stroke(color=color, width=width, opacity=opacity, family=True)


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
