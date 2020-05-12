from shapely.geometry import LineString
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
