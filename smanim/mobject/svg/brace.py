from __future__ import annotations
import numpy as np
from smanim.constants import DOWN, LEFT, PI, RIGHT, SMALL_BUFF, UP
from smanim.mobject.mobject import Mobject
from smanim.mobject.svg.svg_mobject import VMobjectFromSVGPath
from smanim.mobject.text.text_mobject import Text
from smanim.typing import Point3D
from smanim.utils.color import WHITE, ManimColor, has_default_colors_set

import svgelements as se

from smanim.utils.space_ops import angle_from_vector

__all__ = ["Brace", "LabeledBrace"]

path_string_template = (
    "m0.01216 0c-0.01152 0-0.01216 6.103e-4 -0.01216 0.01311v0.007762c0.06776 "
    "0.122 0.1799 0.1455 0.2307 0.1455h{0}c0.03046 3.899e-4 0.07964 0.00449 "
    "0.1246 0.02636 0.0537 0.02695 0.07418 0.05816 0.08648 0.07769 0.001562 "
    "0.002538 0.004539 0.002563 0.01098 0.002563 0.006444-2e-8 0.009421-2.47e-"
    "5 0.01098-0.002563 0.0123-0.01953 0.03278-0.05074 0.08648-0.07769 0.04491"
    "-0.02187 0.09409-0.02597 0.1246-0.02636h{0}c0.05077 0 0.1629-0.02346 "
    "0.2307-0.1455v-0.007762c-1.78e-6 -0.0125-6.365e-4 -0.01311-0.01216-0.0131"
    "1-0.006444-3.919e-8 -0.009348 2.448e-5 -0.01091 0.002563-0.0123 0.01953-"
    "0.03278 0.05074-0.08648 0.07769-0.04491 0.02187-0.09416 0.02597-0.1246 "
    "0.02636h{1}c-0.04786 0-0.1502 0.02094-0.2185 0.1256-0.06833-0.1046-0.1706"
    "-0.1256-0.2185-0.1256h{1}c-0.03046-3.899e-4 -0.07972-0.004491-0.1246-0.02"
    "636-0.0537-0.02695-0.07418-0.05816-0.08648-0.07769-0.001562-0.002538-"
    "0.004467-0.002563-0.01091-0.002563z"
)


# brace by default has its center "sharp tip" pointing down
class Brace(VMobjectFromSVGPath):
    def __init__(
        self,
        start: Point3D,
        end: Point3D,
        sharpness=2,
        # stroke_width=0,
        color: ManimColor | None = None,
        **kwargs,
    ):
        if not has_default_colors_set(kwargs):
            kwargs["default_fill_color"] = color or WHITE

        self.start = start
        self.end = end
        self.direction = (end - start) / np.linalg.norm(end - start)
        center_pt = (self.end + self.start) / 2

        default_min_width = 0.90552
        width = np.linalg.norm(end - start)

        to_rotate = angle_from_vector(self.direction)
        linear_section_length = max(
            0,
            (width * sharpness - default_min_width) / 2,
        )

        svg_path_str = path_string_template.format(
            linear_section_length,
            -linear_section_length,
        )
        svg_path = se.Path(d=svg_path_str)
        super().__init__(svg_path, **kwargs)
        self.stretch_to_fit_width(width)
        self.rotate(to_rotate, about_point=self.center)
        self.move_to(center_pt)

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(start={self.start}, end={self.end})"

    # Rule: It is expected to use keyword names when constructing any object in still-manim
    # TODO: Use Point3D and Vector3D consistently
    @classmethod
    def from_mobject_edge(
        cls, mobject: Mobject, edge: Point3D = DOWN, buff: float = SMALL_BUFF, **kwargs
    ):
        if np.array_equal(edge, DOWN):
            start = mobject.get_corner(edge + LEFT)
            end = mobject.get_corner(edge + RIGHT)
        elif np.array_equal(edge, UP):
            start = mobject.get_corner(edge + RIGHT)
            end = mobject.get_corner(edge + LEFT)
        elif np.array_equal(edge, RIGHT):
            start = mobject.get_corner(edge + DOWN)
            end = mobject.get_corner(edge + UP)
        elif np.array_equal(edge, LEFT):
            start = mobject.get_corner(edge + UP)
            end = mobject.get_corner(edge + DOWN)
        else:
            raise ValueError("Brace must be in UP, DOWN, LEFT, or RIGHT directions")
        brace = cls(start + edge * buff, end + edge * buff, **kwargs)
        return brace

    @property
    def midpoint(self):
        return self.point_from_proportion(0.25)


# Future: Might make sense to add a mob.next_to_rotated(mob2, dir) where mob2 (and its bbox) is assumed to be rotated by dir (more precision, avoids ugly whitespace)
class LabeledBrace(Brace):
    def __init__(
        self,
        *args,
        label: Text | None = None,
        label_buff: float = 0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if label is None:
            label = Text("label")
        self.add_label(label=label, buff=label_buff)

    def add_label(
        self,
        label: Text,
        buff: float = 0,
    ) -> None:
        diff = self.end - self.start
        line_len = np.linalg.norm(diff)
        unit_dir = diff / line_len
        dir_x, dir_y = unit_dir[:2]
        angle = angle_from_vector(unit_dir)

        if angle > PI:
            angle -= PI
        if angle > PI / 2:
            angle -= PI
        label_height = label.height
        label.rotate_in_place(angle)
        perp_dir = np.array([-dir_y, dir_x, 0])
        midpoint = self.midpoint
        label.move_to(midpoint - perp_dir * (buff + (label_height / 2)))
        self.add(label)
