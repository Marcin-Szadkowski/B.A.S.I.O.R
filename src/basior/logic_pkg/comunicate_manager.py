class ComuinicateManager:

    @staticmethod
    def send_trams_coords(trams):
        info = {}
        for i in range(len(trams)):
            info[trams[i].number] = (next(trams[i].route_iterator[0][0]), next(trams[i].route_iterator[0][1]))

            trams[i].route_iterator[1] += 1
            trams[i].route_iterator[1] %= len(trams[i].current_route.xy[0])

        return info
