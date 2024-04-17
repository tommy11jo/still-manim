from typing import Tuple
from typing_extensions import Self
import numpy as np
from smanim.constants import LEFT, ORIGIN, PI, RIGHT, SMALL_BUFF
from smanim.mobject.mobject import Mobject
from smanim.mobject.text.text_mobject import Text
from smanim.mobject.geometry.tips import ArrowTip, ArrowTriangleFilledTip
from smanim.mobject.vmobject import VMobject
from smanim.typing import ManimFloat, Point3D, Vector3
from smanim.utils.color import WHITE, ManimColor
from smanim.utils.logger import log
from smanim.utils.space_ops import angle_from_vector

__all__ = ["Line", "Arrow", "Vector", "TipableLine"]


# TODO: investigate different svg line caps types, fix how arrow looks weird with stroke_width=2.0
class Line(VMobject):
    def __init__(
        self,
        start: Point3D | Mobject = LEFT,
        end: Point3D | Mobject = RIGHT,
        buff=0.0,
        # mobjects that cannot have both a stroke and a fill have a user-facing `color` attr
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        **kwargs,
    ):
        start_pt, end_pt = Line.find_line_anchors(start, end)
        if 2 * buff > np.linalg.norm(end_pt - start_pt):
            raise ValueError("Buff is larger than 2 * line_length")

        dir = (end_pt - start_pt) / np.linalg.norm(end_pt - start_pt)
        self._start_pt = start_pt + (buff * dir)
        self._end_pt = end_pt - buff * dir
        self.buff = buff

        # set is_closed to False to include the end anchor point in "bounding polygon"
        super().__init__(
            is_closed=False, stroke_color=color, stroke_opacity=opacity, **kwargs
        )

    @property
    def start(self):
        return self.points[0]

    @property
    def end(self):
        return self.points[-1]

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(start={self.start}, end={self.end})"

    def generate_points(self) -> None:  # override
        self.points = self._points_from_start_and_end()

    def _points_from_start_and_end(self):
        start, end = self._start_pt, self._end_pt
        dir = end - start
        return np.array(
            [
                start,
                start + dir / 3,
                start + dir * 2 / 3,
                end,
            ],
            dtype=ManimFloat,
        )

    def set_start_and_end(self, start: Point3D, end: Point3D):
        self._start_pt = start
        self._end_pt = end
        self.points = self._points_from_start_and_end()

    def get_direction(self):
        return (self.end - self.start) / np.linalg.norm(self.end - self.start)

    def get_angle(self):
        dir = self.get_direction()
        return angle_from_vector(dir)

    @property
    def length(self):
        return np.linalg.norm(self.end - self.start)

    @staticmethod
    def find_line_anchors(
        start: Point3D | Mobject, end: Point3D | Mobject
    ) -> Tuple[Point3D, Point3D]:
        # for points, use them as is
        # for mobjects, determine rough direction, then use it to find exact boundaries
        if isinstance(start, Mobject):
            rough_start = start.center
        else:
            start = np.array(start, dtype=ManimFloat)
            rough_start = start
        if isinstance(end, Mobject):
            rough_end = end.center
        else:
            end = np.array(end, dtype=ManimFloat)
            rough_end = end
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

    # FUTURE: Determine whether this function is worth keeping
    # Helper function for labeling lines/arrows/vectors in their natural direction when possible and always readable
    def add_label(
        self, label: Text, buff: float = SMALL_BUFF, opposite_side=False
    ) -> None:
        diff = self.end - self.start
        line_len = np.linalg.norm(diff)
        unit_dir = diff / line_len
        dir_x, dir_y = unit_dir[:2]
        angle = angle_from_vector(unit_dir)

        flipped_scalar = 1
        if angle >= PI:
            angle -= PI
            flipped_scalar = -1
        if angle >= PI / 2:
            angle -= PI
            flipped_scalar = -1
        label.rotate_in_place(angle)
        perp_dir = np.array([-dir_y, dir_x, 0])
        sign = -1 * flipped_scalar if opposite_side else 1 * flipped_scalar
        midpoint = self.start + unit_dir * (line_len / 2)
        label.move_to(midpoint + sign * perp_dir * buff)
        self.add(label)

    @property
    def midpoint(self):
        return (self.end + self.start) / 2

    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:  # override
        self.stroke_width *= factor
        return super().scale(factor, about_point)


class TipableLine(Line):
    def create_tip(
        self,
        tip_shape: ArrowTip,
        tip_length: float,
        tip_width: float,
        at_start: bool = False,
        **kwargs,
    ) -> ArrowTip:
        # Side effect: reduces the line length to add the tip, without changing the anchor
        line_start = self.start
        line_end = self.end  # cannot use self.end until tip is added
        line_length = self.length
        line_dir = (line_end - line_start) / line_length
        self.scale((line_length - tip_length) / line_length, about_point=line_start)
        if at_start:
            # make room at start anchor instead of end anchor
            self.shift(line_dir * tip_length)

        tip: ArrowTip = tip_shape(
            length=tip_length,
            width=tip_width,
            # use line color as default tip color
            default_fill_color=self.stroke_color,
            **kwargs,
        )
        rotate_scalar = 1 if at_start else -1
        tip.rotate(self.get_angle() + rotate_scalar * PI / 2)

        anchor = self.start if at_start else self.end
        tip.shift(anchor - tip.base)

        return tip


# TODO: Refactor this to take in an instance maybe?
class Arrow(TipableLine):
    def __init__(
        self,
        start: Point3D | Mobject = LEFT,
        end: Point3D | Mobject = RIGHT,
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        buff: float = 0,
        tip_length: float = 0.2,
        tip_width: float = 0.2,
        tip_scalar: float = 1.0,
        tip_shape=ArrowTriangleFilledTip,
        at_start: bool = False,
        at_end: bool = True,
        tip_config: dict = {},
        **kwargs,
    ):
        self.start_tip = None
        self.end_tip = None
        super().__init__(
            start=start, end=end, color=color, opacity=opacity, buff=buff, **kwargs
        )
        if at_end:
            self.end_tip = self.create_tip(
                tip_length=tip_length * tip_scalar,
                tip_width=tip_width * tip_scalar,
                tip_shape=tip_shape,
                at_start=False,
                **tip_config,
            )
            self.add(self.end_tip)
        if at_start:
            self.start_tip = self.end_tip = self.create_tip(
                tip_length=tip_length * tip_scalar,
                tip_width=tip_width * tip_scalar,
                tip_shape=tip_shape,
                at_start=True,
                **tip_config,
            )
            self.add(self.start_tip)
        self.set_color(color)
        self.set_opacity(opacity)

    @property
    def start(self) -> Point3D:  # override
        if not self.start_tip:
            return super().start
        return self.start_tip.tip_point

    @property
    def end(self) -> Point3D:  # override
        if not self.end_tip:
            return super().end
        return self.end_tip.tip_point


class Vector(Arrow):
    def __init__(self, direction: Vector3 = RIGHT, **kwargs):
        super().__init__(ORIGIN, direction, **kwargs)
