import geopandas as gpd


class DataLoader(object):
    """Class loads data from geojson files"""
    all_lines_data = "data/all_lines_data.geojson"  # Path of .geojson file with tram related data from OSM

    def __init__(self):
        """
        Initializes GeoDataFrame that reads all data from specified file
        + makes new GeoDataFrame with stop_positions only
        """
        self.gdf = gpd.read_file(DataLoader.all_lines_data)
        self.gdf_stops = self.gdf[(self.gdf.public_transport == "stop_position")]

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

    def load_tram_stops(self, tram_line):
        """
        See https://shapely.readthedocs.io/en/latest/manual.html#binary-predicates -> Binary Predicates
        :returns list of stops on given tram line (list of shapely.Point objects)
        """
        contained = filter(tram_line.intersects, list(self.gdf_stops.geometry))
        stops_points = [p for p in contained]
        return stops_points
