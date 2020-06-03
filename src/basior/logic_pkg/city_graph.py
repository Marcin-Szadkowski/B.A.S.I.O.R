import osmnx as ox


class CityGraph:
    def __init__(self, G):
        self.graph = G
        self.damaged_edges = []

    # When any edge is damaged it is removed from graph for some time. Usually time is a count of iterations
    def remove_edge(self, coords, time):
        nr_edge = ox.get_nearest_edge(self.graph, (coords[0], coords[1]))
        u, v = nr_edge[1], nr_edge[2]
        key_del = max(self.graph[u][v], key=int)
        edge_attributes = self.graph[u][v][key_del]
        self.graph.remove_edge(u, v, key=key_del)
        self.damaged_edges.append([(u, v, edge_attributes), time])

    # Method brings back deleted graph edges
    def reinstate_edge(self, edge):
        self.graph.add_edge(edge[0], edge[1], **edge[2])

    # Method used to check which edges can be brought back and also reduce penalty (time)
    # Returns True if any edge was fixed, oth. False
    def check_penalties(self):
        fixed = False

        for e in self.damaged_edges:
            e[1] -= 1

            if e[1] == 0:
                self.reinstate_edge(e[0])
                fixed = True

        return fixed
