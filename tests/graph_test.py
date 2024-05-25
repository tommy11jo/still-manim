import sys
from typing import Hashable, List, Tuple
from pathlib import Path
from smanim import *


CONFIG.save_file_dir = Path(__file__).parent / "media"

AdjacencyListGraph = dict[Hashable, List[Tuple[Hashable, Hashable]]]
WeightedAdjacencyListGraph = dict[Hashable, List[Tuple[Hashable, Hashable, Hashable]]]


SIMPLE_GRAPH = {0: [(1, 2)], 1: []}
GRAPH1 = {
    0: [1, 2],
    1: [2, 3, 4],
    2: [5],
    3: [4],
    4: [2, 5, 6],
    5: [],
    6: [3, 5],
}
WEIGHTED_GRAPH1 = {
    0: [(1, 2), (2, 1)],
    1: [(2, 5), (3, 11), (4, 3)],
    2: [(5, 15)],
    3: [(4, 2)],
    4: [(2, 1), (5, 4), (6, 5)],
    5: [],
    6: [(3, 1), (5, 1)],
}
START1, END1 = 0, 6

TREE1 = {0: [1, 2], 1: [3, 4], 2: [6, 7], 3: [5], 4: [], 5: [], 6: [], 7: []}


def graph(graph):
    vertices, edges = Graph.from_adjacency_list(graph)
    vgraph = Graph(
        vertices,
        edges,
        layout_config={"seed": 2},
        vertex_config={"radius": 0.2, "fill_color": WHITE},
        edge_config={"color": BLUE},
    )
    canvas.add(vgraph)
    canvas.snapshot()


# graph(GRAPH1)


def digraph(graph):
    vertices, edges = Graph.from_adjacency_list(graph)
    vgraph = Graph(
        vertices,
        edges,
        layout_scale=3,
        edge_type=Arrow,
        edge_config={
            "buff": 0,
            "tip_length": 0.15,
            "tip_width": 0.1,
        },
        include_vertex_labels=True,
    )
    canvas.add(vgraph)
    canvas.snapshot()


# digraph(GRAPH1)


# Demos for bidirectional functionality
sys._getframe().f_trace = global_trace_assignments
sys.settrace(trace_assignments)


def weighted_digraph(graph):
    vertices, edges, edge_labels = WeightedGraph.from_adjacency_list(graph)
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
    canvas.snapshot()
    print(graph.get_path())
    print(graph.edge_labels[(0, 1)].get_path())
    print(graph.vertex_labels[0].get_path())


# weighted_digraph(WEIGHTED_GRAPH1)


def tree(graph):
    vertices, edges = Graph.from_adjacency_list(graph)
    graph = Graph(
        vertices, edges, layout="tree", root_vertex=0, include_vertex_labels=True
    )
    canvas.add(graph)
    # canvas.snapshot()
    result = canvas.draw()
    print(graph.get_path())
    print(graph.edges[(0, 1)].get_path())
    print(graph.vertex_labels[2].get_path())
    # print(result)


# tree(TREE1)
