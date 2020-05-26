from .graphconverter import GraphConverter
import networkx as nx
import osmnx as ox


class SubstituteRoute:

    @staticmethod
    def calculate_bypass(graph, tram_line):
        # nodes = GraphConverter.line_to_nodes(graph, line)
        nodes = GraphConverter.line_to_nodes_precise(graph, tram_line)
        # w ten sposob mamy subgraph, ktory dzieli informacje z orginalnym grafem
        sub_graph = graph.subgraph(nodes)
        # Powinno nie byc None ale nigdy nie wiadomo
        if tram_line.route_in_order is None:
            return
        route = tram_line.route_in_order
        # A tak powstaje nowy niezalezny graf
        sub_graph = nx.Graph(sub_graph)
        sub_graph = nx.to_undirected(sub_graph)
        # Komponenty skladowe mozna liczyc tylko dla grafow nieskierowanych
        # Te komponenty uporzadkujemy na podstawie route
        components = list(nx.connected_components(sub_graph))  # list of sets
        components = [list(component) for component in components]
        place_dict = dict()
        for k in components:
            if k[0] in route:
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
        # Po wykonanej wyzej operacji mozemy miec niepolaczone skladowe
        # Teraz sprawdzmy, ktore skladowe zostaly niepodlaczone
        for k in ordered_components:
            # Jesli spojna skladowa i nowa trasa sa rozlaczne, to znaczy, ze nie udalo sie jej polaczyc
            if not bool(new_route & set(k)):
                #  Sprobujmy ja dolaczyc do nowej trasy
                # Wezmy jakikolwiek wierzcholek z nowej trasy
                try:
                    node = next(iter(new_route))  # obsluzyc wyjatek gdy trasa jest pusta! ! !
                except StopIteration:
                    continue
                # Moze sie tak zdazyc, ze ten wierzcholek nie jest w trasie
                node_iter = iter(new_route)
                while node not in route:
                    try:
                        node = next(node_iter)  # Szukamy takiego, ktory jest w oryginalnej trasie
                    except StopIteration:
                        continue  # W takim razie nie podlaczymy skladowej
                path = None
                if route.index(k[0]) < route.index(node):
                    # To znaczy, ze skladowa jest przed polaczona nowa trasa
                    # Musimy to rozrozniac ze wzgledu na wyznaczanie drogi w grafie skierowanym
                    path = SubstituteRoute.connect_components(graph, k, new_route)
                else:
                    # Skladowa jest za polaczona trasa, laczymy nowa_trasa -> skladowa
                    path = SubstituteRoute.connect_components(graph, new_route, k)
                if path is not None:
                    # Dolacz droge i skladowa
                    new_route = new_route.union(set(k))
                    new_route = new_route.union(set(path))
        # Szukamy najdluzszej sciezki, wynikiem bedzie graf liniowy (redukujemy rozne odnogi trasy)
        # new_route = nx.dag_longest_path(sub_graph)
        sub_graph = graph.subgraph(new_route)
        # Jezeli udalo sie znalezc jakas droge zastepcza
        if new_route:
            #  Musimy zredukowac slepe polaczenia zeby trasa jakos wygladala
            if nx.is_directed_acyclic_graph(sub_graph):
                # Then we can find the longest path
                new_route = nx.dag_longest_path(sub_graph)
                sub_graph = graph.subgraph(new_route)
            else:
                # We have to convert graph to DAG - Directed Acyclic Graph
                sub_graph = SubstituteRoute.convert_to_dag(sub_graph)
                new_route = nx.dag_longest_path(sub_graph)
                sub_graph = graph.subgraph(new_route)
            # Finally make new LineString
            tram_line.current_route = GraphConverter.route_to_line_string(sub_graph)

    @staticmethod
    def connect_components(graph, k1, k2):
        min_length = 5000  # Dzieki tej granicy nie bierzemy pod uwage dluzszych objazdow
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
