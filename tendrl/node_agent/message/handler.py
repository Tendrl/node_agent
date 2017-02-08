from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout
import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from io import BlockingIOError
import os
from tendrl.commons.message import Message
from tendrl.node_agent.message.logger import Logger


RECEIVE_DATA_SIZE = 4096

class MessageHandler(gevent.greenlet.Greenlet):
    def __init__(self):
        super(MessageHandler, self).__init__()
        self.server = StreamServer(
            self.bind_unix_listener(),
            self.read_socket
        )

    def read_socket(self, sock, address):
        try:
            data = sock.recv(RECEIVE_DATA_SIZE)
            message = Message.from_json(data)
            Logger(message)
        except (TypeError, ValueError, KeyError,
                socket_error, socket_timeout) as ex:
            raise ex

    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, socket_error, ValueError) as ex:
            raise ex

    def stop(self):
        self.sock.close()
        self.server.close()

    def bind_unix_listener(self):
        socket_path = tendrl_ns.config.data['logging_socket_path'] 
        try:
            if os.path.exists(socket_path):
                os.remove(socket_path)
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.bind(socket_path)
            self.sock.listen(50)
        except (TypeError, BlockingIOError, socket_error, ValueError) as ex:
            raise ex
        return self.sock
