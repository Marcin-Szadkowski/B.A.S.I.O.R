from threading import Thread
import time
import json


class LogicConnector(Thread):  # Mock object to test communication
    def __init__(self):
        super(LogicConnector, self).__init__()
        self.State = True

    def push(self, message):  # Used by ClientHandler to deliver message form Client
        print('Logic got: ' + message)

    def get_state(self):  # Used by ClientHandler to determine if there is any change in game, which i supposed to be send to Client
        return self.State

    def get_changes(self):  # Used by ClientHandler to get changelog of simulation state in order to deliver it to Client
        return json.loads('{ "line":"33", "x":51, "y":"15"}')

    def run(self):
        while True:
            self.State = not self.State

            time.sleep(1)
