class RouteIterator:
    def __init__(self, r):
        self.route = [iter(r.xy[0]), iter(r.xy[1])]
        self.cur_index = 0

    def reverse_route(self, reversd):
        self.route = [iter(reversd.xy[0]), iter(reversd.xy[1])]
        self.cur_index = 0
