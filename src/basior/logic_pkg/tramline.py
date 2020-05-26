import matplotlib.pyplot as plt
from shapely.geometry import MultiLineString
from .route_iterator import RouteIterator
from .graphconverter import GraphConverter


class TramLine(object):
    """Class represents single tram line for example '33: from Pilczyce to Sępolno' """

    def __init__(self, number, direction_to, reverse_direction, dl, is_reversed=False):
        """
        Basic requirements to unambiguously define line
        :param number: number of line as str
        :param direction_to:
        :param dl: DataLoader object
        """
        self.number = number + 'r' if is_reversed else number  # Stored as str
        self.direction_to = direction_to
        self.defult_route = dl.load_single_line(number, direction_to)  # As you can default_route is type LineString
        self.reverse_route = dl.load_single_line(number, reverse_direction)  # Return route
        self.stops = dl.load_tram_stops(self.defult_route)  # List of shapely.Point objects
        self.current_route = self.defult_route
        self.route_in_order = GraphConverter.find_route_in_order(dl, self)
        self.route_iterator = RouteIterator(self.current_route)

    def next_coords(self):
        # Returns next coodinates of tram route or 'LOOP' if tram is on a loop and needs to turn back
        temp = (next(self.route_iterator.route[0], 'LOOP'), next(self.route_iterator.route[1], 'LOOP'))

        if self.check_if_loop(temp):
            return next(self.route_iterator.route[0], 'LOOP'), next(self.route_iterator.route[1], 'LOOP')
        else:
            return temp

    def check_if_loop(self, temp):  # Check if tram is on loop, if so, reverses the route
        if temp == ('LOOP', 'LOOP'):
            self.current_route = self.reverse_route
            self.route_iterator.reverse_route(self.current_route)

            return True
        else:
            return False

    def apply_bypass(self):
        pass

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
