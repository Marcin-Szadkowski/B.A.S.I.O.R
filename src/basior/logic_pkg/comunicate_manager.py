class ComuinicateManager:

    """comunicates given to client"""

    @staticmethod
    def send_possible_delays():
        info = {"type": "delays"}
        delays = ["speed_1", "speed_2", "speed_3", "speed_4", "speed_5","speed_6","speed_7"]
        info["delays"] = delays
        return info

    @staticmethod
    def send_trams_coords(trams):
        info = {"type": "tram"}
        for i in range(len(trams)):
            info[trams[i].number] = trams[i].next_coords()

        return info

    @staticmethod
    def send_update():
        info = {"type": "update"}

        return info

    @staticmethod
    def send_tram_lines(trams):
        info = {"type": "bus_lines"}
        lines = []
        for i in range(len(trams)):
            lines.append(trams[i].number)

        info["lines"] = lines
        print("info   ",info  ," koniec info")
        return info

    @staticmethod
    def send_path(trams, number):
        info = {"type": "path"}

        x = trams[int(number)].temp_path.xy[0]
        y = trams[int(number)].temp_path.xy[1]

        cors = []

        for i in range(0, len(x)):
            touple = [float(y[i]), float(x[i])]
            cors.append(touple)

        info["coordinates"] = cors

        return info

    """comunicates given to server  """

    @staticmethod
    def send_destroy(text):
        text = text.split(',')
        cors = [float(text[0]), float(text[1])]

        info = {"type": "destroy", "coordinates": cors}
        return info

    @staticmethod
    def get_path_of_tram(line):
        info = {"type": "get_tram_path", "line": line}

        return info

    @staticmethod
    def send_delay(delay):
        info = {}
        info["type"] = "chosen_delay"
        info["delay"] = delay

        return info
