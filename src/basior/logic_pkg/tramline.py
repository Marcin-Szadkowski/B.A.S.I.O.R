import matplotlib.pyplot as plt
from shapely.geometry import MultiLineString
from .route_iterator import RouteIterator


class TramLine(object):
    """Class represents single tram line for example '33: from Pilczyce to Sępolno' """

    def __init__(self, number, direction_to, reverse_direction, dl, is_reversed=False):
        """
        Basic requirements to unambiguously define line
        :param number: number of line as str
        :param direction_to:
        :param dl: DataLoader object
        """
        self.number = number  # Stored as str
        self.direction_to = direction_to
        self.default_route = dl.load_single_line(number, direction_to)  # As you can default_route is type LineString
        self.stops = dl.load_tram_stops(self.default_route)  # List of shapely.Point objects
        self.current_route = self.default_route
        self.route_in_order = GraphConverter.find_route_in_order(dl, self)

    def show(self, with_stops=True):
        # Development tool. Plot line
        if isinstance(self.current_route, MultiLineString):
            for line in self.current_route:
                plt.plot(line.xy[0], line.xy[1])
        else:
            plt.plot(self.current_route.xy[0], self.current_route.xy[1])
        if with_stops:
            plt.scatter([p.x for p in self.stops], [p.y for p in self.stops])
        plt.show()
