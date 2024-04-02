from pathlib import Path
from typing_extensions import Literal, Self
import numpy as np
from smanim.constants import (
    ORIGIN,
    OUT,
    PI,
    SMALL_BUFF,
    TEXT_X_PADDING,
    TEXT_Y_PADDING,
    UL,
)
from smanim.mobject.polygon import Polygon
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import Point3D, Vector3
from smanim.config import CONFIG
from smanim.utils.color import WHITE, ManimColor
from smanim.utils.space_ops import to_manim_len, to_pixel_len
from smanim.utils.text_ops import wrap_text
from PIL import ImageFont

__all__ = ["Text"]

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


# FUTURE: Add two text elements together


class Text(TransformableMobject):
    def __init__(
        self,
        text: str,
        position: Point3D = UL,  # coords of upper left corner
        start_angle: float = 0,  # in radians
        fill_color: ManimColor = WHITE,
        fill_opacity: float = 1.0,
        max_width: float | None = 6.0,  # in internal manim units
        z_index: int = 1,  # text is by default above the normal 0 z-index
        font_size: float = 20,
        text_decoration: Literal[
            "none", "underline", "overline", "line-through"
        ] = "none",
        bold: bool = False,
        italics: bool = False,
        x_padding: float = TEXT_X_PADDING,
        y_padding: float = TEXT_Y_PADDING,
        border: bool = False,
        # border_buff: float = 0.1,
        border_buff: float = 0.0,
        **kwargs,
    ):
        if not isinstance(text, str):
            raise ValueError("Text must be a str")
        if len(text) == 0:
            raise ValueError("Text cannot be empty")
        super().__init__(z_index=z_index, **kwargs)
        # FUTURE: will need to sanitize if these diagrams can be shared
        self.raw_text = text
        self._heading = start_angle

        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.max_width = max_width
        self.font_size = font_size
        self.font_family = font_family
        self.text_decoration = text_decoration
        font_file = font_paths_by_style[(bold, italics)]

        self.x_padding_in_pixels = to_pixel_len(x_padding, CONFIG.pw, CONFIG.fw)
        self.y_padding_in_pixels = to_pixel_len(y_padding, CONFIG.pw, CONFIG.fw)
        max_width_in_pixels = to_pixel_len(max_width, CONFIG.pw, CONFIG.fw)

        self.font_path: Path = current_script_directory / font_dir / font_file
        text_tokens, dims = wrap_text(
            text=text,
            font_path=self.font_path,
            font_size=font_size,
            max_width_in_pixels=max_width_in_pixels,
        )
        font = ImageFont.truetype(self.font_path, font_size)
        # line_height = ascent + descent
        # Workaround: ascent seems to be capturing what ascent + descent typically would
        # I think the bbox is including the descent by default
        ascent, descent = font.getmetrics()
        self.font_ascent = ascent
        self.font_descent = descent
        line_height = ascent
        self.leading = line_height * 0.5

        self.font_widths = np.array(
            [pair[0] + self.x_padding_in_pixels * 2 for pair in dims]
        )
        self.font_height = line_height
        line_width_in_munits = (
            max_width + 2 * x_padding
            if len(text_tokens) > 1
            else to_manim_len(self.font_widths[0], CONFIG.pw, CONFIG.fw)
        )
        line_height_in_munits = to_manim_len(self.font_height, CONFIG.pw, CONFIG.fw)
        leading_in_munits = to_manim_len(self.leading, CONFIG.pw, CONFIG.fw)
        font_descent_in_munits = to_manim_len(self.font_descent, CONFIG.pw, CONFIG.fw)

        self.text_tokens = text_tokens
        # Note: first line does not having leading space
        bbox_height = (
            line_height_in_munits * len(text_tokens)
            + leading_in_munits * (len(text_tokens) - 1)
            + y_padding * 2
        ) + font_descent_in_munits
        ur = position + np.eye(3)[0] * (line_width_in_munits + x_padding)
        ul = position
        dl = ul - np.eye(3)[1] * bbox_height
        dr = ur - np.eye(3)[1] * bbox_height
        self.set_bounding_points(np.array([ur, ul, dl, dr]))

        # Note: this point doesn't change during rotate because SVG applies it after. It still changes for other transformations
        # So, `svg_upper_left` can get out of sync with `bounding_points`. Be careful.
        self.svg_upper_left = ul.copy()

        if border:
            border_with_buff = super().scale_points(
                self.bounding_points, 1 + border_buff
            )
            border_polygon = Polygon(
                vertices=border_with_buff,
                default_stroke_color=WHITE,
                stroke_width=0.8,
            )
            self.add(border_polygon)

    @property
    def heading(self) -> float:
        return self._heading

    @heading.setter
    def heading(self, value: float) -> None:
        rot = value - self._heading
        self._heading = value
        bounding_points = super().rotate_points(self.bounding_points, rot, OUT, None)
        super().set_bounding_points(bounding_points)

    def __repr__(self):
        class_name = self.__class__.__qualname__
        return f"{class_name}(value={self.raw_text})"

    def rotate(
        self,
        angle: float = PI / 4,
        axis: Vector3 = OUT,
        about_point: Point3D | None = None,
    ) -> Self:
        # must commute with all other transformations, since it is applied last
        if about_point is not None:
            raise ValueError("Rotation of text mobject must not set `about_point`.")
        # Leaves the `svg_upper_left` unchanged, since a rotation will be applied to it during svg generation
        self.heading = self.heading + angle  # see `heading` setter
        for mob in self.submobjects:
            mob.rotate(angle, axis, about_point)
        return self

    # scales both text and bbox, assumes font size is exactly proportional
    def scale(self, factor: float, about_point: Point3D = ORIGIN) -> Self:
        bounding_points = super().scale_points(
            self.bounding_points, factor, about_point
        )
        super().set_bounding_points(bounding_points)
        self.svg_upper_left = super().scale_points(
            np.array([self.svg_upper_left]), factor, about_point
        )[0]
        self.font_size *= factor
        self.font_widths *= factor
        self.font_height *= factor
        for mob in self.submobjects:
            mob.scale(factor, about_point)
        return self

    # stretches bbox, not the text itself
    def stretch(self, factor: float, dim: int) -> Self:
        bounding_points = super().stretch_points(self.bounding_points, factor, dim)
        super().set_bounding_points(bounding_points)
        self.svg_upper_left = super().stretch_points(
            np.array([self.svg_upper_left]), factor, dim
        )[0]
        for mob in self.submobjects:
            mob.stretch(factor, dim)
        return self

    # shifts the text and text bbox
    def shift(self, vector: Vector3) -> Self:
        bounding_points = super().shift_points(self.bounding_points, vector)
        super().set_bounding_points(bounding_points)
        self.svg_upper_left = super().shift_points(
            np.array([self.svg_upper_left]), vector
        )[0]
        for mob in self.submobjects:
            mob.shift(vector)
        return self

    def add_bg_rectangle(self, buff: float = SMALL_BUFF, rect_config: dict = {}):
        bg_points = super().scale_points(self.bounding_points, 1 + buff)
        bg_polygon = Polygon(
            vertices=bg_points, default_fill_color=CONFIG.bg_color, **rect_config
        )
        self.add(bg_polygon)
