from smanim.config import CONFIG
from smanim.constants import LEFT, RIGHT, SMALL_BUFF, UP
from smanim.mobject.geometry.line import Line
from smanim.mobject.group import Group
from smanim.mobject.mobject import Mobject
from smanim.typing import Vector3
from smanim.utils.color import WHITE
from smanim.utils.space_ops import to_manim_len

__all__ = ["BoxList"]


class BoxList(Group):
    def __init__(
        self,
        *mobjects: Mobject,
        aligned_edge: Vector3 = UP,
        x_padding: str = SMALL_BUFF,
        y_padding: float = SMALL_BUFF,
        line_config: dict = {},
        **kwargs
    ):
        super().__init__(**kwargs)
        if len(mobjects) == 0:
            raise ValueError("A BoxList must contain at least one mobject")

        _default_line_config = {
            "stroke_width": 4,
            "opacity": 1.0,
            "color": WHITE,
        }
        line_config.update(_default_line_config)
        _stroke_width = to_manim_len(line_config["stroke_width"], CONFIG.pw, CONFIG.fw)

        self.items = mobjects
        line_xcoords = []
        for i, mobject in enumerate(mobjects):
            if i != 0:
                mobject.next_to(mobjects[i - 1], buff=x_padding * 2)
                mobject.align_to(mobjects[i - 1], edge=aligned_edge)

            x_coord = mobject.left[0] - x_padding
            line_xcoords.append(x_coord)
        line_xcoords.append(mobject.right[0] + x_padding)

        # for mobject in mobjects:
        #     mobject.set_path_if_not_exists(parent=self, subpath=f"[]")
        self.add(*mobjects)

        top_y_coord = self.top[1]

        y_bottom = top_y_coord - self.height - y_padding
        y_top = top_y_coord + y_padding
        vlines = Group()
        for x_coord in line_xcoords:
            ul = [x_coord, y_top, 0]
            dl = [x_coord, y_bottom, 0]
            vlines.add(Line(ul, dl, **line_config))

        self.add(*vlines)

        ur, ul, dl, dr = self.bbox
        ul += LEFT * (_stroke_width / 2)
        ur += RIGHT * (_stroke_width / 2)
        dl += LEFT * (_stroke_width / 2)
        dr += RIGHT * (_stroke_width / 2)
        hlines = Group(Line(ul, ur, **line_config), Line(dl, dr, **line_config))
        self.add(*hlines)

        self.move_to_origin()
