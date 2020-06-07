

class ComuinicateManager:
    """class responsible for defining messages between the server and client"""

    """comunicates given to client"""

    @staticmethod
    def send_possible_delays():
        """ message defines available speed for tram simulation"""

        info = {"type": "delays"}
        delays = ["speed_1", "speed_2", "speed_3", "speed_4", "speed_5","speed_6","speed_7"]
        info["delays"] = delays

        return info

    @staticmethod
    def send_trams_coords(trams):
        """ message sends next next coordinates for trams"""

        info = {"type": "tram"}

        for i in range(len(trams)):
            info[trams[i].number] = trams[i].next_coords()

        return info

    @staticmethod
    def send_update():
        """message sends info to reload application"""

        info = {"type": "update"}

        return info

    @staticmethod
    def send_tram_lines(trams):
        """message contains info about all identifying number for tramlines"""

        info = {"type": "bus_lines"}
        lines = []

        for i in range(len(trams)):
            lines.append(trams[i].number)

        info["lines"] = lines

        return info

    @staticmethod
    def send_path(trams, number):
        """message sends route of chosen tram"""

        info = {"type": "path"}

        x = trams[int(number)].temp_path.xy[0]
        y = trams[int(number)].temp_path.xy[1]
        cors = []

        for i in range(0, len(x)):
            pair = [float(y[i]), float(x[i])]
            cors.append(pair)

        info["coordinates"] = cors

        return info

    @staticmethod
    def send_ready():
        """message informs that server is ready to send coordinates"""

        info = {"type": "ready"}

        return info

    """messages given to server  """

    @staticmethod
    def send_destroy(text):
        """message from client to server that tells which geo coors"""

        text = text.split(',')
        cors = [float(text[0]), float(text[1])]

        info = {"type": "destroy", "coordinates": cors}
        return info

    @staticmethod
    def get_path_of_tram(line):
        """message informs server which tram route was chosen to draw"""

        info = {"type": "get_tram_path", "line": line}

        return info

    @staticmethod
    def send_delay(delay):
        """message sends simulation delay chosen by user"""

        info = {}
        info["type"] = "chosen_delay"
        info["delay"] = delay

        return info