from pathlib import Path
import subprocess
from typing import List

from smanim.constants import ORIGIN
from smanim.mobject.mobject import Mobject
from smanim.mobject.vmobject import VMobject
from smanim.utils.logger import logger
from smanim.utils.color import BLACK, ManimColor

import itertools as it
import svg

from smanim.utils.space_ops import to_pixel_coords


class Canvas:
    def __init__(
        self,
        pixel_height: float = 900,
        frame_height: float = 8,
        aspect_ratio: float = 16 / 9,
        frame_center: float = ORIGIN,
        bg_color: ManimColor = BLACK,
        save_file_dir: str = "/Users/tommyjoseph/Desktop/projects/still-manim/examples/media/",
    ):
        self.ph = pixel_height
        self.pw = pixel_height * aspect_ratio
        self.fh = frame_height
        self.fw = frame_height * aspect_ratio
        self.fc = frame_center

        self.bg_color = bg_color

        self.mobjects: List[Mobject] = []
        self.num_snapshots = 0
        self.save_file_dir = save_file_dir

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
        use_z_index=False,
    ):
        cur_mobjects = it.chain(*(m.get_family() for m in self.mobjects))

        if use_z_index:
            return sorted(cur_mobjects, key=lambda m: m.z_index)
        return cur_mobjects

    def get_to_svg_func(self, mobject: Mobject):
        to_svg_funcs = {
            VMobject: self.vmobject_to_svg_el,
            Mobject: lambda mobject: mobject,  # do nothing
        }
        for _type in to_svg_funcs:
            if isinstance(mobject, _type):
                return to_svg_funcs[_type]
        raise TypeError(f"Displaying an object of class {_type} is not supported")

    def snapshot(self, preview=False):
        mobjects_in_order = self.get_mobjects_to_display()
        svg_els: List[svg.Element] = [
            svg.Rect(width="100%", height="100%", fill=self.bg_color.value)
        ]
        for mobject in mobjects_in_order:
            svg_el = self.get_to_svg_func(mobject)(mobject)
            svg_els.append(svg_el)
        svg_view_obj = svg.SVG(
            viewBox=svg.ViewBoxSpec(0, 0, self.pw, self.ph),
            elements=svg_els,
        )
        self.save_svg(svg_view_obj, preview=preview, suffix=self.num_snapshots)

        self.num_snapshots += 1

    def vmobject_to_svg_el(self, vmobject: VMobject):
        # Note: Not convinced I need `gen_subpaths_from_points_2d`. No need for disconnected paths yet. Can potentially repr points as list of subpaths later.
        points = to_pixel_coords(
            vmobject.points, self.pw, self.ph, self.fw, self.fh, self.fc
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
        # if vmobject.consider_points_equals_2d(points[0], points[-1]):
        svg_path.append(svg.Z())
        kwargs = {}

        def orNone(value: any):
            return value if value is not None else "none"

        kwargs["stroke"] = orNone(vmobject.stroke_color.value)
        kwargs["stroke_width"] = orNone(vmobject.stroke_width)
        kwargs["stroke_opacity"] = orNone(vmobject.stroke_opacity)
        kwargs["fill_opacity"] = orNone(vmobject.fill_opacity)
        kwargs["fill"] = orNone(vmobject.fill_color.value)

        return svg.Path(d=svg_path, **kwargs)

    def save_svg(
        self,
        svg_obj: svg.SVG,
        name: str = "test",
        preview: bool = False,
        suffix: int | str = "",
    ):
        script_dir = Path(self.save_file_dir)
        fpath = script_dir / f"{name}{suffix}.svg"

        with open(fpath, "w") as file:
            file.write(str(svg_obj))
        if preview:
            subprocess.run(["open", fpath])
