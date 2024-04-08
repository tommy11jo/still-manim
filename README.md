# still-manim

![Still Manim Logo](./public/still-manim-logo.svg)
Inspired by 3blue1brown's [manim](https://github.com/3b1b/manim), still-manim is a python library for creating SVG diagrams of math, programming, and science concepts. The easiest way to create a diagram is through the the [web editor](TODO). You can also work locally by cloning this repo or installing the package with pip:

```
pip install still-manim
```

The web editor source code can be found [here](https://github.com/tommy11jo/still-manim-editor). Examples of programming diagrams with manim-style diagrams can be found on programcomics.com.

## Functionality

- **Polygons**: polygons, regular polygons, squares, rectangles, triangles
- **Arcs**: circles, dots
- **Lines**: line segments, arrows, vectors
- **Graphs**: directed graphs, undirected graphs, weighted graphs
- **Cartesian Graphs**: number lines, 2D cartesian graphs, functions for those graphs
- **Text**: any font size or font color but only one font right now
- **Misc**: crosses, reactive surrounding rectangles, labels

Still Manim does not support all the different types of Mobjects in manim. Also, still manim is entirely in 2D for now. More functionality will be supported if there's demand.

All constructed mobjects permit spatial relations (such as `obj1.next_to(obj2))`), transformations (such as `obj1.rotate(PI / 2)`), coloring, grouping and arrangement, and layering.

## Examples

```
from smanim import *
# creates the lemon logo svg at the top of this README
# a still life for still manim
stroke_width = 1
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
title = Text("Still Manim", font_size=H1_FONT_SIZE)
lemons.scale_to_fit_height(title.height)
title.next_to(lemons, buff=0.05)
canvas.add(lemons, title)

canvas.snapshot(preview=True, crop=True)
# use the draw function instead of snapshot in the web editor
# canvas.draw(crop=True)
```

Another goal of this project is to create mathematical and scientific objects flexibly and clearly in as little code as possible. So far, only a few types of objects have been added, including directed graphs, undirected graphs, weighted graphs, number lines, and 2D cartesian graphs.

![Sin Graph](./public/sin-graph.svg)

```
from smanim import *
n = NumberPlane.from_axes_ranges((-6, 6), (-2, 2))
parabola = n.plot(np.sin, stroke_color=BLUE)
parabola_deriv_fn = parabola.gen_derivative_fn()
parabola_deriv = n.plot(parabola_deriv_fn, stroke_color=RED)
label = Text("y = sin(x)", color=RED, font_size=30).next_to(parabola, UP)
label.shift(LEFT * 0.6)
label2 = Text("y = cos(x)", color=BLUE, font_size=30).next_to(parabola_deriv, UP)
label2.shift(RIGHT * 2)
canvas.add(n, label, label2)
canvas.snapshot(preview=True)
# use the draw function instead of snapshot in the web editor
# canvas.draw()
```

## Notes

- The best documentation right now is the source code and the examples. The examples can be found in `examples/` and `tests/` in this repo.
- The API exposed to users for this project is loosely based on the Manim Community's [variant of manim](https://github.com/ManimCommunity/manim/).
