import socket
import time
from threading import Thread
from basior.logic_pkg.logic_connector import LogicConnector
from .client_handler import ClientHandler


class Server(Thread):
    def __init__(self, port):  # Initiate server
        super(Server, self).__init__()
        # self.handler_list = []
        self.ServerSocket = socket.socket()
        self.ServerSocket.bind(('', port))

    def connect_user(self):  # Waits for incoming connection, and connects new user
        return self.ServerSocket.accept()

    def kill_server(self):
        self.ServerSocket.close()

    def run(self):
        self.ServerSocket.listen(5)

        while True:
            client, addr = self.connect_user()
            player = ClientHandler(client, LogicConnector())  # Here ClientHandler is created
            player.start()

            time.sleep(1)


def run():  # Function used for testing
    TestServer = Server(2137)
    TestServer.start()

    # TestServer.join()


if __name__ == '__main__':
    run()
