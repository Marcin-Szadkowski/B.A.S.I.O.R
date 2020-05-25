from shapely import ops
from shapely.geometry import LineString, Point, MultiLineString
from pandas import Series
from .graphmodifier import connect_lines
import sys
from .graphmodifier import flatten
import networkx as nx
import osmnx as ox


class GraphConverter(object):
    """
    Class contains converters between LineString objects and set of edges from osmnx
    both representing same route
    """
    @staticmethod
    def line_to_edges(graph, tram_line, data_spec=True):
        """
            Converts tram line (LineString or pandas.core.series.Series) to set of edges from osmnx library
            :param graph from osmnx
            :param tram_line represented as LineString or pandas.core.series.Series
            :param data_spec True or False; if True each edge consists of (node, node, dict_of_osm_data)
            """
        if isinstance(tram_line, LineString):
            try:
                edges = [e for e in list(graph.edges(data=data_spec)) if tram_line.contains(e[2]['geometry'])]
                return edges
            except NameError:
                print("Error: as data_spec pass True or False")
        elif isinstance(tram_line, Series):
            try:
                edges = [e for e in list(graph.edges(data=data_spec))
                         if tram_line['geometry'].contains(e[2]['geometry'])]
                return edges
            except NameError:
                print("Error: as data_spec pass True or False")
        else:
            return None

    @staticmethod
    def line_to_nodes(graph, tram_line, data_spec=True):
        """
        Get nodes from graph that lay on line
        :param graph: osmnx graph
        :param tram_line: LineString or pandas Series
        :param data_spec: True or False
        :return: List of ids of nodes from osmnx graph
        """
        if isinstance(tram_line, LineString):
            try:
                vertices = [v[0] for v in list(graph.nodes(data=data_spec))
                            if tram_line.contains(Point(v[1]['x'], v[1]['y']))]
                return vertices
            except NameError:
                print("Error: as data_spec pass True or False")
        elif isinstance(tram_line, Series):
            try:
                vertices = [v[0] for v in list(graph.nodes(data=data_spec))
                            if tram_line['geometry'].contains(Point(v[1]['y'], v[1]['x']))]
            except NameError:
                print("Error: as data_spec pass True or False")
                return vertices
        else:
            return None

    @staticmethod
    def find_route_in_order(dl, tram_line):
        """
        Basically it finds the longest path so that nodes are in correct orders
        Most of given subgraphs have cycles, because of that we need to find minimum spanning tree,
        then we can use dag_longest_path
        :param dl: DataLoader object
        :param tram_line: LineString representig route of tram
        :return: list of nodes in order [start_of_route, ..., end_of_route]
        """
        nodes = GraphConverter.line_to_nodes(dl.graph, tram_line)
        # w ten sposob mamy subgraph, ktory dzieli informacje z orginalnym grafem
        sub_graph = dl.graph.subgraph(nodes)
        # Always work on copy of graph
        sub_graph = nx.Graph(sub_graph)
        # Find spanning tree on undirected sub_graph (method works only for undirected graphs)
        tree = nx.minimum_spanning_tree(sub_graph.to_undirected())
        # To unambiguously identify edge in MultiDiGraph we have to use it`s dictionary
        edges_dict = list(e[2] for e in tree.edges(data=True))
        edges_from_graph = [e for e in dl.graph.edges(data=True) if e[2] in edges_dict]
        # Make new graph based on edges from spanning Tree
        sub_graph = nx.DiGraph(edges_from_graph)
        # We did all operations above because this method doesn`t support graphs with cycles
        return nx.dag_longest_path(sub_graph)

    @staticmethod
    def route_to_line_string(graph):
        """
        Method converts route representes as Directed Acyclic Graph to LineString
        :param graph: MultiDiGraph, DiGraph
        :return: LineString
        """
        geometries = [e[2]['geometry'] for e in graph.edges(data=True)]
        # Some edges have list as geometry
        geometries = list(flatten(geometries))
        # Form MultiLineString of given LineString geometries
        multi_line = MultiLineString(geometries)
        # Finally merge them
        merged_line = ops.linemerge(multi_line)
        if isinstance(merged_line, MultiLineString):
            print("Warning: route can`t be merged", file=sys.stderr)
            # merged_line = connect_lines(merged_line)
        return merged_line
