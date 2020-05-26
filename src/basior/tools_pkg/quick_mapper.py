import osmnx as ox
import pkg_resources
import os
import pandas
import sys
import folium
import osmnx as ox
import networkx as nx
import osmnx as ox
from IPython.display import IFrame
ox.config(log_console=True, use_cache=True)

G = ox.load_graphml('osmnx_graph.graphml')


# plot the street network with folium
graph_map = ox.plot_graph_folium(G, edge_width=2)

filepath = 'templates/graph.html'
graph_map.save(filepath)
IFrame(filepath, width=600, height=500)
#fig,ax = ox.plot_graph(G)