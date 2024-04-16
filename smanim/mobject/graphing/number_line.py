from typing import Sequence

import numpy as np
from smanim.config import CONFIG
from smanim.constants import DOWN, LEFT, PI, RIGHT, UP
from smanim.mobject.geometry.line import Arrow, Line, TipableLine
from smanim.mobject.graphing.scale import _ScaleBase, LinearBase
from smanim.mobject.group import Group
from smanim.mobject.text.text_mobject import Text
from smanim.mobject.vmobject import VMobject
from smanim.typing import Point3D
from smanim.utils.color import WHITE, ManimColor


# FUTURE: Just barebones for now, improve later
class NumberLine(Group):
    """Creates a number line with tick marks."""

    def __init__(
        self,
        # start (inclusive), end (inclusive), step
        x_range: Sequence[float] | None = [-2, 2, 1],
        length: float | None = CONFIG.fw,  # length does not include arrows right now
        scaling: _ScaleBase | None = None,
        is_horizontal: bool = True,
        include_ticks: bool = True,
        include_origin_tick: bool = True,
        include_numbers: bool = True,
        tick_size: float = 0.1,
        # unlike ticks which are relatively simple, the start and end tip arrows are composed to grant user control over their styles
        include_arrow_tips: bool = True,
        start_arrow_tip: Arrow | None = None,
        end_arrow_tip: Arrow | None = None,
        stroke_width: float = 2.0,
        color: ManimColor = WHITE,
        **kwargs,
    ):
        # Entire __init__ assumes number line is horizontal
        # No need to style VMobjects at constructions. They will be uniformly styled at end of __init__
        super().__init__(**kwargs)
        self.line = TipableLine(
            x_range[0] * RIGHT,
            x_range[1] * RIGHT,
        )
        self.add(self.line)
        if len(x_range) == 2:
            self.x_range = np.array([x_range[0], x_range[1], 1], dtype=float)
        else:
            self.x_range = np.array(x_range, dtype=float)
        if scaling is None:
            scaling = LinearBase()

        self.scaling = scaling
        self.x_min, self.x_max, self.x_step = scaling.function(self.x_range)
        if self.x_max <= self.x_min:
            raise ValueError("`x_max` must be > `x_min`")
        self.include_ticks = include_ticks
        self.include_origin_tick = include_origin_tick
        self.include_numbers = include_numbers
        self.tick_size = tick_size

        if start_arrow_tip is None and include_arrow_tips:
            start_arrow_tip = Arrow(
                start=LEFT / 2,
                end=RIGHT / 2,
            )
        if end_arrow_tip is None and include_arrow_tips:
            end_arrow_tip = Arrow(
                start=LEFT / 2,
                end=RIGHT / 2,
            )

        self.start_tip_arrow = start_arrow_tip
        self.end_tip_arrow = end_arrow_tip

        just_line_length = length
        if self.start_tip_arrow:
            just_line_length -= self.start_tip_arrow.length
        if self.end_tip_arrow:
            just_line_length -= self.end_tip_arrow.length

        self.stretch(just_line_length / self.line.length, dim=0)

        if self.start_tip_arrow:
            self.start_tip_arrow.rotate(PI)
            self.start_tip_arrow.move_to(self.line.start).align_to(
                self.line.start, RIGHT
            )
            self.add(self.start_tip_arrow)
        if self.end_tip_arrow:
            self.end_tip_arrow.move_to(self.line.end).align_to(self.line.end, LEFT)
            self.add(self.end_tip_arrow)
        if self.include_ticks:
            self.ticks = self.generate_ticks()
            self.add(self.ticks)

        self.labels = Group()
        if self.include_numbers:
            ticks_iter = iter(self.ticks)
            label_group = Group()
            for x in self.get_tick_range():
                line: Line = next(ticks_iter)
                num_str = str(int(x)) if int(x) == x else str(x)  # Note: 3.0 == 3
                label = Text(num_str)
                label.next_to(line, DOWN, buff=0)
                label_group.add(label)
            self.labels = label_group
            self.add(label_group)

        if not is_horizontal:
            self.rotate(PI / 2)
        self.move_to_origin()

        # Consistent styles are set at the end so any constructions above don't need to have styles
        self.set_color(color=color, family=True)
        members = self.get_family_members_of_type(VMobject)
        for member in members:
            member.set_stroke(width=stroke_width)

    @property
    def step_size(self):
        return self.line.length / (self.x_max - self.x_min)

    @property
    def length(self):
        return (
            self.line.length + self.start_tip_arrow.length + self.end_tip_arrow.length
        )

    def generate_ticks(self) -> Group:
        # Assumes number line is horizontal
        ticks = Group()
        for x in self.get_tick_range():
            tick = Line(
                DOWN * self.tick_size,
                UP * self.tick_size,
            )
            pos = self.coord_to_point(x)

            tick.move_to(pos)
            ticks.add(tick)

        return ticks

    def get_tick_range(self):
        x_min, x_max, x_step = self.x_range
        # or x_min < x_max < 0 or 0 < x_min < x_max
        if self.include_origin_tick:
            tick_range = np.arange(x_min, x_max + 1, x_step)
        else:
            tick_range = np.concatenate(
                (np.arange(x_min, 0, x_step), np.arange(x_step, x_max + 1, x_step))
            )
        return self.scaling.function(tick_range)

    def coord_to_point(self, value: float) -> Point3D:
        """Accepts a coordinate value along the number line and returns its position in the scene.
        Extrapolate the point even if the point is not directly on the number line"""
        units_from_start = value - self.x_min
        return (
            self.line.start
            + self.line.get_direction() * units_from_start * self.step_size
        )
