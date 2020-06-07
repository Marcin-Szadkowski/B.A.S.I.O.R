import geopandas as gpd
from shapely.geometry import LineString
from .graphmodifier import GraphModifier
import pandas as pd
from pandas import Series
import pkg_resources
import os
import osmnx as ox


class DataLoader(object):
    """Class loads data from geojson files"""
    # Path of .geojson file with tram related data from OSM
    all_lines_data = os.path.join(pkg_resources.resource_filename(__package__, "data"), "all_tram_lines.geojson")
    # Path of .cvs file with trams to load
    lines_to_load = os.path.join(pkg_resources.resource_filename(__package__, "data"), "lines_to_load.csv")
    # Path of graph
    folder_of_graph = os.path.join(pkg_resources.resource_filename(__package__, "data"), "osmnx_graph.graphml")

    def __init__(self):
        """
        Initializes GeoDataFrame that reads all data from specified file
        + makes new GeoDataFrame with stop_positions only
        """
        self.gdf = gpd.read_file(self.all_lines_data)
        self.gdf_stops = self.gdf[(self.gdf.public_transport == "stop_position")]
        self.graph = ox.load_graphml(self.folder_of_graph)

    def load_single_line(self, line_number, direction_to, return_type="LINESTRING"):
        """
        Returns shapely.LineString or pandas.core.series.Series object based on given return_type
        return_type = ["LINESTRING", "Series" ]: default: LINESTRING
        example: tram_line_33 = load_single_line("33", "Sępolno")
        """
        if return_type == "LINESTRING":
            line = self.gdf[(self.gdf.ref == line_number) & (self.gdf.to == direction_to)].geometry.iloc[0]
            return line
        elif return_type == "Series":
            line = self.gdf[(self.gdf.ref == line_number) & (self.gdf.to == direction_to)].iloc[0]
            return line
        else:
            return None

    def load_all_lines(self):   # Returns table of all tram lines as list of lists in format: [number, direction]
        data = pd.read_csv(self.lines_to_load)
        data_table = data.loc[0:].to_numpy()

        return data_table

    def load_tram_stops(self, tram_line):
        """
        See https://shapely.readthedocs.io/en/latest/manual.html#binary-predicates -> Binary Predicates
        :param tram_line LineString or pandas Series
        :returns list of stops on given tram line (list of shapely.Point objects)
        """
        if isinstance(tram_line, LineString):
            contained = filter(tram_line.intersects, list(self.gdf_stops.geometry))
            stops_points = [p for p in contained]
            return stops_points
        elif isinstance(tram_line, Series):
            contained = filter(tram_line.geometry.iloc[0].intersects, list(self.gdf_stops.geometry))
            stops_points = [p for p in contained]
            return stops_points

    def update_graph(self):
        """
        Function downloads data from osm as osmnx graph
        Then it fixes it's geomtry
        Subseguently it executes set of commands that will make work with graph more efficient
        :return: DataLoader object graph is up to date and after all necessary fixes
        """
        G = ox.graph_from_place('Wroclaw, Poland', network_type='drive',
                                infrastructure='way["railway"~"tram"]', simplify=True)
        # Fix geometry
        GraphModifier.fix_edges_geometry(G)
        # Perform merge of manually marked edges
        GraphModifier.manual_merge(G, preproc=True)
        # Simplify for correct tram traffic
        G = GraphModifier.simplify_for_tram_traffic(G)
        # Merge manually mapped edges
        GraphModifier.manual_merge(G)
        G = GraphModifier.simplify_for_tram_traffic(G)
        G = GraphModifier.simplify_for_tram_traffic(G)
        # Fix edges geometry to prepare them to be merged
        GraphModifier.fix_edges_merge(G)
        # Deleted mapped edges
        GraphModifier.reduce_multiple_edges(G)
        # Add termini
        GraphModifier.add_termini(G)
        # Connect manualy
        GraphModifier.connect(G)
        # Finally save graph in specified location
        ox.save_graphml(G, "graph.graphml", folder=DataLoader.folder_of_graph)
        self.graph = G
