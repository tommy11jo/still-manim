from smanim import *

# Demos for bidirectional functionality


def demo1():
    s = Square()
    canvas.add(s)
    canvas.snapshot(preview=True)
    print(mobject_registry)
    print(s.get_path())


# demo1()


def demo2():
    a = Arrow()
    canvas.add(a)
    canvas.snapshot(preview=True)
    print(mobject_registry)
    print(a.get_path())
    print(a.end_tip.get_path())


# demo2()


# g = Group(s, Circle())
# Note: this is unsupported. Multiple mobjects must be instantiated on separate lines.


def demo3():
    s = Square()
    c = Circle()
    b = BoxList(s, c)
    canvas.add(b)
    canvas.snapshot(preview=True)
    print(mobject_registry)
    print(b.get_path())
    vlines = b[3]
    print(vlines[0].get_path())  # the first vline


# demo3()


def demo4():
    g = Graph(vertices=range(4), edges=[(0, 1), (0, 2), (0, 3), (1, 3)])
    start = g.vertices[0]
    # Note that this currently doesn't change the subpath and parent, even though it ideally would
    # If the user selects the 0th vertex, the LLM will receive the info that the vertex can be accessed at `g.vertices[0]`
    # Would have to use settrace
    start.set_color(RED)
    canvas.add(g)
    canvas.snapshot(preview=True)
    print(mobject_registry)
    print(g.get_path())

    print(g.vertices[0].get_path())


# demo4()


def demo5():
    g = Group(*[Square() for _ in range(3)]).arrange()
    # Solution will probably be using settrace and capturing line events
    # Aggregating all possible updates via __inits__ called on the current line
    # Committing the last update (in the example above: Group, but not the Squares)
    # settrace can be setup to work in the global frame
    # https://stackoverflow.com/questions/55998616/how-to-trace-code-run-in-global-scope-using-sys-settrace
    canvas.add(g)
    canvas.snapshot(preview=True)
    print(g[0].get_path())


# demo5()


def _gen_circle():
    c = Circle()
    return c


# Another example of why current approach doesn't work
def demo6():
    c1 = _gen_circle().shift(RIGHT * 2)
    c2 = _gen_circle()
    canvas.add(c1, c2)
    canvas.snapshot(preview=True)
    print(c1.get_path())
    print(mobject_registry)


demo6()
# TODO: Test insert_at_front resetting of subpaths and parents by doing a bring to front
