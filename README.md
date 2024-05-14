# still-manim

![Still Manim Logo](./public/still-manim-logo.svg)
still-manim is a python library for drawing static graphics of conceptual content in domains like math and programming.
It's based on 3blue1brown's animation library, [manim](https://github.com/3b1b/manim), except it is designed for static graphics and for running in the browser.
Try it in the [web editor](idraw.chat) (source code [here](https://github.com/tommy11jo/still-manim-editor)).

## Examples

Example 1:

```
# this code creates the logo SVG at the top of this README
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
    line = Line(ORIGIN, c.point_from_proportion(prop / 8))
    spikes.add(line)
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

canvas.draw(crop=True)
# use canvas.snapshot(preview=True) instead of canvas.draw() if you are running locally
```

Example 2:
![Graph Demo](./public/graph-demo.svg)

```

from smanim import *
canvas.set_dimensions(6, 6)
WEIGHTED_GRAPH1 = {
    0: [(1, 2), (2, 1)],
    1: [(2, 5), (3, 11), (4, 3)],
    2: [(5, 15)],
    3: [(4, 2)],
    4: [(2, 1), (5, 4), (6, 5)],
    5: [],
    6: [(3, 1), (5, 1)],
}
vertices, edges, edge_labels = WeightedGraph.from_adjacency_list(WEIGHTED_GRAPH1)
graph = WeightedGraph(
        vertices,
        edges,
        vertex_config={"fill_color": GRAY, "radius": 0.2},
        edge_labels=edge_labels,
        edge_type=Arrow,
        layout_config={"seed": 2},
        include_vertex_labels=True,
    )
start_vertex = graph.vertices[0]
start_vertex.set_color(RED)
pointer = Arrow.points_at(start_vertex, direction=LEFT, color=RED, length=0.5)
start_text = Text("start", color=RED).next_to(pointer)
canvas.add(graph, pointer, start_text)
canvas.draw()
# use canvas.snapshot(preview=True) instead of canvas.draw() if you are running locally
```

## Goals

- Run in the browser
- Allow flexible and clear construction of domain-specific graphical objects in as little python code as possible
- Present language constructs to an LLM tutor, understanding that an LLM might not have great spatial awareness
- Provide sensible support for human-AI interaction while editing diagrams (for example, by tracking the line of code for each variable assignment to a mobject and storing that in the mobject element in the SVG.)

## Supported Mobject Types

- **Polygons**: polygons, regular polygons, squares, rectangles, triangles
- **Arcs**: circles, dots
- **Lines**: line segments, arrows, vectors
- **Graphs**: directed graphs, undirected graphs, weighted graphs
- **Cartesian Graphs**: number lines, 2D cartesian graphs, functions for those graphs (Note: The API is very unstable here)
- **Text**: font size, font color, etc.

still-manim does not support all the different types of Mobjects in manim. Also, still-manim is entirely in 2D for now.

All constructed mobjects permit:

- **spatial relations**: e.g., `obj1.next_to(obj2))`
- **spatial transformations**: e.g., `obj1.rotate(PI / 2)`
- **styling**: e.g., `c = Circle(stroke_color=RED)`
- **grouping**: e.g., `g = Group(Circle(), Rectangle().shift(RIGHT * 2))`
- **layering**: e.g., `circle.set_z_index(10)`
- **various compositions of mobjects**: e.g. `a = Arrow.points_at(circle)` or `circle.add_label(Text("A Circle"))`

## Development

### Pip

```
pip install still-manim
```

### Cloning

1. Clone this repo

```
git clone https://github.com/tommy11jo/still-manim.git
```

2. Install the deps the first time you open this repo.

```
poetry install
```

3. Init the python env each time you open this repo.

```
poetry shell
```

5. Run your first still-manim program by navigating to the `examples` folder and running:

```
python3 hello-world.py
```

## Notes

- Documentation coming soon (maybe).
- Some examples can be found in `examples/` and `tests/` in this repo. More examples can be found in the [web editor](idraw.chat) .
- The API exposed to users for this project is loosely based on the Manim Community's [variant of manim](https://github.com/ManimCommunity/manim/).
