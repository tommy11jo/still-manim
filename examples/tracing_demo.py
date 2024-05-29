import argparse
import sys
import traceback
from smanim import *
from smanim.mobject.transformable import TransformableMobject


sys._getframe().f_trace = global_trace_assignments
sys.settrace(trace_assignments)
canvas = Canvas(CONFIG)

manual_suffix = "0"


def next_manual_suffix():
    global manual_suffix
    cur = int(manual_suffix)
    manual_suffix = str(cur + 1)
    return manual_suffix


def test_simple_assign():
    s = Square()
    canvas.add(s)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        s.get_access_path()[0] == "s"
    ), f"Got: {s.get_access_path()[0]}, Expected: 's'"
    # assert s.get_access_path()[1] == 18, f"Got: {s.get_access_path()[1]}, Expected: 18"


def test_nested_mobject_assign():
    a = Arrow()
    canvas.add(a)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        a.get_access_path()[0] == "a"
    ), f"Got: {a.get_access_path()[0]}, Expected: 'a'"
    assert (
        a.end_tip.get_access_path()[0] == "a.end_tip"
    ), f"Got: {a.end_tip.get_access_path()[0]}, Expected: 'a.end_tip'"


def test_complex_assign():
    canvas = Canvas(CONFIG)
    g = Group(*[Square() for _ in range(3)]).arrange()
    s2 = g[1].set_color(RED)
    canvas.add(g, s2)
    canvas.snapshot(manual_suffix=next_manual_suffix())

    assert (
        g[0].get_access_path()[0] == "g[0]"
    ), f"Got: {g[0].get_access_path()[0]}, Expected: 'g[0]'"
    assert (
        g[1].get_access_path()[0] == "s2"
    ), f"Got: {g[1].get_access_path()[0]}, Expected: 's2'"


def test_graph_demo():
    canvas = Canvas(CONFIG)
    g = Graph(
        vertices=range(4),
        edges=[(0, 1), (0, 2), (0, 3), (1, 3)],
        include_vertex_labels=True,
    )
    start_vertex = g.vertices[0]
    start_vertex.set_color(RED)
    canvas.add(g)
    canvas.snapshot(manual_suffix=next_manual_suffix())

    assert (
        g.vertices[0].get_access_path()[0] == "start_vertex"
    ), f"Got: {g.vertices[0].get_access_path()[0]}, Expected: 'start_vertex'"
    assert (
        g.vertices[1].get_access_path()[0] == "g.vertices[1]"
    ), f"Got: {g.vertices[1].get_access_path()[0]}, Expected: 'g.vertices[1]'"


def test_direct_add():
    canvas = Canvas(CONFIG)
    canvas.add(Circle())
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        canvas.mobjects[0].get_access_path()[0] == "canvas.mobjects[0]"
    ), f"Got: {canvas.mobjects[0].get_access_path()[0]}, Expected: 'canvas.mobjects[0]'"


def more_circle():
    c2 = Circle().shift(RIGHT * 2)
    canvas.add(c2)
    return c2


def test_inner_function_call():
    canvas = Canvas(CONFIG)
    more_circle()
    c = Circle()
    canvas.add(c)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        c.get_access_path()[0] == "c"
    ), f"Got: {c.get_access_path()[0]}, Expected: 'c'"


def test_class_demo():
    canvas = Canvas(CONFIG)

    class CircleShell(TransformableMobject):
        def __init__(self):
            super().__init__()
            inner_circle = Circle()
            self.add(inner_circle)

    d = CircleShell()
    assert len(d[0].access_paths) == 2, f"Got: {len(d[0].access_paths)}, Expected: 2"
    canvas.add(d)
    canvas.snapshot(manual_suffix=next_manual_suffix())


def test_repeated_assign():
    canvas = Canvas(CONFIG)

    def generate_circle():
        circle = Circle()
        return circle

    a = generate_circle().shift(LEFT)
    b = generate_circle()
    canvas.add(a, b)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        a.get_access_path()[0] == "circle"
    ), f"Got: {a.get_access_path()[0]}, Expected: 'circle'"
    assert (
        b.get_access_path()[0] == "circle"
    ), f"Got: {b.get_access_path()[0]}, Expected: 'circle'"


def test_tree():
    canvas = Canvas(CONFIG)
    graph = Graph(
        vertices=[0, 1, 2, 3, 4],
        edges=[(0, 1), (0, 2), (2, 3), (2, 4)],
        include_vertex_labels=True,
        layout="tree",
        root_vertex=0,
    )
    start = graph.vertices[0].set_color(RED)
    canvas.add(graph, start)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        graph.vertices[2].get_access_path()[0] == "graph.vertices[2]"
    ), f"Got: {graph.vertices[2].get_access_path()[0]}, Expected: 'graph.vertices[2]'"
    assert (
        graph.edges[(0, 2)].get_access_path()[0] == "graph.edges[(0, 2)]"
    ), f"Got: {graph.edges[(0, 2)].get_access_path()[0]}, Expected: 'graph.edges[(0, 2)]'"
    assert (
        graph.vertices[0].get_access_path()[0] == "start"
    ), f"Got: {graph.vertices[0].get_access_path()[0]}, Expected: 'start'"
    assert (
        graph.vertex_labels[1].get_access_path()[0] == "graph.vertex_labels[1]"
    ), f"Got: {graph.vertex_labels[1].get_access_path()[0]}, Expected: 'graph.vertex_labels[1]'"


def test_weighted_graph():
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
    canvas.add(graph)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        graph.edge_labels[(0, 1)].get_access_path()[0] == "graph.edge_labels[(0, 1)]"
    ), f"Got: {graph.edge_labels[(0, 1)]}, Expected: 'graph.edge_labels[(0, 1)]'"
    assert (
        graph.vertex_labels[1].get_access_path()[0] == "graph.vertex_labels[1]"
    ), f"Got: {graph.vertex_labels[1]}, Expected: 'graph.vertex_labels[1]'"


def test_grid_2d():
    canvas = Canvas(CONFIG)
    canvas.set_dimensions(width=16, height=16)
    squares = [Square(stroke_color=GRAY) for _ in range(16)]
    group = Group(*squares)
    group.arrange_in_grid(num_rows=4, num_cols=4, buff=0.5)
    canvas.add(group)
    arrow = Arrow(start=squares[0], end=squares[1], color=GRAY)
    canvas.add(arrow)
    arrow2 = Arrow(start=squares[1], end=squares[2], color=GRAY)
    canvas.add(arrow2)
    canvas.snapshot(manual_suffix=next_manual_suffix())
    assert (
        squares[0].get_access_path()[0] == "group[0]"
    ), f"Got: {squares[0].get_access_path()[0]}, Expected: 'group[0]'"


def main():
    # unittest does not work cleanly with sys.set_trace on individual unittests so I had to do this manually
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-function",
        choices=[
            "all",
            "simple_assign",
            "nested_mobject_assign",
            "complex_assign",
            "graph_demo",
            "direct_add",
            "inner_function_call",
            "class_demo",
            "repeated_assign",
            "grid_2d",
            "tree",
            "weighted_graph",
        ],
        required=True,
        help="Choose which test function to run",
    )
    args = parser.parse_args()

    test_functions = {
        "simple_assign": test_simple_assign,
        "nested_mobject_assign": test_nested_mobject_assign,
        "complex_assign": test_complex_assign,
        "graph_demo": test_graph_demo,
        "direct_add": test_direct_add,
        "inner_function_call": test_inner_function_call,
        "class_demo": test_class_demo,
        "repeated_assign": test_repeated_assign,
        "grid_2d": test_grid_2d,
        "tree": test_tree,
        "weighted_graph": test_weighted_graph,
    }

    if args.test_function == "all":
        for name, func in test_functions.items():
            try:
                print(f"Running {name}...")
                func()
            except AssertionError as e:
                tb = traceback.format_exc()
                print(f"*** Failed on {name}: {e}\nTraceback:\n{tb}")
            except Exception as e:
                tb = traceback.format_exc()
                print(
                    f"*** An unexpected error occurred in {name}: {e}\nTraceback:\n{tb}"
                )
    else:
        name = args.test_function
        test_function = test_functions[name]
        try:
            print(f"Running {name}...")
            test_function()
        except AssertionError as e:
            tb = traceback.format_exc()
            print(f"*** Failed on {name}: {e}\nTraceback:\n{tb}")
        except Exception as e:
            tb = traceback.format_exc()
            print(f"*** An unexpected error occurred in {name}: {e}\nTraceback:\n{tb}")


if __name__ == "__main__":
    main()
