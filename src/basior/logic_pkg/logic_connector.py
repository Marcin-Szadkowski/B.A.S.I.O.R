from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tramline import TramLine
from .comunicate_manager import ComuinicateManager


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.Comunicates = ComuinicateManager()
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

    def push(self, message):  # Used by ClientHandler to deliver message form Client
        print('Logic got: ', message)

    def get_state(self):  # Used by ClientHandler to determine if there is any change in game, which is supposed to be send to Client
        return self.State

    def get_changes(self):  # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
        temp = self.next_move.copy()
        self.next_move = None

        self.State = False if self.State is True else False

        return json.dumps(temp)

    def run(self):

        while True:

            if self.next_move is None:
                self.next_move = self.Comunicates.send_trams_coords(self.trams)
                self.State = not self.State

            elif self.next_move is None:
                self.next_move = self.Comunicates.send_trams_coords(self.trams)
                self.State = not self.State

            time.sleep(1)