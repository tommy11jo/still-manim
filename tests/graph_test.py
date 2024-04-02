from typing import Hashable, List, Tuple
from pathlib import Path
from smanim import *
from smanim.config import Config


config = Config(save_file_dir=Path(__file__).parent / "media")
canvas = Canvas(config=config)

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


def adj_list_graph_to_weighted_graph_format(graph: AdjacencyListGraph):
    vertices = list(graph.keys())
    edges = []
    for vertex, neighbors in graph.items():
        for neighbor, weight in neighbors:
            edges.append((vertex, neighbor, weight))
    return vertices, edges


def adj_list_graph_to_graph_format(graph: AdjacencyListGraph):
    vertices = list(graph.keys())
    edges = []
    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            edges.append((vertex, neighbor))
    return vertices, edges


def adj_list_graph_to_graph_format_weighted(graph: WeightedAdjacencyListGraph):
    vertices = list(graph.keys())
    edges = []
    labels = {}
    for vertex, neighbors in graph.items():
        for neighbor, weight in neighbors:
            edge = (vertex, neighbor)
            edges.append(edge)
            labels[edge] = weight
    return vertices, edges, labels


def graph(graph):
    vertices, edges = adj_list_graph_to_graph_format(graph)
    vgraph = Graph(
        vertices,
        edges,
        # labels=True,
        layout_config={"seed": 2},
        vertex_config={"radius": 0.2},
        # Can use either fill or stroke color on lines (which are the default edge type)
        # edge_config={"fill_color": BLUE},
        edge_config={"stroke_color": BLUE},
    )
    canvas.add(vgraph)
    canvas.snapshot(preview=True)


# graph(GRAPH1)


def digraph(graph):
    vertices, edges = adj_list_graph_to_graph_format(graph)
    vgraph = Graph(
        vertices,
        edges,
        labels=True,
        edge_type=Arrow,
        edge_config={
            "buff": 0,
            "tip_length": 0.15,
            "tip_width": 0.1,
        },
    )
    canvas.add(vgraph)
    canvas.snapshot(preview=True)


# digraph(GRAPH1)


def weighted_digraph(graph):
    vertices, edges, edge_labels = adj_list_graph_to_graph_format_weighted(graph)
    graph = WeightedGraph(
        vertices, edges, labels=True, edge_labels=edge_labels, edge_type=Arrow
    )
    canvas.add(graph)
    canvas.snapshot(preview=True)


# weighted_digraph(WEIGHTED_GRAPH1)
