class RouteIterator:
    def __init__(self, r):
        self.route = [iter(r.xy[0]), iter(r.xy[1])]
        self.halted = False
        self.last = None

    def reverse_route(self, reversd):
        self.route = [iter(reversd.xy[0]), iter(reversd.xy[1])]

    def get_next(self):
        if not self.halted:
            self.last = (next(self.route[0], 'LOOP'), next(self.route[1], 'LOOP'))

        return self.last
