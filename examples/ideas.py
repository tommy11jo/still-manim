from pathlib import Path
from smanim import *

CONFIG.save_file_dir = Path(__file__).parent / "media"
canvas = Canvas(CONFIG)


# https://arxiv.org/pdf/2307.00146.pdf
# Let's compare diagrams with their example
# I like how they showed Playfairs drawing. That's a good iconic example to do later if I add plotting.
# A pro of their tool is that its in js/ts so it's easier to add interaction with js handlers.
# A con of their tool is JSX syntax and (I think) being stuck in a "tree-structured" hierarchy.
# What is the underlying output? HTML/CSS? SVG?
def draw_planets():
    mercury_diam = 4879
    venus_diam = 12104
    earth_diam = 12756
    mars_diam = 6794

    earth_width_units = 2
    mercury_width, venus_width, earth_width, mars_width = (
        np.array([mercury_diam, venus_diam, earth_diam, mars_diam])
        / earth_diam
        * earth_width_units
        / 2
    )
    mercury = Circle(fill_color=GOLD_A, radius=mercury_width).shift(LEFT * 2)
    mercury.add_label(Text("Mercury"))
    mercury.add_surrounding_rect(stroke_color=GREY)
    venus = Circle(fill_color=LIGHT_BROWN, radius=venus_width)
    earth = Circle(fill_color=BLUE, radius=earth_width)
    mars = Circle(fill_color=RED, radius=mars_width)
    planets = Group(mercury, venus, earth, mars)
    planets.arrange(aligned_edge=UP)
    canvas.add(planets)
    canvas.snapshot(preview=True)


draw_planets()
