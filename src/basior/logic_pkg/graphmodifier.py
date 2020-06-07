import math
import networkx as nx
import osmnx as ox
import numpy as np
import itertools
import sys
from tools_pkg.mapper_data_loader import MapDataLoader
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from shapely import ops


class GraphModifier:
    """
    Class implements very important modifications that provide correct tram traffic
    """
    @staticmethod
    def simplify_for_tram_traffic(G):
        """
        Nodes of degree of 4 are irrelevant in tram network
        Without this reduction tram would make not possible(in real live) turns
        :param G: MultiDiGraph
        :return: MultiDiGraph after reduction
        """
        G = nx.MultiDiGraph(G)
        # Find all nodes of deg=4 that should be deleted
        red_nodes = [node for node in G.nodes() if nx.degree(nx.to_undirected(G), node, weight=1) == 4]
        red_nodes = [node for node in G.nodes(data=True) if node[0] in red_nodes]

        for node in red_nodes:
            # Of course we have to replace edges that contains specified node
            paths = GraphModifier.get_correct_paths(node, G)
            # paths is None if node has not exactly 4 undirected neighbors and 2 directed neighbors
            if paths is None:
                continue
            for path in paths:
                # Path states for new edge that we have to construct from two edges in path
                # Dictionary of attributes of edges in path
                edge_attributes = {}
                # Note: new edge will be constructed out of exactly two edges
                for u, v in zip(path[:-1], path[1:]):
                    # (MultiGraphs use keys (the 0 here), indexed with ints from 0 and
                    # up)
                    edge = G.edges[u, v, 0]
                    # Gather all properties of edges
                    for key in edge:
                        if key in edge_attributes:
                            # if this key already exists in the dict, append it to the
                            # value list
                            edge_attributes[key].append(edge[key])
                        else:
                            # if this key doesn't already exist, set the value to a list
                            # containing the one value
                            edge_attributes[key] = [edge[key]]
                # Reduce gathered attributes to only unique values (except Length and geometry)
                for key in edge_attributes:
                    # We have to flatten attributes because there are some situations where lists of attr includes lists
                    edge_attributes[key] = list(flatten(edge_attributes[key]))
                    # geometry and lengths are special treated
                    if not key == 'geometry' and len(set(edge_attributes[key])) == 1 and not key == 'length':
                        # if there's only 1 unique value in this attribute list,
                        # consolidate it to the single value (the zero-th)
                        edge_attributes[key] = edge_attributes[key][0]
                    elif not key == 'length' and not key == 'geometry':
                        # otherwise, if there are multiple values, keep one of each value
                        edge_attributes[key] = list(set(edge_attributes[key]))
                # We have to merge LineString geometries
                if 'geometry' in edge_attributes:
                    multi_line = []
                    for line in edge_attributes['geometry']:
                        multi_line.append(line)
                    multi_line = list(flatten(multi_line))  # cos some of edges have list of LineStrings as geometry
                    # Form MultiLineString of given LineString geometries
                    multi_line = MultiLineString(multi_line)
                    # Finally merge them
                    merged_line = ops.linemerge(multi_line)
                    # There is one (meybe more) edge that can't be merged because they are not contiguous
                    if isinstance(merged_line, LineString):
                        edge_attributes['geometry'] = merged_line
                    # So if they are not contiguous ops.linemerge() returns MultiLineString
                    elif isinstance(merged_line, MultiLineString):
                        # Here we gonna fix this by connect_lines method
                        edge_attributes['geometry'] = connect_lines(merged_line)
                else:
                    # If there is no geometry then simply add straight LineString between two nodes
                    edge_attributes['geometry'] = LineString([Point((G.nodes[node]['x'], G.nodes[node]['y']))
                                                              for node in path])
                # Sum length of edges in path
                try:
                    edge_attributes['length'] = sum(edge_attributes['length'])
                except KeyError:
                    # Not sure how many edges are relate to this exception
                    edge_attributes['length'] = 1
                # Add new edge
                G.add_edge(path[0], path[-1], **edge_attributes)
            # Remove redundant node
            G.remove_node(node[0])
        return G

    @staticmethod
    def get_correct_paths(node, graph):
        """
        Functions returns correct paths of node: deg(node) = 4, based on smallest angle between vetors
        Given node v of deg(v) = 4 (in undirected graph), it has 4 neighbors {w, u, k, m} and 2 neighbors {k, m} in
        directed graph - we are exactly interested in that case.
        To form sensible paths we have find paths (v1, v, v2), v1 in {w, u}, v2 in {k, m} that angle between
        vectors (v1, v) & (v, v2) is the smallest, so tram would make only smooth turns
        :param node:    node to delete - node of deg(node) = 4
        :param graph: directed MultiDiGraph
        :return: list of correct paths to add, single path represents correct edge that will be added to graph,
        """
        # We can use undirected graph to define undirected neighbors
        un_graph = nx.Graph(graph)
        un_graph = nx.to_undirected(un_graph)
        # Define undirected neighbors
        un_neighbors = set(un_graph.neighbors(node[0]))
        # Define directed neighbors
        di_neighbors = set(graph.neighbors(node[0]))
        un_neighbors = un_neighbors.difference(di_neighbors)
        di_neighbors = list(di_neighbors)
        un_neighbors = list(un_neighbors)
        # Here we check for condition described in above function description
        if len(un_neighbors) != 2 or len(di_neighbors) != 2:
            return None
        # First vector from 1 to given node
        vect_1 = tuple((graph.nodes[un_neighbors[0]]['y'] - node[1]['y'],
                        graph.nodes[un_neighbors[0]]['x'] - node[1]['x']))
        # Second vector from 2 to given node
        vect_2 = tuple((graph.nodes[un_neighbors[1]]['y'] - node[1]['y'],
                        graph.nodes[un_neighbors[1]]['x'] - node[1]['x']))
        # Third vector from given node to 3
        vect_3 = tuple((node[1]['y'] - graph.nodes[di_neighbors[0]]['y'],
                        node[1]['x'] - graph.nodes[di_neighbors[0]]['x']))

        # Fourth vector from given node to 4
        vect_4 = tuple((node[1]['y'] - graph.nodes[di_neighbors[1]]['y'],
                        node[1]['x'] - graph.nodes[di_neighbors[1]]['x']))
        # Calculate angles between vectors
        angle_13 = angle_between(vect_1, vect_3)
        angle_14 = angle_between(vect_1, vect_4)
        angle_23 = angle_between(vect_2, vect_3)
        angle_24 = angle_between(vect_2, vect_4)
        # The set of two correct paths will be chosen based on the smallest angle
        paths = {angle_13: [[un_neighbors[0], node[0], di_neighbors[0]], [un_neighbors[1], node[0], di_neighbors[1]]],
                 angle_14: [[un_neighbors[0], node[0], di_neighbors[1]], [un_neighbors[1], node[0], di_neighbors[0]]],
                 angle_23: [[un_neighbors[1], node[0], di_neighbors[0]], [un_neighbors[0], node[0], di_neighbors[1]]],
                 angle_24: [[un_neighbors[1], node[0], di_neighbors[1]], [un_neighbors[0], node[0], di_neighbors[0]]]}
        best_angle = sorted([angle_13, angle_14, angle_24, angle_23])[0]
        return paths[best_angle]

    @staticmethod
    def fix_edges_geometry(graph):
        """
        It unifies edges from graph - simplifies further analyze
        Very short edges from osmnx graph has no 'geometry' property
        This method adds 'geometry' to these edges - added 'geometry' is straight LINESTRING
        :param graph:
        :return:
        """
        for edge1 in graph.edges(data=True):
            try:
                line = edge1[2]['geometry']
            except KeyError:
                point1 = graph.nodes[edge1[0]]
                point2 = graph.nodes[edge1[1]]
                new_linestring = LineString([(point1['x'], point1['y']), (point2['x'], point2['y'])])
                edge1[2]['geometry'] = new_linestring

    @staticmethod
    def fix_edges_merge(graph):
        for n in graph.nodes():
            in_edges = list(graph.in_edges(n, data=True))
            out_edges = list(graph.out_edges(n, data=True))
            pairs = list(itertools.product(in_edges, out_edges))
            for pair in pairs:
                e1, e2 = pair[0], pair[1]
                if e1[2]['geometry']. intersects(e2[2]['geometry']):
                    new_geom = e1[2]['geometry'].difference(e2[2]['geometry'])
                    if not new_geom.is_empty:
                        e1[2]['geometry'] = new_geom

    @staticmethod
    def reduce_multiple_edges(graph):
        """
        Function deletes edges specified by tool from tools_pkg
        It is used in preprocessing of the graph
        :param graph:
        :return:
        """
        mdl = MapDataLoader()
        # edges to be deleted
        del_edges = mdl.deleted_edges
        for e in del_edges:
            if graph.has_edge(e[0], e[1], key=e[2]):
                graph.remove_edge(e[0], e[1], key=e[2])
            else:
                print("Warning: consider 'edges.json' update", file=sys.stderr)

    @staticmethod
    def add_termini(graph):
        """
        Functions adds an extra property to every edge`s dictionary
        Based on information gathered by tool in tool_pkg edges
        get 'terminus' as 'service' property
        :param graph:
        :return:
        """
        mdl = MapDataLoader()
        termini = mdl.get_loop_data()
        # by default 'service' is 'rail'
        for e in graph.edges(data=True):
            e[2]['service'] = 'rail'

        for terminus in termini:
            e1, e2 = terminus[0], terminus[1]
            if graph.has_edge(e1[0], e1[1], key=e1[2]):
                graph[e1[0]][e1[1]][e1[2]]['service'] = 'terminus'
            else:
                print("Warning: consider update of termini data")
            if graph.has_edge(e2[0], e2[1], key=e2[2]):
                graph[e2[0]][e2[1]][e2[2]]['service'] = 'terminus'
            else:
                print("Warning: consider update of termini data: ", terminus, file=sys.stderr)

    @staticmethod
    def connect(G):
        """
        Merge two edges into one
        :param G: MultiDiGraph
        """
        mdl = MapDataLoader()
        to_cnt = mdl.get_to_connect()
        for c in to_cnt:
            # c is a pair of edges
            path = [c[0][0], c[0][1], c[1][1]]
            edge_attributes = {}
            for e in c:

                # Note: new edge will be constructed out of exactly two edges
                edge = G.edges[e[0], e[1], e[2]]
                # Gather all properties of edges
                for key in edge:
                    if key in edge_attributes:
                        # if this key already exists in the dict, append it to the
                        # value list
                        edge_attributes[key].append(edge[key])
                    else:
                        # if this key doesn't already exist, set the value to a list
                        # containing the one value
                        edge_attributes[key] = [edge[key]]
                # Reduce gathered attributes to only unique values (except Length and geometry)
            for key in edge_attributes:
                # We have to flatten attributes because there are some situations where lists of attr includes lists
                edge_attributes[key] = list(flatten(edge_attributes[key]))
                # geometry and lengths are special treated
                if not key == 'geometry' and len(set(edge_attributes[key])) == 1 and not key == 'length':
                    # if there's only 1 unique value in this attribute list,
                    # consolidate it to the single value (the zero-th)
                    edge_attributes[key] = edge_attributes[key][0]
                elif not key == 'length' and not key == 'geometry':
                    # otherwise, if there are multiple values, keep one of each value
                    edge_attributes[key] = list(set(edge_attributes[key]))
                # We have to merge LineString geometries
            if 'geometry' in edge_attributes:
                multi_line = []
                for line in edge_attributes['geometry']:
                    multi_line.append(line)
                multi_line = list(flatten(multi_line))  # cos some of edges have list of LineStrings as geometry
                # Form MultiLineString of given LineString geometries
                multi_line = MultiLineString(multi_line)
                # Finally merge them
                merged_line = ops.linemerge(multi_line)
                # There is one (meybe more) edge that can't be merged because they are not contiguous
                if isinstance(merged_line, LineString):
                    edge_attributes['geometry'] = merged_line
                # So if they are not contiguous ops.linemerge() returns MultiLineString
                elif isinstance(merged_line, MultiLineString):
                    # Here we gonna fix this by connect_lines method
                    edge_attributes['geometry'] = connect_lines(merged_line)
            else:
                # If there is no geometry then simply add straight LineString between two nodes
                edge_attributes['geometry'] = LineString([Point((G.nodes[node]['x'], G.nodes[node]['y']))
                                                          for node in path])
                # Sum length of edges in path
            try:
                edge_attributes['length'] = sum(edge_attributes['length'])
            except KeyError:
                # Not sure how many edges are relate to this exception
                edge_attributes['length'] = 1
                # Add new edge
            G.add_edge(c[0][0], c[1][1], **edge_attributes)
            # Remove redundant node
        G.remove_node(c[0][1])

    @staticmethod
    def manual_merge(G, preproc=False):
        """
        Merge manually marked edges [(u, v), (v, w)][(p, v), (v, g)] -> (u, w), (p, g)
        :param G: MultiDiGraph
        :param preproc: if Ture then load data marked before simplify_to_tram_traffic() was performed
        """
        mdl = MapDataLoader()
        if preproc:
            to_mg = mdl.get_to_merge_preproc()
        else:
            to_mg = mdl.get_to_merge()
        # We take four edges to replace them with 2 edges
        for i in range(0, len(to_mg), 2):
            # mg is a pair of edges
            merged = [to_mg[i], to_mg[i+1]]
            for mg in merged:
                edge_attributes = {}
                path = [mg[0][0], mg[0][1], mg[1][1]]
                for e in mg:
                    # Note: new edge will be constructed out of exactly two edges
                    edge = G.edges[e[0], e[1], e[2]]
                    # Gather all properties of edges
                    for key in edge:
                        if key in edge_attributes:
                            # if this key already exists in the dict, append it to the
                            # value list
                            edge_attributes[key].append(edge[key])
                        else:
                            # if this key doesn't already exist, set the value to a list
                            # containing the one value
                            edge_attributes[key] = [edge[key]]
                    # Reduce gathered attributes to only unique values (except Length and geometry)
                for key in edge_attributes:
                    # We have to flatten attributes because there are some situations where lists of attr includes lists
                    edge_attributes[key] = list(flatten(edge_attributes[key]))
                    # geometry and lengths are special treated
                    if not key == 'geometry' and len(set(edge_attributes[key])) == 1 and not key == 'length':
                        # if there's only 1 unique value in this attribute list,
                        # consolidate it to the single value (the zero-th)
                        edge_attributes[key] = edge_attributes[key][0]
                    elif not key == 'length' and not key == 'geometry':
                        # otherwise, if there are multiple values, keep one of each value
                        edge_attributes[key] = list(set(edge_attributes[key]))
                    # We have to merge LineString geometries
                if 'geometry' in edge_attributes:
                    multi_line = []
                    for line in edge_attributes['geometry']:
                        multi_line.append(line)
                    multi_line = list(flatten(multi_line))  # cos some of edges have list of LineStrings as geometry
                    # Form MultiLineString of given LineString geometries
                    multi_line = MultiLineString(multi_line)
                    # Finally merge them
                    merged_line = ops.linemerge(multi_line)
                    # There is one (meybe more) edge that can't be merged because they are not contiguous
                    if isinstance(merged_line, LineString):
                        edge_attributes['geometry'] = merged_line
                    # So if they are not contiguous ops.linemerge() returns MultiLineString
                    elif isinstance(merged_line, MultiLineString):
                        # Here we gonna fix this by connect_lines method
                        edge_attributes['geometry'] = connect_lines(merged_line)
                else:
                    # If there is no geometry then simply add straight LineString between two nodes
                    edge_attributes['geometry'] = LineString([Point((G.nodes[node]['x'], G.nodes[node]['y']))
                                                              for node in path])
                    # Sum length of edges in path
                try:
                    edge_attributes['length'] = sum(edge_attributes['length'])
                except KeyError:
                    # Not sure how many edges are relate to this exception
                    edge_attributes['length'] = 1
                    # Add new edge
                G.add_edge(mg[0][0], mg[1][1], **edge_attributes)
            # Remove redundant node
            G.remove_node(mg[0][1])


def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """
    Function calculates angle between two vectors
    :param v1: vector
    :param v2:  vector
    :return: angle in radians
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def flatten(o, tree_types=(list, tuple)):
    """Funkcja przechodzaca po liscie"""
    if isinstance(o, tree_types):
        for value in o:
            for sub_value in flatten(value, tree_types):
                yield sub_value
    else:
        yield o


def connect_lines(multi_line):
    """
    Function connects not contiguous LineStrings (by simply adding straight line between them)
    :param multi_line:  MultiLineString - so list of LineStrings
    :return: contiguous LineString
    """
    new_lines = []
    for line1, line2 in zip(multi_line[:-1], multi_line[1:]):
        new = LineString([line1.coords[-1], line2.coords[0]])
        new_lines.append(new)
    for line in multi_line:
        new_lines.append(line)
    multi_line = MultiLineString(new_lines)
    return ops.linemerge(multi_line)
