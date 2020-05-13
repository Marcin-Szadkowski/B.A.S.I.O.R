import socket
import time
import json
import pickle
from threading import Thread


class Client(Thread):
    def __init__(self, port, ip):  # Client initiation
        super(Client, self).__init__()
        self.Socket = socket.socket()
        self.ip = ip
        self.port = port
        self.changes = []  # Queue of server_pkg communicates. To be modified in future?

    def message_to_server(self, mess):  # Sends message to server_pkg, used by UserInterface(?)
        self.Socket.send(pickle.dumps(mess))  # In future JSON will be sent, so must add serialization

    def check_changes(self):  # Used by UserInterface(?) to get changes which were sent by ClientHandler
        if len(self.changes) > 0:
            temp = self.changes.copy()
            self.changes = []

            return temp
        else:
            return False

    def run(self):
        self.Socket.connect((self.ip, self.port))
        self.Socket.setblocking(False)

        while True:
            try:
                server_mess = pickle.loads(self.Socket.recv(1024))  # TODO: check precisely if queueing in socket communication needed!
                is_received = True
            except socket.error:
                is_received = False

            if is_received:
                self.changes.append(server_mess)

            time.sleep(0.001)

        Socket.close()


def run():  # Function used for testing
    TestClient = Client(2137, '127.0.0.1')
    TestClient.start()

    time.sleep(1)
    TestClient.message_to_server('START')

    for i in range(10):
        TestClient.message_to_server(str(i))
        time.sleep(5)
        print(TestClient.check_changes())

    TestClient.join()


if __name__ == '__main__':
    run()
