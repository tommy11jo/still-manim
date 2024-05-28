import numpy as np
from smanim.config import CONFIG
from smanim.constants import DOWN, LEFT, RIGHT, SMALL_BUFF, UP
from smanim.mobject.geometry.line import Line
from smanim.mobject.group import Group
from smanim.mobject.mobject import Mobject
from smanim.mobject.vmobject import VGroup
from smanim.typing import Vector3
from smanim.utils.color import WHITE
from smanim.utils.space_ops import to_manim_len

__all__ = ["BoxList"]


class BoxList(Group):
    def __init__(
        self,
        *mobjects: Mobject,
        direction: Vector3 = RIGHT,
        aligned_edge: Vector3 | None = None,
        x_padding: str = SMALL_BUFF,
        y_padding: float = SMALL_BUFF,
        line_config: dict = {},
        **kwargs
    ):
        super().__init__(**kwargs)
        if len(mobjects) == 0:
            raise ValueError("A BoxList must contain at least one mobject")
        if not any(np.array_equal(direction, cdir) for cdir in [RIGHT, LEFT, UP, DOWN]):
            raise ValueError("`direction` must be a cardinal direction")
        is_vertical = np.array_equal(direction, UP) or np.array_equal(direction, DOWN)
        if aligned_edge is None:
            aligned_edge = UP if not is_vertical else LEFT

        updated_line_config = {
            "stroke_width": 4,
            "opacity": 1.0,
            "color": WHITE,
        }
        updated_line_config.update(line_config)
        _stroke_width = to_manim_len(
            updated_line_config["stroke_width"], CONFIG.pw, CONFIG.fw
        )

        self.items = mobjects
        for i, mobject in enumerate(mobjects):
            if i != 0:
                mobject.next_to(
                    mobjects[i - 1],
                    direction=direction,
                    aligned_edge=aligned_edge,
                    buff=x_padding * 2,
                )

        self.add(*mobjects)

        if not is_vertical:
            top_y_coord = self.top[1]
            y_bottom = top_y_coord - self.height - y_padding
            y_top = top_y_coord + y_padding

            x_line_coords = []
            for mobject in mobjects:
                x_point = mobject.get_critical_point(-direction) - direction * x_padding
                x_line_coords.append(x_point[0])
            x_point = mobject.get_critical_point(direction) + direction * x_padding
            x_line_coords.append(x_point[0])
            vlines = VGroup()
            for x_coord in x_line_coords:
                ul = [x_coord, y_top, 0]
                dl = [x_coord, y_bottom, 0]
                vlines.add(Line(ul, dl, **updated_line_config))
            self.add(*vlines)

            ur, ul, dl, dr = self.bbox
            ul += LEFT * (_stroke_width / 2)
            ur += RIGHT * (_stroke_width / 2)
            dl += LEFT * (_stroke_width / 2)
            dr += RIGHT * (_stroke_width / 2)
            hlines = Group(
                Line(ul, ur, **updated_line_config), Line(dl, dr, **updated_line_config)
            )
            self.add(*hlines)
        else:
            left_x_coord = self.left[0]
            x_right = left_x_coord + self.width + x_padding - _stroke_width / 2
            x_left = left_x_coord - x_padding + _stroke_width / 2

            y_line_coords = []
            for mobject in mobjects:
                y_point = mobject.get_critical_point(-direction) - direction * y_padding
                y_line_coords.append(y_point[1])
            y_point = mobject.get_critical_point(direction) + direction * y_padding
            y_line_coords.append(y_point[1])

            hlines = VGroup()
            for y_coord in y_line_coords:
                ul = [x_left, y_coord, 0]
                ur = [x_right, y_coord, 0]
                hlines.add(Line(ul, ur, **updated_line_config))
            self.add(*hlines)

            ur, ul, dl, dr = self.bbox
            ul += UP * (_stroke_width / 2)
            ur += UP * (_stroke_width / 2)
            dl += DOWN * (_stroke_width / 2)
            dr += DOWN * (_stroke_width / 2)
            vlines = Group(
                Line(ul, dl, **updated_line_config), Line(ur, dr, **updated_line_config)
            )
            self.add(*vlines)

        self.move_to_origin()
