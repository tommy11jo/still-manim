import base64
from pathlib import Path
import subprocess
from textwrap import dedent
from typing import List, Sequence

import numpy as np

from smanim.config import CONFIG, Config
from smanim.mobject.mobject import Mobject
from smanim.mobject.vmobject import VMobject
from smanim.mobject.text_mobject import Text
from smanim.utils.logger import logger

import itertools as it
import svg

from smanim.utils.space_ops import to_pixel_coords

__all__ = ["canvas"]


class Canvas:
    def __init__(self, config: Config):
        self.config = config

        # Should this be a VGroup?
        self.mobjects: List[Mobject] = []
        self.num_snapshots = 0

    def add(self, *mobjects):
        for mobject in mobjects:
            if mobject in self.mobjects:
                logger.warning(f"Mobject already added: {mobject}")
            else:
                self.mobjects.append(mobject)

    def remove(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.mobjects:
                logger.warning(f"Mobject not found: {mobject}")
            else:
                self.mobjects.remove(mobject)

    def clear(self):
        self.mobjects = []

    def get_mobjects_to_display(
        self,
        use_z_index=True,
    ):
        cur_mobjects = it.chain(*(m.get_family() for m in self.mobjects))

        if use_z_index:
            return sorted(cur_mobjects, key=lambda m: m.z_index)
        return cur_mobjects

    def get_to_svg_func(self, mobject: Mobject):
        to_svg_funcs = {
            VMobject: self.vmobject_to_svg_el,
            Text: self.text_to_svg_el,
            Mobject: lambda mobject: mobject,  # do nothing
        }
        for _type in to_svg_funcs:
            if isinstance(mobject, _type):
                return to_svg_funcs[_type]
        raise TypeError(f"Displaying an object of class {_type} is not supported")

    def snapshot(self, preview=False):
        mobjects_in_order = self.get_mobjects_to_display()
        svg_els_lst: List[svg.Element] = [
            svg.Rect(width="100%", height="100%", fill=self.config.bg_color.value)
        ]
        for mobject in mobjects_in_order:
            new_svg_els = self.get_to_svg_func(mobject)(mobject)
            svg_els_lst.extend(new_svg_els)
        svg_view_obj = svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.config.pw, self.config.ph),
            elements=svg_els_lst,
        )
        self.save_svg(svg_view_obj, preview=preview, suffix=self.num_snapshots)

        self.num_snapshots += 1

    def vmobject_to_svg_el(self, vmobject: VMobject) -> Sequence[svg.Element]:
        points = to_pixel_coords(
            vmobject.points,
            self.config.pw,
            self.config.ph,
            self.config.fw,
            self.config.fh,
            self.config.fc,
        )
        if len(points) == 0:
            return

        quads = vmobject.get_points_in_quads(points)
        svg_path = []
        start = quads[0][0]
        # assumes a continuous path, no subpaths (for now)
        svg_path.append(svg.M(*start[:2]))
        for _p0, p1, p2, p3 in quads:
            svg_path.append(svg.C(*p1[:2], *p2[:2], *p3[:2]))

        if vmobject.is_closed:
            svg_path.append(svg.Z())
        kwargs = {}

        def orNone(value: any):
            return value if value is not None else "none"

        if vmobject.stroke_opacity > 0.0 and vmobject.stroke_width > 0.0:
            kwargs["stroke"] = orNone(
                None
                if not vmobject.stroke_color
                else orNone(vmobject.stroke_color.value)
            )
            kwargs["stroke_width"] = orNone(vmobject.stroke_width)
            # Note: stroke_opacity as "none" defaults to opaque
            kwargs["stroke_opacity"] = orNone(vmobject.stroke_opacity)
        kwargs["fill_opacity"] = orNone(vmobject.fill_opacity)
        kwargs["fill"] = orNone(
            None if not vmobject.fill_color else orNone(vmobject.fill_color.value)
        )
        kwargs["stroke_dasharray"] = vmobject.stroke_dasharray

        return (svg.Path(d=svg_path, **kwargs),)

    def text_to_svg_el(self, text_obj: Text):

        start_pt = to_pixel_coords(
            np.array([np.array([text_obj.svg_x, text_obj.svg_y, 0])]),
            self.config.pw,
            self.config.ph,
            self.config.fw,
            self.config.fh,
            self.config.fc,
        )[0]
        font_family = text_obj.font_family
        font_size = text_obj.font_size
        # for browser, should be able to set font path to be in pyodide native FS
        with open(text_obj.font_path, "rb") as font_file:
            font_data = font_file.read()
        base64_font = base64.b64encode(font_data).decode("utf-8")

        # can use foreign object to handle max_width and text wrapping in browser envs, but not for local svg
        font_style_inline_font = dedent(
            f"""
            @font-face {{ font-family: {font_family}; src: url(data:font/otf;base64,{base64_font}) format('opentype'); }}
            .styleClass {{
                text-decoration: {font_family};
                fill: {text_obj.fill_color.value};
                font-size: {font_size};
                fill-opacity: {text_obj.fill_opacity};
                font-family: {font_family};
            }}
            
            """
        )

        text_tspan_objs = []

        for i, raw_text in enumerate(text_obj.text_tokens):
            text_tspan_objs.append(
                svg.TSpan(
                    text=raw_text,
                    x=start_pt[0],
                    dy=text_obj.font_heights[i],
                )
                # svg.TSpan(text=raw_text, x=start_pt[0], dy=0)
            )
        text_svg_obj = svg.Text(
            elements=text_tspan_objs,
            x=start_pt[0],
            y=start_pt[1],
            class_=["styleClass"],
        )

        return svg.Style(text=font_style_inline_font), text_svg_obj

    def save_svg(
        self,
        svg_obj: svg.SVG,
        name: str = "test",
        preview: bool = False,
        suffix: int | str = "",
    ):
        script_dir = Path(self.config.save_file_dir)
        fpath = script_dir / f"{name}{suffix}.svg"

        with open(fpath, "w") as file:
            file.write(str(svg_obj))
        if preview:
            subprocess.run(["open", fpath])


canvas = Canvas(CONFIG)
