class ComuinicateManager:

    """comunicates given to client"""
    @staticmethod
    def send_trams_coords(trams):
        info = {}
        info["type"] = "tram"
        for i in range(len(trams)):
            info[trams[i].number] = (next(trams[i].route_iterator[0][0]), next(trams[i].route_iterator[0][1]))

            trams[i].route_iterator[1] += 1
            trams[i].route_iterator[1] %= len(trams[i].current_route.xy[0])

        return info

    @staticmethod
    def send_update():
        info = {}
        info["type"] = "update"

        return info

    @staticmethod
    def send_tram_lines(trams):
        info = {}
        info["type"] = "bus_lines"
        lines = []
        for i in range(len(trams)):
            lines.append(trams[i].number)

        info["lines"] = lines
        return info

    @staticmethod
    def send_path(trams,number):
        info = {}
        info["type"] = "path"

        x = trams[int(number)].current_route.xy[0]
        y = trams[int(number)].current_route.xy[1]

        cors = []

        for i in range(0,len(x)):
            touple = []
            touple.append(float(y[i]))
            touple.append(float(x[i]))
            cors.append(touple)

        info["coordinates"] = cors

        return info



    @staticmethod
    def nodes_to_break(list_of_nodes_coordinates):
        info = {}
        info["type"] = "nodes_to_break"
        info["coordinates"] = list_of_nodes_coordinates
        return info


    """comunicates given to server  """


    @staticmethod
    def send_destroy(text):
        text = text.split(',')
        cors = []
        cors.append(float(text[0]))
        cors.append(float(text[1]))

        dict = {}
        dict["type"] = "destroy"
        dict["coordinates"] = cors
        return dict

    @staticmethod
    def get_path_of_tram(line):
        info = {}
        info["type"] = "get_tram_path"
        info["line"] = line

        return info
