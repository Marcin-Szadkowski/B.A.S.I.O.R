from unittest import TestCase
import unittest
from random import randint
import osmnx as ox
from substituteroute import SubstituteRoute
from graphconverter import GraphConverter
from dataloader import DataLoader
from tramline import TramLine


class TestSubstituteRoute(TestCase):
    def test_calculate_bypass(self):
        """
        Do:
            - Foreach route delete at least one edge (could be random)
            - calculate bypas for this route on modified graph
        Expected:
            - New route is displayed
            - User manualy verifies whether new route is correct or not
        """
        dl = DataLoader()
        G = dl.graph
        lines_table = dl.load_all_lines()

        for line in lines_table:
            # Create TramLine object
            tram_line = TramLine(str(line[0]), line[1], dl)
            tram_line.show()
            # Convert line to nodes in order to verify graph before edges deletion
            nodes = GraphConverter.line_to_nodes_precise(G, tram_line)
            sub_graph = G.subgraph(nodes)
            ox.plot_graph(sub_graph)
            # Get stops on this line
            stops = dl.load_tram_stops(tram_line.default_route)    # List of shapely objects
            # Get random stops
            # change range to increase or decrease number of deleted edges
            r_stops = [stops[randint(0, len(stops)-1)] for i in range(3)]
            # Get nearest edges and delete them
            deleted_edges = list()
            for stop in r_stops:
                nr_edge = ox.get_nearest_edge(G, (stop.y, stop.x))
                G.remove_edge(nr_edge[1], nr_edge[2])
                deleted_edges.append(nr_edge)
            # Show route without edges
            sub_graph = G.subgraph(nodes)
            ox.plot_graph(sub_graph)
            # Now calculate bypas
            SubstituteRoute.calculate_bypass(G, tram_line)
            tram_line.show()
            for e in deleted_edges:
                G.add_edge(e[1], e[2], geometry=e[0])
        ox.plot_graph(G)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
