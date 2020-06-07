class RouteIterator:
    def __init__(self, r):
        self.route = [iter(r.xy[0]), iter(r.xy[1])]
        self.last = None

    # When new route is passed new iterator is created
    def apply_new_route(self, new):
        self.route = [iter(new.xy[0]), iter(new.xy[1])]
        self.last = None

    # Get next coordinates in route
    def get_next(self):
        self.last = (next(self.route[0], 'LOOP'), next(self.route[1], 'LOOP'))

        return self.last

    # Get current coordinates (position of tram)
    def get_current_coords(self):
        return self.last
