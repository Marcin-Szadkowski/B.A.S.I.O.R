import osmnx as ox


class CityGraph:
    def __init__(self, G):
        self.graph = G
        self.damaged_edges = []

    def remove_edge(self, coords):
        nr_edge = ox.get_nearest_edge(self.graph, (coords[1], coords[0]))
        self.graph.remove_edge(nr_edge[1], nr_edge[2])
        self.damaged_edges.append(nr_edge)

    def check_penalties(self):
        pass
