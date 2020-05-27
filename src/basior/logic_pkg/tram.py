from .tramline import TramLine
from .route_iterator import RouteIterator


# Class that represents single tram
class Tram:
    def __init__(self, number, direction_to, reverse_direction, dl, is_reversed=False):
        self.number = number if not is_reversed else number + 'r'
        self.current_route = TramLine(number, direction_to, dl)
        self.reverse_route = TramLine(number, reverse_direction, dl)
        self.route_iterator = RouteIterator(self.current_route.current_route)

    def next_coords(self):  # Returns next coordinates of tram route or 'LOOP' if tram is on a loop
        temp = self.route_iterator.get_next()

        if self.check_if_loop(temp):    # Check if tram is on a 'LOOP' and needs to turn back
            return self.route_iterator.get_next()
        else:
            return temp

    def apply_bypass(self):
        pass

    def check_if_loop(self, temp):  # Check if tram is on loop, if so, reverses the route
        if temp == ('LOOP', 'LOOP'):
            self.current_route = self.reverse_route
            self.route_iterator.reverse_route(self.current_route.current_route)

            return True
        else:
            return False
