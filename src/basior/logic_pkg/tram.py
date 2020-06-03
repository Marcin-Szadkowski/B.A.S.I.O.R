from .tramline import TramLine
from .route_iterator import RouteIterator
from shapely.geometry import Point, LineString


# Class that represents single tram
class Tram:
    def __init__(self, number, direction_to, reverse_direction, dl, is_reversed=False):
        self.number = number if not is_reversed else number + 'r'
        self.current_route = TramLine(number, direction_to, dl)  # Defaul tram route (to loop)
        self.reverse_route = TramLine(number, reverse_direction, dl)  # Route from tram loop
        self.route_iterator = RouteIterator(self.current_route.current_route)
        self.is_halted = False

    # Returns next coordinates of tram route or 'LOOP' if tram is on a loop
    def next_coords(self):
        if not self.is_halted:
            temp = self.route_iterator.get_next()

            if self.check_if_loop(temp):  # Check if tram is on a 'LOOP' and needs to turn back
                return self.route_iterator.get_next()
            else:
                return temp
        else:  # If tram is halted due to route damage, it stays in the same place until obstacle is removed
            return self.route_iterator.get_current_coords()

    # This method
    def apply_bypass(self, temp_route):
        cur_coords = self.route_iterator.get_current_coords()  # Get current position of tram

        if (temp_route is None) or not (temp_route.contains(Point(cur_coords[0], cur_coords[1]))):
            # If tram is not on substitute route which was found, it waits until edge is fixed
            self.is_halted = True
        else:
            # If tram is on substitute route then apply it. Sometimes if damage does not infuence tram route
            # bypass is equal to current tram route, but it is handled in the same way as bypass route
            idx = self.get_point_coords(temp_route, cur_coords)
            new_route = LineString(temp_route.coords[idx:])  # We start from current tram coords
            self.route_iterator.apply_new_route(new_route)
            self.is_halted = False

    # Check if tram is on loop, if so, reverses the route
    def check_if_loop(self, temp):
        if temp == ('LOOP', 'LOOP'):
            self.current_route, self.reverse_route = self.reverse_route, self.current_route
            self.route_iterator.apply_new_route(self.current_route.current_route)

            return True
        else:
            return False

    @staticmethod
    def get_point_coords(line, point):  # Function is used to get index of point if one is in list, else return False
        for i in range(len(line.coords)):
            if line.coords[i] == tuple(point):
                return i

        return False
