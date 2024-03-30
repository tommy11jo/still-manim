import numpy as np
from smanim.constants import DOWN, LEFT, PI, RIGHT, SMALL_BUFF, UP
from smanim.mobject.line import Line
from smanim.mobject.mobject import Mobject
from smanim.mobject.svg_object import VMobjectFromSVGPath
from smanim.typing import Point3D
from smanim.utils.color import WHITE, ManimColor

import svgelements as se

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


class Brace(VMobjectFromSVGPath):
    def __init__(
        self,
        mobject: Mobject,
        direction: Point3D = DOWN,  # corresponds to edge on mobject
        buff=SMALL_BUFF,
        sharpness=2,
        # stroke_width=0,
        default_fill_color: ManimColor = WHITE,
        **kwargs,
    ):

        default_min_width = 0.90552
        self.buff = buff
        self.mobject = mobject
        if np.array_equal(direction, UP):
            brace_width = mobject.width
            to_rotate = 0
        elif np.array_equal(direction, DOWN):
            brace_width = mobject.width
            to_rotate = PI
        elif np.array_equal(direction, LEFT):
            brace_width = mobject.height
            to_rotate = PI / 2
        elif np.array_equal(direction, RIGHT):
            brace_width = mobject.height
            to_rotate = -PI / 2
        else:
            raise ValueError("Brace must be in UP, DOWN, LEFT, or RIGHT directions")

        linear_section_length = max(
            0,
            (brace_width * sharpness - default_min_width) / 2,
        )

        svg_path_str = path_string_template.format(
            linear_section_length,
            -linear_section_length,
        )
        svg_path = se.Path(d=svg_path_str)
        super().__init__(svg_path, default_fill_color=default_fill_color, **kwargs)
        self.stretch_to_fit_width(brace_width)
        self.rotate(to_rotate, about_point=self.get_center())
        self.next_to(mobject, direction, buff=buff)

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(mobject={self.mobject})"


# Manim originally called this "BraceBetweenPoints"
class BraceBetween(Brace):
    def __init__(
        self,
        start: Point3D | Mobject,
        end: Point3D | Mobject,
        direction: Point3D = DOWN,
        **kwargs,
    ):
        line = Line(start, end)
        self.start_pt, self.end_pt = line.start_pt, line.end_pt
        super().__init__(line, direction=direction, **kwargs)
