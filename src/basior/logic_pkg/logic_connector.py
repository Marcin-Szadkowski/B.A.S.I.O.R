from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tramline import TramLine
from .comunicate_manager import ComuinicateManager
from .substituteroute import SubstituteRoute


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.Comunicates = ComuinicateManager()
        self.State = False
        self.trams = []
        self.route_iterator = []
        self.next_move = None
        self.Loader = DataLoader()

        self.load_data()

    def load_data(self):
        all_trams_data = self.Loader.load_all_lines()

        for i in range(0, len(all_trams_data), 2):
            self.trams.append(
                TramLine(str(all_trams_data[i][0]), str(all_trams_data[i][1]), str(all_trams_data[i + 1][1]),
                         self.Loader))
            self.trams.append(
                TramLine(str(all_trams_data[i + 1][0]), str(all_trams_data[i + 1][1]), str(all_trams_data[i][1]),
                         self.Loader, is_reversed=True))

    def push(self, message):  # Used by ClientHandler to deliver message form Client

        type = json.loads(json.dumps(message))["type"]
        if type == 'destroy':
            if self.next_move is None:
                self.next_move = self.Comunicates.send_path(self.trams, "2")
                self.State = not self.State

    def get_state(
            self):  # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
        return self.State

    def get_changes(
            self):  # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
        temp = self.next_move.copy()
        self.next_move = None

        self.State = False if self.State is True else False

        return json.dumps(temp)

    def run(self):
        while True:

            if self.next_move is None:
                self.next_move = ComuinicateManager.send_trams_coords(self.trams)
                self.State = not self.State

            time.sleep(1)

    def check_routes(self, coords):  # Method to check how deleting edges influences tram routes and takes care of it

        for tram in self.trams:
            temp_route = SubstituteRoute.calculate_bypass(tram, coords)

            if temp_route is not tram.current_route:
                tram.current_route = temp_route
                # TODO: Must add iterator modification !!!
            elif temp_route is tram.default_route:
                tram.current_route = tram.default_route

        self.next_move = self.Comunicates.send_trams_coords(self.trams)
        self.State = not self.State

        time.sleep(1)
