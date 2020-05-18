from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tramline import TramLine
from itertools import cycle


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.State = False
        self.trams = []
        self.route_iterator = []
        self.next_move = None

        self.load_data()

    def load_data(self):
        Loader = DataLoader()
        all_trams_data = Loader.load_all_lines()

        for elem in all_trams_data:
            self.trams.append(TramLine(str(elem[0]), str(elem[1]), Loader))

        for tram in self.trams:
            self.route_iterator.append((cycle(tram.current_route.xy[0]), cycle(tram.current_route.xy[1])))

    def push(self, message):  # Used by ClientHandler to deliver message form Client
        print('Logic got: ', message)

    def get_state(
            self):  # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
        return self.State

    def get_changes(self):  # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
        temp = self.next_move.copy()
        self.next_move = None

        self.State = False if self.State is True else False

        return json.dumps(temp)

    def run(self):

        while True:

            if self.next_move is None:
                info = {}
                for i in range(len(self.trams)):
                    info[self.trams[i].number] = (next(self.route_iterator[i][0]), next(self.route_iterator[i][1]))

                self.next_move = info
                self.State = not self.State

            time.sleep(1)
