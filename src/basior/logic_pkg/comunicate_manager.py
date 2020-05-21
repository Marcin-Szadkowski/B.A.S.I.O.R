import random
class ComuinicateManager:

    @staticmethod
    def send_trams_coords(trams):
        info = {}
        info["type"] = "tram"
        for i in range(len(trams)):
            info[trams[i].number] = (next(trams[i].route_iterator[0]), next(trams[i].route_iterator[1]))

        return info

    @staticmethod
    def send_update():
        info = {}
        info["type"] = "update"

        return info

    @staticmethod
    def send_tram_lines(lines):
        info = {}
        info["type"] = "bus_line"
        info["lines"] = ["1", "2", "3", "11", "33", "70"]

        return info

    @staticmethod
    def send_path(path_coordinates):
        info = {}
        info["type"] = "path"
        info["coordinates"] = [[random.uniform(51.100,51.113), 17.03408718109131], [51.11633355911742, 17.03333616256714],
                                [51.11827317886492, 17.03850746154785], [random.uniform(51.100,51.113), random.uniform(17,17.1)]]
        #do sth
        return info

    @staticmethod
    def nodes_to_break(trams):
        info = {}
        info["type"] = "nodes_to_break"
        #do sth
        return info
