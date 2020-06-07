import unittest
import networkx as nx
import osmnx as ox
from matplotlib import pyplot as plt
from graphmodifier import GraphModifier
from dataloader import DataLoader
from unittest import TestCase


class TestGraphModifier(TestCase):
    def test_simplify_for_tram_traffic(self):
        """
        Do:
            - mark joints to be simplified
            - plot graph
            - simplify graph
            - mark joints and plot graph
        Expected:
            - user verifies wheter operation was correct or not
        """
        # Load clean graph
        G = ox.load_graphml('clean_graph.graphml', folder="data")
        for e in G.edges(data=True):
            e[2]['new'] = False

        print(G.edges(data=True))
        nc = ['blue' if nx.degree(nx.to_undirected(G), node, weight=1) == 4 else 'red' for node in G.nodes()]
        ec = ox.get_edge_colors_by_attr(G, attr='length')
        ox.plot_graph(G, node_color=nc, edge_color=ec)
        # Fix geometry
        GraphModifier.fix_edges_geometry(G)
        G = GraphModifier.simplify_for_tram_traffic(G)
        ec = ['blue' if e[2]['new'] is True else 'red' for e in G.edges(data=True)]
        nc = ['blue' if nx.degree(nx.to_undirected(G), node, weight=1) == 4 else 'red' for node in G.nodes()]
        ox.plot_graph(G, edge_color=ec, node_color=nc)

        ec = ox.get_edge_colors_by_attr(G, attr='length')
        ox.plot_graph(G, edge_color=ec, node_color=nc, bgcolor='black')

        nr_edge = G[1904770451][1904770434][0]
        print(nr_edge)
        plt.plot(nr_edge['geometry'].xy[1], nr_edge['geometry'].xy[0])
        plt.show()
        # ox.save_graphml(G, "result_graph.graphml", folder="data")
        self.assertTrue(True)

    def test_add_termini(self):
        """
        Do:
            - update graph
            - color termini
            - display graph
        Expcted:
            - graph is shown with termin markes as blue
        :return:
        """
        # Load clean graph
        G = ox.load_graphml('clean_graph.graphml', folder="data")
        # Fix geometry
        GraphModifier.fix_edges_geometry(G)
        # Simplify for correct tram traffic
        G = GraphModifier.simplify_for_tram_traffic(G)
        # Delete edges
        # GraphModifier.reduce_multiple_edges(G)
        # Add termini
        GraphModifier.add_termini(G)
        ec = ['blue' if e[2]['service'] == 'yard' or e[2]['service'] == 'terminus' else 'gray' for e in
              G.edges(data=True)]
        ox.plot_graph(G, edge_color=ec)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
