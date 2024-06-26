"""Mobjects used to represent mathematical graphs (think graph theory, not plotting)."""

from __future__ import annotations

from smanim.config import CONFIG
from smanim.mobject.geometry.circle import Dot
from smanim.mobject.geometry.shape_matchers import SurroundingRectangle
from smanim.mobject.text.text_mobject import Text
from smanim.mobject.transformable import TransformableMobject
from smanim.typing import AdjacencyListGraph, WeightedAdjacencyListGraph
from smanim.utils.color import GRAY

__all__ = ["Graph", "WeightedGraph"]

from copy import copy
from typing import Dict, Hashable, Iterable, List, Tuple

import networkx as nx
import numpy as np

from smanim.mobject.geometry.line import Arrow, Line
from smanim.mobject.group import Group
from smanim.mobject.mobject import Mobject


class Graph(TransformableMobject):
    """Supports directed and undirected graphs with unweighted edges.
    Layout constructed using underlying networkx library, which can be configured using:
    - `layout`: str that can be set to "circular", "kamada_kawai", "planar", "random", "shell", "spectral", "partite", "tree", "spiral", "spring"
    - `layout_config`: dict that can take in typical constructing params for networkx graphs, like setting "seed" to value 1
    """

    def __init__(
        self,
        vertices: list[Hashable] | None = None,
        edges: list[tuple[Hashable, Hashable]] | None = None,
        layout: str | dict = "spring",
        layout_scale: (
            float | tuple
        ) = 2,  # scale the layout determined by networkx by this factor, "spread out the vertices"
        layout_config: dict | None = None,
        vertex_type: type[Mobject] = Dot,
        vertex_config: dict = {},  # params to pass into constructor of `vertex_type` class
        edge_type: type[Mobject] = Line,
        edge_config: dict = {},  # params to pass into constructor of `edge_type` class
        include_vertex_labels: bool = False,
        vertex_label_config: dict = {},
        partitions: list[list[Hashable]] | None = None,
        root_vertex: Hashable | None = None,
        **kwargs,
    ) -> None:
        if not issubclass(edge_type, Line):
            raise ValueError("edge_type must be `Line` or inherit from `Line`")

        super().__init__(**kwargs)
        if vertices is None and edges is None:
            vertices = [0, 1, 2]
            edges = [(0, 1), (1, 2), (2, 0)]

        nx_graph = Graph._empty_networkx_graph()
        nx_graph.add_nodes_from(vertices)
        nx_graph.add_edges_from(edges)

        _layout = _determine_graph_layout(
            nx_graph,
            layout=layout,
            layout_scale=layout_scale,
            layout_config=layout_config,
            partitions=partitions,
            root_vertex=root_vertex,
        )

        if vertex_type is Dot:
            if len(vertex_config) == 0:
                _vertex_config = {"fill_color": GRAY, "radius": 0.2}
            else:
                _vertex_config = {}
        else:
            _vertex_config = {}
        _vertex_config.update(vertex_config)
        self.vertices = {
            v: vertex_type(**_vertex_config, parent=self, subpath=f".vertices[{v}]")
            for v in vertices
        }

        for vid, vertex in self.vertices.items():
            vertex.move_to(_layout[vid])
        self.add(*self.vertices.values())

        if edge_type is Line:
            _edge_config = {
                "buff": 0.0,
                "stroke_width": 2.0,
            }
        elif edge_type is Arrow:
            _edge_config = {
                "buff": 0.0,
                "tip_length": 0.1,
                "tip_width": 0.1,
                "stroke_width": 2.0,
            }
        else:
            _edge_config = {}

        _edge_config.update(edge_config)

        self.edges = {
            (u, v): edge_type(
                start=self.vertices[u],
                end=self.vertices[v],
                parent=self,
                subpath=f".edges[{(u, v)}]",
                **_edge_config,
            )
            for u, v in edges
        }
        self.add(*self.edges.values())

        self.vertex_labels: Group | None
        if include_vertex_labels:
            self.vertex_labels = Group(subpath=".vertex_labels", parent=self)
            self.populate_vertex_labels(self.vertex_labels, **vertex_label_config)
            self.add(*self.vertex_labels)
        else:
            self.vertex_labels = None

    @staticmethod
    def _empty_networkx_graph() -> nx.Graph:
        return nx.Graph()

    def __repr__(self):
        classname = self.__class__.__qualname__
        return (
            f"{classname}(vertices={self.vertices.keys()}, edges={self.edges.keys()})"
        )

    @staticmethod
    def from_adjacency_list(
        graph: AdjacencyListGraph,
    ) -> Tuple[List[Hashable], List[Tuple[Hashable, Hashable]]]:
        # graph is a map from vertex => [vertex1, vertex2, ...]
        vertices = list(graph.keys())
        edges = []
        for vertex, neighbors in graph.items():
            for neighbor in neighbors:
                edges.append((vertex, neighbor))
        return vertices, edges

    def populate_vertex_labels(
        self,
        vertex_labels: Group,
        labels: Iterable[str] | None = None,
        label_config: dict = {},
    ) -> None:
        if labels is None:
            labels = [str(i) for i in range(len(self.vertices))]
        for vertex, label in zip(self.vertices.values(), labels):
            text = Text(label, **label_config)
            text.move_to(vertex)
            vertex_labels.add(text)


class WeightedGraph(Graph):
    def __init__(
        self,
        *args,
        edge_labels: (
            Dict[Tuple[Hashable, Hashable], Text | str | int] | None
        ) = None,  # labels maps from edge tuple (u, v) => Text
        edge_label_config: dict = {},  # kwargs for `Text` edge label
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        if edge_labels is None:
            raise Exception(
                "Weighted graphs must include a `labels` arg. If you don't want labels, use `Graph`"
            )
        converted_labels: Dict[Tuple[Hashable, Hashable], Text] = {}
        for edge, label in edge_labels.items():
            if not isinstance(label, Text):
                converted_labels[edge] = Text(
                    str(label),
                    subpath=f".edge_labels[{edge}]",
                    parent=self,
                    **edge_label_config,
                )
            else:
                converted_labels[edge] = label
        edge_label_map: dict[Tuple[Hashable, Hashable], Text] = {}
        for edge, weight_text in converted_labels.items():
            v1, v2 = edge
            edge_obj = self.edges[(v1, v2)]

            weight_text.move_to(edge_obj.midpoint)
            weight_text.add(
                SurroundingRectangle(
                    weight_text,
                    fill_color=CONFIG.bg_color,
                    fill_opacity=1.0,
                    buff=0.005,
                )
            )
            edge_label_map[edge] = weight_text
        self.add(*edge_label_map.values())
        self.edge_labels = edge_label_map

    @staticmethod
    def from_adjacency_list(
        graph: WeightedAdjacencyListGraph,
    ) -> Tuple[
        List[Hashable],
        List[Tuple[Hashable, Hashable]],
        Dict[Tuple[Hashable, Hashable], Hashable],
    ]:
        # graph is a map from vertex => [(vertex1, weight1), (vertex2, weight2), ...]
        vertices = list(graph.keys())
        edges = []
        labels = {}
        for vertex, neighbors in graph.items():
            for neighbor, weight in neighbors:
                edge = (vertex, neighbor)
                edges.append(edge)
                labels[edge] = weight
        return vertices, edges, labels


def _determine_graph_layout(
    nx_graph: nx.classes.graph.Graph | nx.classes.digraph.DiGraph,
    layout: str | dict = "spring",
    layout_scale: float = 2,
    layout_config: dict | None = None,
    partitions: list[list[Hashable]] | None = None,
    root_vertex: Hashable | None = None,
) -> dict:
    automatic_layouts = {
        "circular": nx.layout.circular_layout,
        "kamada_kawai": nx.layout.kamada_kawai_layout,
        "planar": nx.layout.planar_layout,
        "random": nx.layout.random_layout,
        "shell": nx.layout.shell_layout,
        "spectral": nx.layout.spectral_layout,
        "partite": nx.layout.multipartite_layout,
        "tree": _tree_layout,
        "spiral": nx.layout.spiral_layout,
        "spring": nx.layout.spring_layout,
    }

    custom_layouts = ["random", "partite", "tree"]

    if layout_config is None:
        layout_config = {}

    if isinstance(layout, dict):
        return layout
    elif layout in automatic_layouts and layout not in custom_layouts:
        auto_layout = automatic_layouts[layout](
            nx_graph, scale=layout_scale, **layout_config
        )
        # NetworkX returns a dictionary of 3D points if the dimension
        # is specified to be 3. Otherwise, it returns a dictionary of
        # 2D points, so adjusting is required.
        if layout_config.get("dim") == 3:
            return auto_layout
        else:
            return {k: np.append(v, [0]) for k, v in auto_layout.items()}
    elif layout == "tree":
        if root_vertex is None:
            raise ValueError("Root vertex not specified.")
        return _tree_layout(
            nx_graph, root_vertex=root_vertex, scale=layout_scale, **layout_config
        )
    elif layout == "partite":
        if partitions is None or len(partitions) == 0:
            raise ValueError(
                "The partite layout requires the 'partitions' parameter to contain the partition of the vertices",
            )
        partition_count = len(partitions)
        for i in range(partition_count):
            for v in partitions[i]:
                if nx_graph.nodes[v] is None:
                    raise ValueError(
                        "The partition must contain arrays of vertices in the graph",
                    )
                nx_graph.nodes[v]["subset"] = i
        # Add missing vertices to their own side
        for v in nx_graph.nodes:
            if "subset" not in nx_graph.nodes[v]:
                nx_graph.nodes[v]["subset"] = partition_count

        auto_layout = automatic_layouts["partite"](
            nx_graph, scale=layout_scale, **layout_config
        )
        return {k: np.append(v, [0]) for k, v in auto_layout.items()}
    elif layout == "random":
        # the random layout places coordinates in [0, 1)
        # we need to rescale manually afterwards...
        auto_layout = automatic_layouts["random"](nx_graph, **layout_config)
        for k, v in auto_layout.items():
            auto_layout[k] = 2 * layout_scale * (v - np.array([0.5, 0.5]))
        return {k: np.append(v, [0]) for k, v in auto_layout.items()}
    else:
        raise ValueError(
            f"The layout '{layout}' is neither a recognized automatic layout, "
            "nor a vertex placement dictionary.",
        )


def _tree_layout(
    T: nx.classes.graph.Graph | nx.classes.digraph.DiGraph,
    root_vertex: Hashable | None,
    scale: float | tuple | None = 2,
    vertex_spacing: tuple | None = None,
    orientation: str = "down",
):
    if root_vertex is None:
        raise ValueError("The tree layout requires the root_vertex parameter")
    if not nx.is_tree(T):
        raise ValueError("The tree layout must be used with trees")

    children = {root_vertex: list(T.neighbors(root_vertex))}
    # The following code is SageMath's tree layout implementation, taken from
    # https://github.com/sagemath/sage/blob/cc60cfebc4576fed8b01f0fc487271bdee3cefed/src/sage/graphs/graph_plot.py#L1447

    # Always make a copy of the children because they get eaten
    stack = [list(children[root_vertex]).copy()]
    stick = [root_vertex]
    parent = {u: root_vertex for u in children[root_vertex]}
    pos = {}
    obstruction = [0.0] * len(T)
    if orientation == "down":
        o = -1
    else:
        o = 1

    def slide(v, dx):
        """
        Shift the vertex v and its descendants to the right by dx.
        Precondition: v and its descendents have already had their
        positions computed.
        """
        level = [v]
        while level:
            nextlevel = []
            for u in level:
                x, y = pos[u]
                x += dx
                obstruction[y] = max(x + 1, obstruction[y])
                pos[u] = x, y
                nextlevel += children[u]
            level = nextlevel

    while stack:
        C = stack[-1]
        if not C:
            p = stick.pop()
            stack.pop()
            cp = children[p]
            y = o * len(stack)
            if not cp:
                x = obstruction[y]
                pos[p] = x, y
            else:
                x = sum(pos[c][0] for c in cp) / float(len(cp))
                pos[p] = x, y
                ox = obstruction[y]
                if x < ox:
                    slide(p, ox - x)
                    x = ox
            obstruction[y] = x + 1
            continue

        t = C.pop(0)  # children should be placed left->right
        pt = parent[t]

        ct = [u for u in list(T.neighbors(t)) if u != pt]
        for c in ct:
            parent[c] = t
        children[t] = copy(ct)

        stack.append(ct)
        stick.append(t)

    # the resulting layout is then rescaled again to fit on Manim's canvas

    x_min = min(pos.values(), key=lambda t: t[0])[0]
    x_max = max(pos.values(), key=lambda t: t[0])[0]
    y_min = min(pos.values(), key=lambda t: t[1])[1]
    y_max = max(pos.values(), key=lambda t: t[1])[1]
    center = np.array([x_min + x_max, y_min + y_max, 0]) / 2
    height = y_max - y_min
    width = x_max - x_min
    if vertex_spacing is None:
        if isinstance(scale, (float, int)) and (width > 0 or height > 0):
            sf = 2 * scale / max(width, height)
        elif isinstance(scale, tuple):
            if scale[0] is not None and width > 0:
                sw = 2 * scale[0] / width
            else:
                sw = 1

            if scale[1] is not None and height > 0:
                sh = 2 * scale[1] / height
            else:
                sh = 1

            sf = np.array([sw, sh, 0])
        else:
            sf = 1
    else:
        sx, sy = vertex_spacing
        sf = np.array([sx, sy, 0])
    return {v: (np.array([x, y, 0]) - center) * sf for v, (x, y) in pos.items()}
