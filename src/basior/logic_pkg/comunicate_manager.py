class ComuinicateManager:

    @staticmethod
    def send_trams_coords(trams):
        info = {}
        for i in range(len(trams)):
            info[trams[i].number] = (next(trams[i].route_iterator[0]), next(trams[i].route_iterator[1]))

        return info
