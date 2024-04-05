# class CoordinateSystem:

import numpy as np
from smanim.constants import PI
from smanim.mobject.graphing.number_line import NumberLine
from smanim.mobject.mobject import Group


class Axes(Group):
    def __init__(
        self,
        x_axis: NumberLine | None = None,
        y_axis: NumberLine | None = None,
        # x_origin: float = 0.0,  # coord along x_axis that y_axis should be placed
        # y_origin: float = 0.0,
        **kwargs
    ) -> None:
        # Requires construction of x_axis and y_axis with desired styles
        # Handles all positioning of axes and centers the entire Mobject
        # Entire __init__ assumes x_axis is horizontal and y_axis is vertical
        super().__init__(**kwargs)
        if x_axis is None:
            x_axis = NumberLine(exclude_origin_tick=True)
        if y_axis is None:
            y_axis = NumberLine(exclude_origin_tick=True)
        # if not x_axis.x_min < x_origin < x_axis.x_max:
        #     raise ValueError("`x_axis` must include `x_coord_of_y_axis`")
        # if not y_axis.x_min < y_origin < y_axis.x_max:
        #     raise ValueError("`y_axis` must include `y_coord_of_x_axis`")
        self.x_axis = x_axis
        self.y_axis = y_axis
        # self.origin_coords = (x_origin, y_origin)

        # Move the y_axis to the proper spot on the x_axis
        y_axis.rotate(PI / 2)
        # dest_point = x_axis.coord_to_point(x_origin)
        # start_point = y_axis.coord_to_point(y_origin)

        dest_point = x_axis.coord_to_point(0)
        start_point = y_axis.coord_to_point(0)
        y_axis_center = y_axis.get_center()
        to_center = y_axis_center - start_point
        y_axis.shift(to_center + (dest_point - y_axis_center))

        self.add(x_axis)
        self.add(y_axis)

    def point_to_point(self, x_coord: float, y_coord: float):
        """Accepts a coordinate point on this graph and returns its position in the scene"""
        # Assumes horizontal x_axis and vertical y_axis
        x_coord = self.x_axis.coord_to_point(x_coord)
        y_coord = self.y_axis.coord_to_point(y_coord)
        return np.array([x_coord[0], y_coord[1], 0])
