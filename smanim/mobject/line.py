from typing import Tuple
import numpy as np
from smanim.constants import PI, SMALL_BUFF
from smanim.mobject.mobject import Mobject
from smanim.mobject.tips import ArrowTip, ArrowTriangleFilledTip
from smanim.mobject.vmobject import VMobject
from smanim.typing import InternalPoint3D_Array, ManimFloat, Point3D


class Line(VMobject):
    def __init__(
        self, start: Point3D | Mobject, end: Point3D | Mobject, buff=0.0, **kwargs
    ):
        start_pt, end_pt = self.find_line_anchors(start, end)
        if 2 * buff > np.linalg.norm(end_pt - start_pt):
            raise ValueError("Buff is larger than 2 * line_length")

        dir = (end_pt - start_pt) / np.linalg.norm(end_pt - start_pt)
        self.start_pt = start_pt + buff * dir
        self.end_pt = end_pt - buff * dir
        self.buff = buff
        super().__init__(**kwargs)

    def generate_points(self) -> InternalPoint3D_Array:  # override
        dir = self.end_pt - self.start_pt
        return np.array(
            [
                self.start_pt,
                self.start_pt + dir / 3,
                self.start_pt + dir * 2 / 3,
                self.end_pt,
            ],
            dtype=ManimFloat,
        )

    def get_direction(self):
        start_pt, end_pt = self.points[0], self.points[-1]
        return (end_pt - start_pt) / np.linalg.norm(end_pt - start_pt)

    def get_length(self):
        return np.linalg.norm(self.points[-1] - self.points[0])

    def find_line_anchors(
        self, start: Point3D | Mobject, end: Point3D | Mobject
    ) -> Tuple[Point3D, Point3D]:
        # for points, use them as is
        # for mobjects, determine rough direction, then use it to find exact boundaries
        rough_start = start.get_center() if isinstance(start, Mobject) else start
        rough_end = end.get_center() if isinstance(end, Mobject) else end
        dir = rough_end - rough_start

        # TODO: fix this logic
        # shoot through start and find closest line segment intersection with all lines formed by consecutive "defining points" in end mobject
        # must refactor first
        start_pt = (
            start.get_boundary_point(dir) if isinstance(start, Mobject) else start
        )
        end_pt = end.get_boundary_point(-dir) if isinstance(end, Mobject) else end
        return start_pt, end_pt


# Manim uses max_tip_length_to_length_ratio, max_stroke_width_to_length_ratio
# These are unintuitive and annoying to use
# I'm going to try to change them but not confident
"""max_tip_length_to_length_ratio
        `tip_length` scales with the length of the arrow. Increasing this ratio raises the max value of `tip_length`.
    max_stroke_width_to_length_ratio
        `stroke_width` scales with the length of the arrow. Increasing this ratio ratios the max value of `stroke_width`.
"""


class Arrow(Line):
    """An arrow."""

    def __init__(
        self,
        *args,
        stroke_width: float = 6,
        buff: float = SMALL_BUFF,
        # buff: float = 0,
        # max_tip_length_to_length_ratio: float = 0.25,
        # max_stroke_width_to_length_ratio: float = 5,
        # perhaps add defaults tip styles instead
        tip_length: float = 0.2,
        tip_width: float = 0.2,
        tip_shape=ArrowTriangleFilledTip,
        **kwargs,
    ):
        super().__init__(*args, buff=buff, **kwargs)
        self.stroke_width = stroke_width
        self.add_tip(tip_shape=tip_shape, tip_length=tip_length, tip_width=tip_width)

    def add_tip(
        self,
        tip_shape: ArrowTip,
        tip_length: float,
        tip_width: float,
        at_start: bool = False,
    ) -> None:
        # reduce the line length to add the tip, without changing the anchor
        line_start = self.points[0].copy()
        line_length = self.get_length()
        line_dir = self.get_direction()
        self.shift(-line_start)
        self.scale((line_length - tip_length) / line_length)
        self.shift(line_start)
        if at_start:
            # make room at start anchor instead of end anchor
            self.shift(line_dir * tip_length)

        kwargs = {}
        if self.fill_color:
            kwargs["fill_color"] = self.fill_color
        if self.stroke_color:
            kwargs["stroke_color"] = self.stroke_color
        tip: ArrowTip = tip_shape(length=tip_length, width=tip_width, **kwargs)
        x, y = line_dir[:2]
        tip.rotate(np.arctan2(y, x) - PI / 2)

        anchor = self.points[0] if at_start else self.points[-1]
        tip.shift(anchor - tip.base)

        self.add(tip)
