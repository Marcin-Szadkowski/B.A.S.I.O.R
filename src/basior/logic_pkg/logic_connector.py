from threading import Thread
import time
import json
from .dataloader import DataLoader
from .tramline import TramLine


class LogicConnector(Thread):
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.State = False
        self.trams = []
        self.next_move = None

        self.load_data()

    def load_data(self):
        Loader = DataLoader()

        self.trams.append(TramLine("33", "Sępolno", Loader))
        self.trams.append(TramLine("11", "Kromera", Loader))

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
        counter = 0  # Temporary solution

        while True:

            if self.next_move is None:
                info = {}
                for tram in self.trams:
                    info[tram.number] = (tram.current_route.xy[0][counter], tram.current_route.xy[1][counter])

                    if counter + 3 >= len(tram.current_route.xy[0]):    # Temporary solution
                        counter = 0

                self.next_move = info
                self.State = not self.State
                counter += 3

            time.sleep(1)
