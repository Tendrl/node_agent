import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout
from io import BlockingIOError
import os
import sys
from tendrl.commons.message import Message
from tendrl.node_agent.message.logger import Logger
import traceback

RECEIVE_DATA_SIZE = 4096
SYSTEMD_SOCKET_PATH= "/var/run/tendrl/message.sock"


class MessageHandler(gevent.greenlet.Greenlet):
    def __init__(self):
        super(MessageHandler, self).__init__()
        self.server = StreamServer(
            self.bind_unix_listener(),
            self.read_socket
        )

    def read_socket(self, sock, *args):
        try:
            self.data = sock.recv(RECEIVE_DATA_SIZE)
            message = Message.from_json(self.data)
            Logger(message)
        except (socket_error, socket_timeout):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
        except (TypeError, ValueError, KeyError, AttributeError):
            sys.stderr.write(
                "Unable to log the message.%s\n" % self.data)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)

    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, socket_error, ValueError):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)

    def stop(self):
        pass

    def bind_unix_listener(self):
        # http://0pointer.de/blog/projects/systemd.html (search "file
        # descriptor 3")
        socket_fd = 3
        if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
            self.sock = socket.fromfd(socket_fd, socket.AF_UNIX,
                                      socket.SOCK_STREAM)
        else:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                if os.path.exists(SYSTEMD_SOCKET_PATH):
                    os.remove(SYSTEMD_SOCKET_PATH)
                self.sock.setblocking(0)
                self.sock.bind(SYSTEMD_SOCKET_PATH)
                self.sock.listen(50)
            except (TypeError, BlockingIOError, socket_error, ValueError):
                exc_type, exc_value, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb,
                                          file=sys.stderr)
        return self.sock
