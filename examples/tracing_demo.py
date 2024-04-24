from smanim import *

# Demos for bidirectional functionality

# must actually call setup birdirectional for now
setup_bidirectional(__file__)


def demo1():
    s = Square()
    canvas.add(s)
    canvas.snapshot(preview=True)
    print(s.get_path())


# demo1()


def demo2():
    a = Arrow()
    canvas.add(a)
    canvas.snapshot(preview=True)
    print(a.get_path())
    print(a.end_tip.get_path())


# demo2()


def demo3():
    s = Square()
    c = Circle()
    b = BoxList(s, c)
    canvas.add(b)
    canvas.snapshot(preview=True)
    print(b.get_path())
    vlines = b[3]
    print(vlines[0].get_path())  # the first vline


# demo3()


def complex_assign():
    g = Group(*[Square() for _ in range(3)]).arrange()
    s = Square()
    canvas.add(g)
    canvas.snapshot(preview=True)
    print(g[0].get_path())
    print(s.get_path())


# complex_assign()


def _gen_circle():
    c = Circle()
    return c


# Another example of why current approach doesn't work
def assign_in_separate_fn():
    c1 = _gen_circle().shift(RIGHT * 2)
    c2 = _gen_circle()
    canvas.add(c1, c2)
    canvas.snapshot(preview=True)
    print(c1.get_path())


# assign_in_separate_fn()
# TODO: Test insert_at_front resetting of subpaths and parents by doing a bring to front


def graph_demo():
    g = Graph(vertices=range(4), edges=[(0, 1), (0, 2), (0, 3), (1, 3)])
    # this actually triggers an update to the subpath
    start_vertex = g.vertices[0]
    start_vertex.set_color(RED)
    canvas.add(g)
    canvas.snapshot(preview=True)
    assert g.vertices[0].get_path() == "start_vertex"
    assert g.vertices[1].get_path() == "g.vertices[1]"


graph_demo()


# direct adds should be avoided when possible
# the reference is stored as canvas.mobjects[k], which the LLM can access but is less clear than a var reference
def direct_add():
    canvas.add(Circle())
    canvas.snapshot(preview=True)
    print(canvas.mobjects[0].get_path())


# direct_add()
# TODO: testing adding an edge between nodes with an LLM using the reference technique above

# TODO: Potential method is drawing all points and bboxes now and only showing them when user clicks
# TODO: hover events example https://developer.mozilla.org/en-US/docs/Web/SVG/Element/a
