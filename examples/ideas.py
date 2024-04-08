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


# draw_planets()


def generate_lemons(stroke_width=4):
    lemon = VGroup()
    c = Circle(fill_color=YELLOW_D, stroke_color=WHITE, stroke_width=stroke_width)
    c.stretch(1.4, dim=0).rotate(PI / 8)
    arc = Arc(
        angle=-PI, fill_color=YELLOW_E, stroke_color=WHITE, stroke_width=stroke_width
    )
    arc.stretch(2, dim=1)
    arc.stretch(1.4, dim=0).rotate(PI / 8)
    lemon.add(c, arc)
    lemon.bring_to_front(c)

    spikes = VGroup()
    for prop in range(8):
        vector = Vector(c.point_from_proportion(prop / 8))
        spikes.add(vector)
    lemon.add(spikes)

    other_lemon: VGroup = lemon.copy()
    other_lemon.scale(0.8).shift(RIGHT * 0.5).rotate(-PI / 4)
    lemon.shift(LEFT * 0.5)
    other_lemon.shift(RIGHT * 0.8)
    other_lemon.set_z_index(-10)

    lemons = VGroup(lemon, other_lemon)
    return lemons


# a still life for still manim
def lemon_logo():
    lemons: VGroup = generate_lemons(stroke_width=1)
    # lemons.scale(0.2)

    title = Text("Still Manim", font_size=H1_FONT_SIZE)

    lemons.scale_to_fit_height(title.height)
    title.next_to(lemons, buff=0.05)
    canvas.add(lemons, title)

    canvas.snapshot(preview=True, crop=True)
    # canvas.draw()


lemon_logo()
