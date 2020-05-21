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
        single_line = lines_table[0]
        line = TramLine(str(single_line[0]), single_line[1], dl)
        line.show(with_stops=True)
        self.assertTrue(True)
        for line in lines_table:
            # Create TramLine object
            tram_line = TramLine(str(line[0]), line[1], dl)
            # Convert line to nodes in order to verify graph before edges deletion
            nodes = GraphConverter.line_to_nodes(G, tram_line.default_route)
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
            # Now calculate bypas
            SubstituteRoute.calculate_bypass(G, tram_line)
            for e in deleted_edges:
                G.add_edge(e[1], e[2], geometry=e[0])


if __name__ == '__main__':
    unittest.main()
