from typing import Any, Callable, Sequence
import numpy as np
from smanim.config import CONFIG
from smanim.constants import RIGHT, UP
from smanim.mobject.geometry.line import Line
from smanim.mobject.graphing.functions import ParametricFunction
from smanim.mobject.graphing.number_line import NumberLine
from smanim.mobject.group import Group
from smanim.utils.color import BLUE_D


class Axes(Group):
    def __init__(
        self,
        x_axis: NumberLine | None = None,
        y_axis: NumberLine | None = None,
        num_sampled_graph_points_per_tick: float = 8,
        **kwargs,
    ) -> None:
        # Requires construction of x_axis and y_axis with desired styles
        # Handles all positioning of axes and centers the entire Mobject
        # Entire __init__ assumes x_axis is horizontal and y_axis is vertical
        super().__init__(**kwargs)
        if x_axis is None:
            half_width = int(CONFIG.fw / 2)
            x_range = (-half_width, half_width, 1)
            x_axis = NumberLine(x_range=x_range, include_origin_tick=False)
        if y_axis is None:
            half_height = int(CONFIG.fh / 2)
            y_range = (-half_height, half_height, 1)
            y_axis = NumberLine(
                x_range=y_range, include_origin_tick=False, is_horizontal=False
            )

        self.x_axis = x_axis
        self.y_axis = y_axis
        self.num_sampled_graph_points_per_tick = num_sampled_graph_points_per_tick

        # TODO: Since the y_axis still gets created when its not within the bounds of the canvas, this creates an awkward svg experience
        # But I also need the y_axis to exist in case it gets shifted into the picture (and I don't want to override the shift to reset the whole graph)
        # Move the y_axis to the proper spot on the x_axis
        dest_point = x_axis.coord_to_point(0)
        start_point = y_axis.coord_to_point(0)
        y_axis_center = y_axis.get_center()
        to_center = y_axis_center - start_point
        y_axis.shift(to_center + (dest_point - y_axis_center))

        self.add(x_axis)
        self.add(y_axis)
        self.center()

    def coords_to_point(self, x_coord: float, y_coord: float):
        """Accepts a coordinate point on this graph and returns its position in the scene"""
        # Assumes horizontal x_axis and vertical y_axis
        x_coord = self.x_axis.coord_to_point(x_coord)
        y_coord = self.y_axis.coord_to_point(y_coord)
        return np.array([x_coord[0], y_coord[1], 0])

    def plot(
        self,
        function: Callable[[float], float],
        x_range: Sequence[float] | None = None,
        use_vectorized: bool = False,
        **kwargs: Any,
    ) -> ParametricFunction:
        # May produce inaccurate results. Currently relies on interpolation between evenly-spaced samples of the curves
        if x_range is None:
            sample_rate = self.x_axis.step_size / self.num_sampled_graph_points_per_tick
            x_range = np.array([self.x_axis.x_min, self.x_axis.x_max, sample_rate])
        else:
            x_range = np.array(x_range, dtype=float)

        graph = ParametricFunction(
            function=lambda t: self.coords_to_point(t, function(t)),
            underlying_function=function,
            t_range=x_range,
            scaling=self.x_axis.scaling,
            use_vectorized=use_vectorized,
            **kwargs,
        )
        self.add(graph)
        return graph


class NumberPlane(Axes):
    """2D cartesian plane with grid lines"""

    def __init__(
        self,
        *args,
        coord_step_size: float = 0.5,
        grid_lines: bool = True,
        grid_line_config: dict = {},
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not grid_lines:
            return
        default_grid_line_config = {
            "stroke_color": BLUE_D,
            "stroke_width": 1,
            "stroke_opacity": 0.5,
        }
        grid_line_config.update(default_grid_line_config)
        grid_lines = self.create_grid_lines(coord_step_size, **grid_line_config)
        self.grid_lines = grid_lines
        self.add(grid_lines)
        self.bring_to_back(grid_lines)

    @classmethod
    def from_axes_ranges(
        cls,
        x_axis_range: Sequence[float],
        y_axis_range: Sequence[float],
        x_length: float | None = None,
        y_length: float | None = None,
        fill_canvas: bool = True,  # whether to span the full canvas size
        axis_config: dict = {},
        **kwargs,
    ):
        if fill_canvas:
            x_length = CONFIG.fw
            y_length = CONFIG.fh
        # easiest way to create a 2D cartesian graph with custom ranges is by calling this constructor
        x_axis = NumberLine(
            x_axis_range, include_origin_tick=False, length=x_length, **axis_config
        )
        y_axis = NumberLine(
            y_axis_range,
            include_origin_tick=False,
            length=y_length,
            is_horizontal=False,
            **axis_config,
        )
        return cls(x_axis=x_axis, y_axis=y_axis, **kwargs)

    def create_grid_lines(self, coord_step_size: float, **line_config) -> Group:
        vertical_lines = Group()
        horizontal_lines = Group()
        x_min = self.x_axis.x_min
        x_max = self.x_axis.x_max
        y_min = self.y_axis.x_min
        y_max = self.y_axis.x_max

        x_left = self.x_axis.coord_to_point(x_min)[0]
        x_right = self.x_axis.coord_to_point(x_max)[0]
        y_up = self.y_axis.coord_to_point(y_max)[1]
        y_down = self.y_axis.coord_to_point(y_min)[1]

        x_coord = x_min
        while x_coord <= x_max:
            x_pos = self.x_axis.coord_to_point(x_coord)
            x_comp = x_pos * RIGHT
            line = Line(x_comp + UP * y_up, x_comp + UP * y_down, **line_config)
            vertical_lines.add(line)
            x_coord += coord_step_size

        y_coord = y_min
        while y_coord <= y_max:
            y_pos = self.y_axis.coord_to_point(y_coord)
            y_comp = y_pos * UP
            line = Line(
                y_comp + RIGHT * x_left, y_comp + RIGHT * x_right, **line_config
            )
            horizontal_lines.add(line)
            y_coord += coord_step_size
        return Group(vertical_lines, horizontal_lines)
