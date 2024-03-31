from pathlib import Path
from typing_extensions import Literal
import numpy as np
from smanim.constants import (
    TEXT_X_PADDING,
    TEXT_Y_PADDING,
    UL,
)
from smanim.mobject.mobject import Mobject
from smanim.typing import Point3D
from smanim.config import CONFIG
from smanim.utils.color import WHITE, ManimColor
from smanim.utils.space_ops import to_manim_len, to_pixel_len
from smanim.utils.text_ops import wrap_text

current_script_directory = Path(__file__).parent

font_family = "computer-modern"
font_dir = "fonts/computer-modern/"
# (Bold, Italic)
font_paths_by_style = {
    (True, False): "cmunbx.ttf",
    (False, True): "cmunti.ttf",
    (False, False): "cmunrm.ttf",
    (True, True): "cmunbi.ttf",
}


# If I don't inherit from VMobject, then I can't make them a family.
# I think I need to create a separate class that allows for "transformable" objects, since this can't be a VMObject (since it doesn't have bezier curves)
# Instead of transforming each of the points for each submobject, we should call the transformable function on submobjects.
# Each transformable requires a getter and setter for points (numpy array) as well as rotate, stretch, shift.
# The base transformable class handles the points and the subclasses can handle additional logic.

# But making this rotatable is a pain since then I need to track pre-rotated points too:
# Example: (50, 50) is center here
# <text x="50" y="50" transform="rotate(45,50,50)" fill="black">Rotated Text</text>

# FUTURE: Add two text elements together


class Text(Mobject):
    def __init__(
        self,
        text: str,
        position: Point3D = UL,  # coords of upper left corner
        start_angle: float = 0,  # in radians
        fill_color: ManimColor = WHITE,
        fill_opacity: float = 1.0,
        max_width: float | None = 2.0,  # in internal manim units
        font_size: int = 20,
        text_decoration: Literal[
            "none", "underline", "overline", "line-through"
        ] = "none",
        bold: bool = False,
        italics: bool = False,
        x_padding: float = TEXT_X_PADDING,
        y_padding: float = TEXT_Y_PADDING,
        **kwargs
    ):
        super().__init__(**kwargs)
        # FUTURE: will need to sanitize if these diagrams can be shared
        self.raw_text = text
        self.heading = start_angle

        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.max_width = max_width
        self.font_size = font_size
        self.font_family = font_family
        self.text_decoration = text_decoration
        font_file = font_paths_by_style[(bold, italics)]

        x_padding_in_pixels = to_pixel_len(x_padding, CONFIG.pw, CONFIG.fw)
        y_padding_in_pixels = to_pixel_len(y_padding, CONFIG.pw, CONFIG.fw)
        max_width_in_pixels = to_pixel_len(max_width, CONFIG.pw, CONFIG.fw)

        self.font_path: Path = current_script_directory / font_dir / font_file
        text_tokens, dims = wrap_text(
            text=text,
            font_path=self.font_path,
            font_size=font_size,
            max_width_in_pixels=max_width_in_pixels,
        )
        self.font_widths = [pair[0] + x_padding_in_pixels * 2 for pair in dims]
        self.font_heights = [
            pair[1] + 2 * y_padding_in_pixels for pair in dims
        ]  # used for drawing
        width_in_munits = to_manim_len(max(self.font_widths), CONFIG.pw, CONFIG.fw)
        height_in_munits = to_manim_len(sum(self.font_heights), CONFIG.pw, CONFIG.fw)

        self.text_tokens = text_tokens
        ur = position + np.eye(3)[0] * width_in_munits
        ul = position
        dl = ul - np.eye(3)[1] * height_in_munits
        dr = ur - np.eye(3)[1] * height_in_munits
        self.set_bounding_points(np.array([ur, ul, dl, dr]))
        self.svg_x = ul[0]  # these points do not change during rotate
        self.svg_y = ul[1]

    # TODO: layout and transformations
    # @property
    # def points(self) -> Vector3D:
    #     # These points can only be changed by setting them or by changing the heading (rotating)
    #     return self.bounding_points

    # @points.setter
    # def points(self, value: Vector3D):
    #     value.flags.writeable = False
    #     super().set_bounding_points(value)

    # @property
    # def heading(self) -> float:
    #     return self._heading

    # @heading.setter
    # def heading(self, value: float) -> None:
    #     self._heading = value
    # new_points = Transformable.rotate()
    # super().set_bounding_points(new_points)

    # def rotate(
    #     self,
    #     angle: float = PI / 4,
    #     axis: Vector3D = OUT,
    #     about_point: Point3D | None = CENTER,
    # ) -> Self:
    #     if not all(about_point == CENTER):
    #         raise ValueError("Can only rotate text about the CENTER")
    #     self.heading += angle
    # leave `svg_x_pt` and `svg_y_pt` alone
    # return super().rotate(angle, axis, about_point)
    # The only ways an objects points can be moved is by shifting them, stretching them, or rotating them
