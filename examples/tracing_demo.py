import sys
from smanim import *

# Demos for bidirectional functionality
sys._getframe().f_trace = global_trace_assignments
sys.settrace(trace_assignments)


def simple_assign():
    s = Square()
    canvas.add(s)
    canvas.snapshot()
    print(s.get_path())


# simple_assign()


# trace only captures var assignment in this file, so does not capture the arrow components line and triangle
def nested_mobject_assign():
    a = Arrow()
    canvas.add(a)
    canvas.snapshot()
    print(a.get_path())
    print(a.end_tip.get_path())


# nested_mobject_assign()


# demonstrates multi_mobject
# demonstrates reference to mobject created in another file
def multi_mobject_assign():
    s = Square()
    c = Circle()
    b = BoxList(s, c)
    canvas.add(b)
    canvas.snapshot()
    print(b.get_path())
    vlines = b[3]
    print(vlines[0].get_path())  # the first vline


# multi_mobject_assign()


def complex_assign():
    g = Group(*[Square() for _ in range(3)]).arrange()
    s = Square()
    canvas.add(g)
    canvas.snapshot()
    print(g[0].get_path())
    print(s.get_path())


# complex_assign()


def graph_demo():
    g = Graph(vertices=range(4), edges=[(0, 1), (0, 2), (0, 3), (1, 3)])
    # this actually triggers an update to the subpath
    start_vertex = g.vertices[0]
    start_vertex.set_color(RED)
    canvas.add(g)
    canvas.snapshot()
    assert g.vertices[0].get_path() == "start_vertex"
    assert g.vertices[1].get_path() == "g.vertices[1]"


graph_demo()


# direct adds should be avoided when possible
# the reference is stored as canvas.mobjects[k], which the LLM can access but is less clear than a var reference
def direct_add():
    canvas.add(Circle())
    canvas.snapshot()
    print(canvas.mobjects[0].get_path())


# direct_add()


def more_circle():
    c2 = Circle().shift(RIGHT * 2)
    canvas.add(c2)
    print("c2 subpath is", c2.subpath)


def inner_function_call():
    more_circle()
    c = Circle()
    canvas.add(c)
    canvas.snapshot()
    print("c path is", c.get_path())


# inner_function_call()


class CircleShell(Mobject):
    def __init__(self):
        super().__init__()
        inner_circle = Circle()
        self.add(inner_circle)

    # TODO: this should not be abstract, just make them do nothing by default
    def rotate(self):
        pass

    def scale(self):
        pass

    def shift(self):
        pass

    def stretch(self):
        pass


def class_demo():
    d = CircleShell()
    canvas.add(d)
    canvas.snapshot()


# class_demo()

# global assigns are why the sys._getframe().f_trace assignment is needed
# https://stackoverflow.com/questions/55998616/how-to-trace-code-run-in-global-scope-using-sys-settrace
# global mobject assign
# a = Square()


def generate_circle():
    circle = Circle()
    return circle


# assigns a name to the same mobject instance twice
def repeated_assign():
    a = generate_circle().shift(LEFT)
    b = generate_circle()
    c = generate_circle().shift(RIGHT)
    canvas.add(a, b, c)
    canvas.snapshot()


# repeated_assign()
def test():
    n = NumberPlane.from_axes_ranges(
        (-6, 6), (-2, 2), axis_config={"include_arrow_tips": False}
    )
    sin_graph_obj = n.plot(np.sin, color=RED)

    canvas.add(n)
    canvas.draw()


# test()

# TODO: testing adding an edge between nodes with an LLM using the reference technique above
# I'm worried the LLM will overindex on the user selected vertices g.vertices[0] and g.vertices[1] and try to draw a line between them rather than just changing edges in the constructor
# TODO: Test insert_at_front resetting of subpaths and parents by doing a bring to front


# Future: Current approach to assignment is not perfect. If an object reference is assigned a name multiple times, only the last time is captured.
# I could use "access points" and let the LLM decide where to access
# The LLM should be able to infer this though.
