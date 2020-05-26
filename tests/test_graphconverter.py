import unittest
from unittest import TestCase
from tramline import TramLine
from dataloader import DataLoader
from graphconverter import GraphConverter
import osmnx as ox


class TestGraphConverter(TestCase):
    def test_line_to_nodes(self):
        """
        Do:
            - Make new TramLine object
            - Show it`s default route
            - Convert default_route to list of nodes and siplay as subgraph
        Expected:
            - Both LineString and subgraph are displayed
            - User manually verifies whether conversion is correct or not
        """
        # Load data
        dl = DataLoader()
        dl.update_graph()
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
            tram_line.current_route = GraphConverter.route_to_line_string(sub_graph)
            tram_line.show()
            print(tram_line.current_route.contains(tram_line.stops[0]))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
