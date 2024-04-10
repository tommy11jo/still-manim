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
    canvas.snapshot(preview=True)


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
    )
    vgraph.add_vertex_labels()
    canvas.add(vgraph)
    canvas.snapshot(preview=True)


# digraph(GRAPH1)


def weighted_digraph(graph):
    vertices, edges, edge_labels = WeightedGraph.from_adjacency_list(graph)
    graph = WeightedGraph(
        vertices,
        edges,
        vertex_config={"fill_color": GRAY},
        edge_labels=edge_labels,
        edge_type=Arrow,
        layout_config={"seed": 2},
    )
    graph.add_vertex_labels()
    canvas.add(graph)
    canvas.snapshot(preview=True)


# weighted_digraph(WEIGHTED_GRAPH1)
