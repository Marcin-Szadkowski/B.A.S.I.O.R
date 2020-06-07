from graphconverter import GraphConverter
import networkx as nx
from shapely.geometry import LineString, MultiLineString
import sys
import osmnx as ox


class SubstituteRoute:

    @staticmethod
    def calculate_bypass(graph, tram_line):
        # Just in case method gets tram_line without correct initialization
        if tram_line.route_in_order is None:
            return
        # Get list of nodes laying on the tram_line.default_route
        nodes = GraphConverter.line_to_nodes_precise(graph, tram_line)
        # make subgraph of graph. Note: these two share data
        sub_graph = graph.subgraph(nodes)
        # find weak components (because graph is directed)
        weak_components = [list(s) for s in nx.weakly_connected_components(sub_graph)]
        route = tram_line.route_in_order

        place_dict = dict()
        for k in weak_components:
            if k[0] in route:
                place_dict[route.index(k[0])] = k
        ordered_components = []
        # putting in order
        for key in sorted(place_dict.keys()):
            ordered_components.append(place_dict[key])

        new_route = set()
        # pair components (k_n, k_n+1)
        for k1, k2 in zip(ordered_components[:-1], ordered_components[1:]):
            path = SubstituteRoute.connect_components(graph, k1, k2)
            if path is None:
                continue
            new_route = new_route.union(set(path))
            new_route = new_route.union(set(k1))
            new_route = new_route.union(set(k2))
        # Previous operation does not always connect components
        # Find those not connected
        for k in ordered_components:
            # Check is compenent and new_route are disjoint sets
            if not bool(new_route & set(k)):
                # Try to connect this component
                try:
                    node = next(iter(new_route))
                except StopIteration:
                    continue
                # find next node in route
                node_iter = iter(new_route)
                while node not in route:
                    try:
                        # we are looking for node that is present in default_route
                        node = next(node_iter)
                    except StopIteration:
                        continue  # if exception occurs we cannot connect component
                path = None
                if route.index(k[0]) < route.index(node):
                    # This means that component was successfully connected to route
                    path = SubstituteRoute.connect_components(graph, k, new_route)
                else:
                    # component comes after new route. Connect:  new_route -> component
                    path = SubstituteRoute.connect_components(graph, new_route, k)
                if path is not None:
                    # add route and component
                    new_route = new_route.union(set(k))
                    new_route = new_route.union(set(path))
        # compute the longest path
        sub_graph = graph.subgraph(new_route)
        # only if we found substitute route
        if new_route:
            #  reduce all unnecessary edges ramaining in subgraph
            if nx.is_directed_acyclic_graph(sub_graph):
                # Then we can find the longest path
                new_route = nx.dag_longest_path(sub_graph)
            else:
                # We have to convert graph to DAG - Directed Acyclic Graph
                sub_graph = SubstituteRoute.convert_to_dag(sub_graph)
                new_route = nx.dag_longest_path(sub_graph)
                # sub_graph = graph.subgraph(new_route)
            new_route = SubstituteRoute.connect_to_termini(graph, new_route)
            sub_graph = graph.subgraph(new_route)
            sub_graph = SubstituteRoute.convert_to_dag(sub_graph)
            new_route = nx.dag_longest_path(sub_graph)
            sub_graph = graph.subgraph(new_route)
            # Finally make new LineString
            new_line = GraphConverter.route_to_line_string(sub_graph)
            if isinstance(new_line, LineString):
                return new_line
            else:
                return SubstituteRoute.merge_lines(new_line)
        else:
            longest_component = [c for c in sorted(weak_components, key=len, reverse=True)][0]
            sub_graph = graph.subgraph(longest_component)
            sub_graph = SubstituteRoute.convert_to_dag(sub_graph)
            path = list(nx.topological_sort(sub_graph))
            path = SubstituteRoute.connect_to_termini(graph, path)
            sub_graph = graph.subgraph(new_route)
            sub_graph = SubstituteRoute.convert_to_dag(sub_graph)
            new_route = nx.dag_longest_path(sub_graph)
            sub_graph = graph.subgraph(new_route)
            new_line = GraphConverter.route_to_line_string(sub_graph)
            if isinstance(new_line, LineString):
                return new_line
            else:
                return None

    @staticmethod
    def connect_to_termini(graph, route):
        """
        Function connects each end of the route to the nearest terminus
        :param graph: MultiDiGraph
        :param route: list of nodes in presentet order [route_start,... ,route_end]
        :return:
        """
        termini = [e for e in graph.edges(data=True) if e[2]['service'] == 'terminus']
        skipped = list()
        path = list()
        min_length = 3000
        for v in route:
            for e in termini:
                try:
                    if nx.shortest_path_length(graph, e[1], v) < min_length:
                        path = nx.shortest_path(graph, e[1], v)
                        min_length = nx.shortest_path_length(graph, e[1], v)
                except nx.NetworkXNoPath:
                    continue
            if path == list():
                skipped.append(v)
        path2 = list()
        min_length2 = 3000
        for v in route[::-1]:
            for e in termini:
                try:
                    if nx.shortest_path_length(graph, v, e[1]) < min_length2:
                        path2 = nx.shortest_path(graph, v, e[1])
                        min_length2 = nx.shortest_path_length(graph, v, e[1])
                except nx.NetworkXNoPath:
                    continue
            if path2 == list():
                skipped.append(v)
        route = set(route).difference(set(skipped))
        route = route.union(set(path))
        route = route.union(set(path2))
        return route

    @staticmethod
    def connect_components(graph, k1, k2):
        """
        Connect two components with shortest path
        :param graph: MultiDiGraph
        :param k1: component
        :param k2: component
        :return: path: list of nodes
        """
        min_length = 5000  # treshold of maximum length of new route
        path = None
        for v in k1:
            for w in k2:
                try:
                    length = nx.shortest_path_length(graph, v, w, weight='length')
                except nx.exception.NetworkXNoPath:
                    continue
                if length < min_length:
                    path = nx.shortest_path(graph, v, w, weight='length')
                    min_length = length
        return path

    @staticmethod
    def convert_to_dag(graph):
        """
        Method tries to convert graph to Directed Acyclic Graph
        Algorithm:
            - find minimum spanning tree
            - get attributes of all edges in tree
            - build DiGraph from those edges
        :param graph: MultiDiGraph, DiGraph
        :return: Directed Acyclic Graph
        """
        sub_graph = nx.MultiDiGraph(graph)
        # Find spanning tree on undirected sub_graph (method works only for undirected graphs)
        tree = nx.minimum_spanning_tree(sub_graph.to_undirected())
        # To unambiguously identify edge in MultiDiGraph we have to use it`s dictionary
        edges_dict = list(e[2] for e in tree.edges(data=True))
        edges_from_graph = [e for e in graph.edges(data=True) if e[2] in edges_dict]
        sub_graph = nx.DiGraph()
        for e in edges_from_graph:
            sub_graph.add_edge(e[0], e[1], **e[2])
        return sub_graph

    @staticmethod
    def merge_lines(lines):
        last = None
        points = []
        for line in lines:
            current = line.coords[0]

            if last is None:
                points.extend(line.coords)
            else:
                if last == current:
                    points.extend(line.coords[1:])
                else:
                    print('Skipping to merge {} {}'.format(last, current))
                    return None
            last = line.coords[-1]
        return LineString(points)
