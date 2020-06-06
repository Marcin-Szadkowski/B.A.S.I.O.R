from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tramline import TramLine
from .comunicate_manager import ComuinicateManager
from .substituteroute import SubstituteRoute
import random


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.Comunicates = ComuinicateManager()
        self.State = False
        self.trams = []
        self.route_iterator = []
        self.next_move = None
        self.Loader = DataLoader()
        self.path = None
        self.delay = self.get_delay("speed_5")

        self.load_data()

    def load_data(self):
        all_trams_data = self.Loader.load_all_lines()

        for elem in all_trams_data:
            self.trams.append(TramLine(str(elem[0]), str(elem[1]), self.Loader))

    def push(self, message):  # Used by ClientHandler to deliver message form Client
        print(self.trams)
        print(message)
        type = json.loads(json.dumps(message))["type"]
        if type == 'get_tram_path':
            for tram in self.trams:
                if tram.number == json.loads(json.dumps(message))["line"]:
                    self.path = self.trams.index(tram)


        elif type == 'stop_showing_path':
            self.path = None

        elif type == 'chosen_delay':
            self.delay = self.get_delay(json.loads(json.dumps(message))["delay"])

           # print(self.path)




    def get_state(
            self):  # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
        return self.State

    def get_changes( self):  # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
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



    def run(self):

        if self.next_move is None:
            self.next_move = ComuinicateManager.send_tram_lines(self.trams)
            self.State = not self.State
        time.sleep(0.09)

        if self.next_move is None:
            self.next_move = ComuinicateManager.send_possible_delays()
            self.State = not self.State

        time.sleep(0.09)
        if self.next_move is None:
            self.next_move = ComuinicateManager.send_update()
            self.State = not self.State


        while True:

            if self.next_move is None:
                if self.path is not None:
                    self.next_move = self.Comunicates.send_path(self.trams, self.path)
                    self.State = not self.State

            time.sleep(self.delay)

            if self.next_move is None:
                self.next_move = ComuinicateManager.send_trams_coords(self.trams)
                self.State = not self.State
            time.sleep(self.delay)

            """   if self.next_move is None:
                self.next_move = ComuinicateManager.send_tram_lines(self.trams)
                self.State = not self.State

            time.sleep(0.09)
            """





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
