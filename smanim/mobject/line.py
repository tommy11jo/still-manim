from typing import Tuple
from typing_extensions import Self
import numpy as np
from smanim.constants import LEFT, ORIGIN, PI, RIGHT, SMALL_BUFF
from smanim.mobject.mobject import Mobject
from smanim.mobject.tips import ArrowTip, ArrowTriangleFilledTip
from smanim.mobject.vmobject import VMobject
from smanim.typing import ManimFloat, Point3D
from smanim.utils.color import ManimColor
from smanim.utils.logger import log

__all__ = ["Line", "Arrow"]


# TODO: investigate different svg line caps types, fix how arrow looks weird with stroke_width=2.0
class Line(VMobject):
    def __init__(
        self,
        start: Point3D | Mobject = LEFT,
        end: Point3D | Mobject = RIGHT,
        buff=0.0,
        fill_color: ManimColor = None,
        stroke_color: ManimColor = None,
        **kwargs,
    ):
        start_pt, end_pt = self.find_line_anchors(start, end)
        if 2 * buff > np.linalg.norm(end_pt - start_pt):
            raise ValueError("Buff is larger than 2 * line_length")

        dir = (end_pt - start_pt) / np.linalg.norm(end_pt - start_pt)
        self.start_pt = start_pt + buff * dir
        self.end_pt = end_pt - buff * dir
        self.buff = buff
        # set is_closed to False to include the end anchor point in "bounding polygon"
        super().__init__(
            is_closed=False, default_stroke_color=stroke_color or fill_color, **kwargs
        )

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(start={self.start_pt}, end={self.end_pt})"

    def generate_points(self) -> None:  # override
        self.points = self._points_from_start_and_end()

    def _points_from_start_and_end(self):
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

    def set_start_and_end(self, start: Point3D, end: Point3D):
        self.start_pt = start
        self.end_pt = end
        self.points = self._points_from_start_and_end()

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
        start = np.array(start) if isinstance(start, Tuple) else start
        end = np.array(end) if isinstance(start, Tuple) else end
        rough_start = start.get_center() if isinstance(start, Mobject) else start
        rough_end = end.get_center() if isinstance(end, Mobject) else end
        dir = rough_end - rough_start

        start_pt = (
            start
            if not isinstance(start, Mobject)
            else start.get_closest_intersecting_point_2d(rough_start[:2], dir[:2])
        )
        new_dir = rough_end - start_pt
        end_pt = (
            end
            if not isinstance(end, Mobject)
            else end.get_closest_intersecting_point_2d(start_pt[:2], new_dir[:2])
        )

        if np.array_equal(start_pt, end_pt):
            log.warning(
                "Line end points are equal. Increasing end slightly to avoid errors."
            )
            end_pt += 0.0001
        return start_pt, end_pt

    def get_start_point(self):
        return self.start_pt

    def get_end_point(self):
        return self.end_pt

    @property
    def midpoint(self):
        return (self.end_pt + self.start_pt) / 2

    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:  # override
        self.stroke_width *= factor
        return super().scale(factor, about_point)


# Manim uses max_tip_length_to_length_ratio, max_stroke_width_to_length_ratio
# These are unintuitive and annoying to use
# I'm going to try to change them but not confident
"""max_tip_length_to_length_ratio
        `tip_length` scales with the length of the arrow. Increasing this ratio raises the max value of `tip_length`.
    max_stroke_width_to_length_ratio
        `stroke_width` scales with the length of the arrow. Increasing this ratio ratios the max value of `stroke_width`.
"""


class Arrow(Line):
    def __init__(
        self,
        # control line thickness with `stroke_width`
        *args,
        buff: float = SMALL_BUFF,
        # buff: float = 0,
        # max_tip_length_to_length_ratio: float = 0.25,
        # max_stroke_width_to_length_ratio: float = 5,
        # perhaps add defaults tip styles instead
        tip_length: float = 0.2,
        tip_width: float = 0.2,
        tip_scalar: float = 1.0,
        tip_shape=ArrowTriangleFilledTip,
        tip_config: dict = {},
        **kwargs,
    ):
        super().__init__(*args, buff=buff, **kwargs)
        self.add_tip(
            tip_length=tip_length * tip_scalar,
            tip_width=tip_width * tip_scalar,
            tip_shape=tip_shape,
            **tip_config,
        )

    def add_tip(
        self,
        tip_shape: ArrowTip,
        tip_length: float,
        tip_width: float,
        at_start: bool = False,
        **kwargs,
    ) -> None:
        # reduce the line length to add the tip, without changing the anchor
        line_start = self.points[0].copy()
        line_length = self.get_length()
        line_dir = self.get_direction()
        self.scale((line_length - tip_length) / line_length, about_point=line_start)
        if at_start:
            # make room at start anchor instead of end anchor
            self.shift(line_dir * tip_length)

        kwargs["default_fill_color"] = (
            self.stroke_color
        )  # use line color as default arrow color
        tip: ArrowTip = tip_shape(length=tip_length, width=tip_width, **kwargs)
        x, y = line_dir[:2]
        tip.rotate(np.arctan2(y, x) - PI / 2)

        anchor = self.points[0] if at_start else self.points[-1]
        tip.shift(anchor - tip.base)

        self.add(tip)
