from .dataloader import DataLoader
import matplotlib.pyplot as plt
from itertools import cycle


class TramLine(object):
    """Class represents single tram line for example '33: from Pilczyce to Sępolno' """

    def __init__(self, number, direction_to, dl):
        """
        Basic requirements to unambiguously define line
        :param number: number of line as str
        :param direction_to:
        :param dl: DataLoader object
        """
        self.number = number  # Stored as str
        self.direction_to = direction_to
        self.defult_route = dl.load_single_line(number, direction_to)  # As you can default_route is type LineString
        self.current_route = self.defult_route
        self.stops = dl.load_tram_stops(self.defult_route)  # List of shapely.Point objects
        self.deleted_edges = []  # List of deleted edges from defult route
        self.route_iterator = [[cycle(self.current_route.xy[0]), cycle(self.current_route.xy[1])], 0]  # [0] is route iterator, [1] is index of iterated list

    def show(self, with_stops=True):
        """Development tool. Plot line"""
        plt.plot(self.current_route.xy[0], self.current_route.xy[1])
        if with_stops:
            plt.scatter([p.x for p in self.stops], [p.y for p in self.stops])

        plt.show()
