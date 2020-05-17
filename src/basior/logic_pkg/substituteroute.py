from graphconverter import GraphConverter
import networkx as nx
import osmnx as ox


class SubstituteRoute:

    @staticmethod
    def calculate_bypass(graph, edge, tram_line):
        omitted = []
        route = tram_line.route_in_order
        line = tram_line.default_route
        nodes = GraphConverter.line_to_nodes(graph, line)
        # w ten sposob mamy subgraph, ktory dzieli informacje z orginalnym grafem
        sub_graph = graph.subgraph(nodes)

        # A tak powstaje nowy niezalezny graf
        sub_graph = nx.Graph(sub_graph)

        sub_graph = nx.to_undirected(sub_graph)
        # Komponenty skladowe mozna liczyc tylko dla grafow nieskierowanych
        # Te komponenty uporzadkujemy na podstawie route

        components = list(nx.connected_components(sub_graph))  # list of sets
        components = [list(component) for component in components]

        place_dict = dict()
        for k in components:
            place_dict[route.index(k[0])] = k
        ordered_components = []
        # Uporzadkowywanie spojnych skladowych w kolejnosci jak na trasie
        for key in sorted(place_dict.keys()):
            ordered_components.append(place_dict[key])

        new_route = set()
        # Tworzymy pary skladowych (k_n, k_n+1)
        for k1, k2 in zip(ordered_components[:-1], ordered_components[1:]):
            path = SubstituteRoute.connect_components(graph, k1, k2)
            if path is None:
                continue
            new_route = new_route.union(set(path))
            new_route = new_route.union(set(k1))
            new_route = new_route.union(set(k2))

        sub_graph = graph.subgraph(new_route)
        new_route = nx.dag_longest_path(sub_graph)
        sub_graph = graph.subgraph(new_route)
        print(new_route)
        ox.plot_graph(sub_graph)
        """
        node_left = edge[1]
        node_right = edge[2]
        switch = True  # przelacznik zeby iterowac na zmiane
        iter_left = sub_graph.neighbors(node_left)
        iter_right = sub_graph.neighbors(node_right)

        while not nx.has_path(graph, node_left, node_right):
            # to ma luki - gdy dochodzimy do konca trasy to sytuacja sie sypie
            # pewnie inne luki tez sa
            if switch:
                omitted.append(node_left)
                try:
                    node_left = next(iter_left)
                    iter_left = sub_graph.neighbors(node_left)
                except StopIteration:
                    omitted.pop()
                    break
                switch = False
            elif not switch:
                omitted.append(node_right)
                try:
                    node_right = next(iter_right)
                    iter_right = sub_graph.neighbors(node_right)
                except StopIteration:
                    omitted.pop()
                    break
                switch = True
        path = nx.shortest_path(graph, node_left, node_right, weight='length')
        min_length = nx.shortest_path_length(graph, node_left, node_right, weight='length')
        print(min_length)
        print("Dlugosc sciezki: ", len(path))
        new_nodes = set(nodes).difference(set(omitted))
        new_nodes = list(new_nodes.union(set(path)))
        new_graph = graph.subgraph(new_nodes)
        # Mamy juz poczatkowe rozwiazanie
        iter_left = sub_graph.neighbors(node_left)
        iter_right = sub_graph.neighbors(node_right)

        k1 = components[0]
        k2 = components[1]

        for v in k1:
            for w in k2:
                try:
                    length = nx.shortest_path_length(graph, v, w, weight='length')
                except nx.exception.NetworkXNoPath:
                    continue
                if length < min_length:
                    path = nx.shortest_path(graph, v, w, weight='length')
                    min_length = length
        print(min_length)
        new_route = set(nodes).difference(set(omitted))
        new_route = list(new_route.union(set(path)))
        # ox.plot_graph(nx.subgraph(graph, new_route))
        # cycles = nx.find_cycle(sub_graph, orientation='ignore')

        # ox.plot_graph(new_graph)
        # simple_path = list(nx.simple_cycles(sub_graph))

        # show_edges(sub_graph, cycles)
        """
    @staticmethod
    def connect_components(graph, k1, k2):
        min_length = 3000
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