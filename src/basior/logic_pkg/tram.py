from .tramline import TramLine
from .route_iterator import RouteIterator
from shapely.geometry import Point, LineString


# Class that represents single tram
class Tram:
    def __init__(self, number, direction_to, reverse_direction, dl, is_reversed=False):
        self.number = number if not is_reversed else number + 'r'
        self.current_route = TramLine(number, direction_to, dl)
        self.reverse_route = TramLine(number, reverse_direction, dl)
        self.route_iterator = RouteIterator(self.current_route.current_route)
        self.is_halted = False

    def next_coords(self):  # Returns next coordinates of tram route or 'LOOP' if tram is on a loop
        if not self.is_halted:
            temp = self.route_iterator.get_next()

            if self.check_if_loop(temp):  # Check if tram is on a 'LOOP' and needs to turn back
                return self.route_iterator.get_next()
            else:
                return temp
        else:  # If tram is halted due to route damage, it stays in the same place until obstacle is removed
            return self.route_iterator.get_current_coords()

    def apply_bypass(self, temp_route):

        cur_coords = self.route_iterator.get_current_coords()
        print(self.number, temp_route.contains(Point(cur_coords[0], cur_coords[1])))
        if (temp_route is None) or not (temp_route.contains(Point(cur_coords[0], cur_coords[1]))):
            self.is_halted = True
            print(self.number, "Halted")
        else:
            print(self.number, "Bypas")
            print(self.number, "Is the same", self.current_route.current_route is temp_route)
            idx = self.get_point_coords(temp_route, cur_coords)
            new_route = LineString(temp_route.coords[idx:])
            self.route_iterator.apply_new_route(new_route)

    def check_if_loop(self, temp):  # Check if tram is on loop, if so, reverses the route
        if temp == ('LOOP', 'LOOP'):
            self.current_route = self.reverse_route
            self.route_iterator.apply_new_route(self.current_route.current_route)

            return True
        else:
            return False

    @staticmethod
    def get_point_coords(line, point):
        for i in range(len(line.coords)):
            if line.coords[i] == tuple(point):
                return i

        return False
