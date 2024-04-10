# still-manim

![Still Manim Logo](./public/still-manim-logo.svg)
still-manim is a python library for creating diagrams programatically with a higher-level language based on 3blue1brown's [manim](https://github.com/3b1b/manim). Like manim, the focus is on visuals for math, programming, and science concepts. Unlike manim, still-manim can run in the browser, enables creating SVGs with shapes and text combined, and is designed to create still (not animated) pictures. Try it in the [web editor](https://still-manim-editor.vercel.app/) or install it using pip from testpypi:

```
pip install -i https://test.pypi.org/simple/ still-manim
```

The web editor source code can be found [here](https://github.com/tommy11jo/still-manim-editor). Some examples of programming diagrams with manim-style diagrams can be found on [programcomics.com](https://programcomics.com).

## Examples

```
# this code creates the logo SVG at the top of this README
# a still life for still-manim
from smanim import *
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

One goal of this project is to create mathematical and scientific objects flexibly and clearly in as little code as possible. So far, only a few types of domain-specific objects have been added: directed graphs, undirected graphs, weighted graphs, number lines, and 2D cartesian graphs.

![Sin Graph](./public/sin-graph.svg)

```
from smanim import *
n = NumberPlane.from_axes_ranges((-6, 6), (-2, 2), axis_config={"include_arrow_tips": False})
sin_graph_obj = n.plot(np.sin, color=RED)
derivative_fn = sin_graph_obj.gen_derivative_fn()
cos_graph_obj = n.plot(derivative_fn, color=BLUE)
sin_label = Text("y = sin(x)", color=RED, font_size=30).next_to(sin_graph_obj, UP)
sin_label.shift(RIGHT * 2)
cos_label = Text("y = cos(x)", color=BLUE, font_size=30).next_to(cos_graph_obj, UP)
cos_label.shift(LEFT * 0.6)
canvas.add(n, sin_label, cos_label)
canvas.snapshot(preview=True)
```

## Functionality

- **Polygons**: polygons, regular polygons, squares, rectangles, triangles
- **Arcs**: circles, dots
- **Lines**: line segments, arrows, vectors
- **Graphs**: directed graphs, undirected graphs, weighted graphs
- **Cartesian Graphs**: number lines, 2D cartesian graphs, functions for those graphs
- **Text**: any font size or font color but only one font right now
- **Misc**: crosses, reactive surrounding rectangles, labels

still-manim does not support all the different types of Mobjects in manim. Also, still-manim is entirely in 2D for now.

All constructed mobjects permit spatial relations (such as `obj1.next_to(obj2))`), transformations (such as `obj1.rotate(PI / 2)`), coloring, grouping and arrangement, and layering.

## Notes

- The best documentation right now is the source code and the examples. The examples can be found in `examples/` and `tests/` in this repo.
- The API exposed to users for this project is loosely based on the Manim Community's [variant of manim](https://github.com/ManimCommunity/manim/).
