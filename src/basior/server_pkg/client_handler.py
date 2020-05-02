import socket
import time
from threading import Thread


class ClientHandler(Thread):
    def __init__(self, client, logic):  # Initiate ClientHandler
        super(ClientHandler, self).__init__()
        self.ClientSocket = client
        self.ClientSocket.setblocking(False)
        self.Logic = logic

    def message_to_client(self, mess):  # In future JSON will be sent, so must add serialization
        self.ClientSocket.send(bytes(mess, 'utf-8'))

    def message_to_logic(self, mess):  # Pushes Client message to LogicConnector
        self.Logic.push(mess)

    def start_simulation(self):  # Starts simulation
        self.Logic.start()

    def check_game_changes(self):  # Check if LogicConnector wants to send changes to Client, if so it sends it
        if self.Logic.get_state():
            return self.Logic.get_changes()
        else:
            return False

    def run(self):

        while True:

            try:
                mess = self.ClientSocket.recv(1024).decode("utf-8")  # TODO: check precisely if queueing in socket communication needed!
                is_received = True
            except socket.error:
                is_received = False

            if is_received:
                if mess == 'START':
                    self.start_simulation()
                else:
                    self.message_to_logic(mess)

            game_changes = self.check_game_changes()

            if game_changes is not False:
                self.message_to_client(game_changes)

            time.sleep(0.001)
