from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tram import Tram
from .comunicate_manager import ComuinicateManager
from .city_graph import CityGraph
from .substituteroute import SubstituteRoute
import osmnx as ox

class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.State = False
        self.trams = []
        self.next_move = None
        self.Loader = DataLoader()
        self.city_graph = CityGraph(self.Loader.graph.copy())

        self.load_data()

    def load_data(self):
        all_trams_data = self.Loader.load_all_lines()

        for i in range(0, len(all_trams_data), 2):
            self.trams.append(
                Tram(str(all_trams_data[i][0]), str(all_trams_data[i][1]), str(all_trams_data[i + 1][1]),
                     self.Loader))
            self.trams.append(
                Tram(str(all_trams_data[i + 1][0]), str(all_trams_data[i + 1][1]), str(all_trams_data[i][1]),
                     self.Loader, is_reversed=True))

    def push(self, message):  # Used by ClientHandler to deliver message form Client
        message = json.loads(json.dumps(message))
        if message["type"] == 'destroy':  # If message "destroy" is obtained from client
            self.check_routes(message["coordinates"])  # check how client actions affect tram routes
            if self.next_move is None:
                self.next_move = ComuinicateManager.send_path(self.trams, "2")
                self.State = not self.State

    def get_state(self):
        # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
        return self.State

    def get_changes(self):
        # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
        temp = self.next_move.copy()
        self.next_move = None

        self.State = False if self.State is True else False

        return json.dumps(temp)

    def run(self):
        while True:

            if self.next_move is None:
                self.next_move = ComuinicateManager.send_trams_coords(self.trams)
                self.State = not self.State

            time.sleep(0.3)

    def check_routes(self, coords):  # Method to check how deleting edges influences tram routes and takes care of it
        ox.plot_graph(self.city_graph.graph)
        self.city_graph.remove_edge(coords)
        ox.plot_graph(self.city_graph.graph)

        for tram in self.trams:
            temp_route = SubstituteRoute.calculate_bypass(self.city_graph.graph, tram.current_route)
            tram.apply_bypass(temp_route)
