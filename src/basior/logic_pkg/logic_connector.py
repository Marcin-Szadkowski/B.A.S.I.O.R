from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tram import Tram
from .comunicate_manager import ComuinicateManager
from .city_graph import CityGraph
from .substituteroute import SubstituteRoute
import random


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.State = False
        self.can_fix = True
        self.trams = []
        self.next_move = None
        self.Loader = DataLoader()
        self.city_graph = CityGraph(self.Loader.graph)
        self.path = None
        self.delay = self.get_delay("speed_5")
        self.load_data()

    # Load all trams specified in "data/lines_to_load.csv" and their routes (regular ones and reversed)
    def load_data(self):
        all_trams_data = self.Loader.load_all_lines()

        for i in range(0, len(all_trams_data), 2):
            self.trams.append(
                Tram(str(all_trams_data[i][0]), str(all_trams_data[i][1]), str(all_trams_data[i + 1][1]),
                     self.Loader))
            self.trams.append(
                Tram(str(all_trams_data[i + 1][0]), str(all_trams_data[i + 1][1]), str(all_trams_data[i][1]),
                     self.Loader, is_reversed=True))

    # Used by ClientHandler to deliver message form Client
    def push(self, message):
        message = json.loads(json.dumps(message))
        if message["type"] == 'destroy':  # If message "destroy" is obtained from client
            self.damage_route(message["coordinates"])  # check how client actions affect tram routes
            if self.next_move is None:
                self.next_move = ComuinicateManager.send_path(self.trams, "2")
                self.State = not self.State
        elif message["type"] == 'get_tram_path':
            for tram in self.trams:
                if tram.number == json.loads(json.dumps(message))["line"]:
                    self.path = self.trams.index(tram)

        elif message["type"] == 'stop_showing_path':
            self.path = None

        elif type == 'chosen_delay':
            self.delay = self.get_delay(json.loads(json.dumps(message))["delay"])

           # print(self.path)





    # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
    def get_state(self):

        return self.State

    # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
    def get_changes(self):
        temp = self.next_move.copy()
        self.next_move = None

        self.State = False if self.State is True else False

        return json.dumps(temp)


    def get_delay(self,speed_string):
        if speed_string == "speed_1":
            return 2;
        elif speed_string == "speed_2":
            return 1.5;
        elif speed_string == "speed_3":
            return 1;
        elif speed_string == "speed_4":
            return 0.8;
        elif speed_string == "speed_5":
            return 0.5;
        elif speed_string == "speed_6":
            return 0.2;
        elif speed_string == "speed_7":
            return 0.1;
        else:
            return 0.2;



    # Method that sends tram coordinates every x seconds to client

    def run(self):
        if self.next_move is None:
            self.next_move = ComuinicateManager.send_tram_lines(self.trams)
            self.State = not self.State
        time.sleep(0.09)

        if self.next_move is None:
            self.next_move = ComuinicateManager.send_update()
            self.State = not self.State
        time.sleep(0.09)

        delay = 0.3
        while True:

            if self.next_move is None:
                if self.path is not None:
                    self.next_move = ComuinicateManager.send_path(self.trams, self.path)
                    self.State = not self.State

            if self.next_move is None:
                self.next_move = ComuinicateManager.send_trams_coords(self.trams)
                self.State = not self.State

            if self.can_fix:
                self.can_fix_routes()

            time.sleep(self.delay)


# Method to check how deleting edges influences tram routes and takes care of it
    def damage_route(self, coords):
        self.can_fix = False
        self.city_graph.remove_edge(coords, 350)

        for tram in self.trams:
            temp_route = SubstituteRoute.calculate_bypass(self.city_graph.graph, tram.current_route)
            tram.apply_bypass(temp_route)

        self.can_fix = True

    # Method that checks if any of edges can be fixed if so then trams which were halted check if they are clear to go
    # If any tram had applied bypass, then it won't change its route to default until it gets to loop
    def can_fix_routes(self):
        was_fixed = self.city_graph.check_penalties()

        if was_fixed:
            for tram in self.trams:
                if tram.is_halted:
                    temp_route = SubstituteRoute.calculate_bypass(self.city_graph.graph, tram.current_route)
                    tram.apply_bypass(temp_route)