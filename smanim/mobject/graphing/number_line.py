from typing import Sequence

import numpy as np
from smanim.constants import DOWN, LEFT, PI, RIGHT, UP
from smanim.mobject.geometry.line import Arrow, Line, TipableVMobject
from smanim.mobject.graphing.scale import _ScaleBase, LinearBase
from smanim.mobject.mobject import Group
from smanim.mobject.text.text_mobject import Text
from smanim.typing import Point3D


# FUTURE: Just barebones for now, improve later
class NumberLine(TipableVMobject):
    """Creates a number line with tick marks."""

    def __init__(
        self,
        # start (inclusive), end (inclusive), step
        x_range: Sequence[float] | None = [-3, 3, 1],
        length: float | None = None,
        unit_size: float = 1,
        scaling: _ScaleBase = LinearBase(),
        # tick params
        include_ticks: bool = True,
        exclude_origin_tick: bool = False,
        include_numbers: bool = True,
        tick_size: float = 0.1,
        start_tip_arrow: Arrow | None = None,
        end_tip_arrow: Arrow | None = None,
        stroke_width: float = 2.0,
        **kwargs,
    ):
        # Entire __init__ assumes numer line is horizontal
        self.x_range = np.array(x_range, dtype=float)
        self.length = length
        self.unit_size = unit_size
        self.scaling = scaling
        self.x_min, self.x_max, self.x_step = scaling.function(self.x_range)
        if self.x_max <= self.x_min:
            raise ValueError("`x_max` must be > `x_min`")
        self.include_ticks = include_ticks
        self.exclude_origin_tick = exclude_origin_tick
        self.include_numbers = include_numbers
        self.tick_size = tick_size
        # self.start_tip = start_tip
        # self.end_tip = end_tip
        self.start_tip_arrow = start_tip_arrow
        self.end_tip_arrow = end_tip_arrow
        super().__init__(
            self.x_range[0] * RIGHT,
            self.x_range[1] * RIGHT,
            stroke_width=stroke_width,
            **kwargs,
        )
        if length:
            self.length = length
            self.scale(length / self.get_length())
            self.unit_size = self.get_length() / (self.x_range[1] - self.x_range[0])
        else:
            self.scale(self.unit_size)
        self.center()

        if self.include_ticks:
            self.ticks = self.generate_ticks()
            self.add(self.ticks)
        if self.include_numbers:
            ticks_iter = iter(self.ticks)
            label_group = Group()
            for x in self.get_tick_range():
                line: Line = next(ticks_iter)
                num_str = str(int(x)) if int(x) == x else str(x)  # Note: 3.0 == 3
                label = Text(num_str)
                label.next_to(line, DOWN, buff=0)
                label_group.add(label)
            self.add(label_group)

        if self.start_tip_arrow:
            self.start_tip_arrow.rotate(PI)
            self.start_tip_arrow.move_to(self.start, aligned_edge=RIGHT)
            self.add(self.start_tip_arrow)
        if self.end_tip_arrow:
            self.end_tip_arrow.move_to(self.end, aligned_edge=LEFT)
            self.add(self.end_tip_arrow)

    # TODO: Add match_style function
    def generate_ticks(self) -> Group:
        # Assumes numer line is horizontal
        ticks = Group()
        for x in self.get_tick_range():
            tick = Line(DOWN * self.tick_size, UP * self.tick_size)
            pos = self.number_to_point(x)

            tick.move_to(pos)
            # tick.match_style(self)
            ticks.add(tick)

        return ticks

    def get_tick_range(self):
        x_min, x_max, x_step = self.x_range
        # no_origin_included = x_min < x_max < 0 or x_max > x_min > 0
        if not self.exclude_origin_tick:
            tick_range = np.arange(x_min, x_max + 1, x_step)
        else:
            tick_range = np.concatenate(
                (np.arange(x_min, 0, x_step), np.arange(x_step, x_max + 1, x_step))
            )
        return self.scaling.function(tick_range)

    def number_to_point(self, value: float) -> Point3D:
        """Accepts a value along the number line and returns its position in the scene"""
        if value < self.x_min or value > self.x_max:
            raise ValueError(f"Number {value} not on number line")
        units_from_start = value - self.x_min
        return self.start + RIGHT * units_from_start * self.unit_size
