from shapely.geometry import LineString, Point
from pandas import Series


class GraphConverter(object):
    """
    Class contains converters between LineString objects and set of edges from osmnx
    both representing same route
    """
    @staticmethod
    def line_to_edges(graph, tram_line, data_spec=True):
        """
            Converts tram line (LineString or pandas.core.series.Series) to set of edges from osmnx library
            :param graph from osmnx
            :param tram_line represented as LineString or pandas.core.series.Series
            :param data_spec True or False; if True each edge consists of (node, node, dict_of_osm_data)
            """
        if isinstance(tram_line, LineString):
            try:
                edges = [e for e in list(graph.edges(data=data_spec)) if tram_line.contains(e[2]['geometry'])]
                return edges
            except NameError:
                print("Error: as data_spec pass True or False")
        elif isinstance(tram_line, Series):
            try:
                edges = [e for e in list(graph.edges(data=data_spec))
                         if tram_line['geometry'].contains(e[2]['geometry'])]
                return edges
            except NameError:
                print("Error: as data_spec pass True or False")
        else:
            return None

    @staticmethod
    def line_to_nodes(graph, tram_line, data_spec=True):
        """
        Get nodes from graph that lay on line
        :param graph: osmnx graph
        :param tram_line: LineString or pandas Series
        :param data_spec: True or False
        :return: List of ids of nodes from osmnx graph
        """
        if isinstance(tram_line, LineString):
            try:
                vertices = [v[0] for v in list(graph.nodes(data=data_spec))
                            if tram_line.contains(Point(v[1]['x'], v[1]['y']))]
                return vertices
            except NameError:
                print("Error: as data_spec pass True or False")
        elif isinstance(tram_line, Series):
            try:
                vertices = [v[0] for v in list(graph.nodes(data=data_spec))
                            if tram_line['geometry'].contains(Point(v[1]['y'], v[1]['x']))]
                return vertices
            except NameError:
                print("Error: as data_spec pass True or False")
        else:
            return None
