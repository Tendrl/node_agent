from _socket import error as _socket_error
import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from io import BlockingIOError
import json
import logging
from tendrl.commons.alert import AlertUtils
from tendrl.node_agent.alerts.base_alert_handler import AlertHandlerManager
from tendrl.node_agent.alerts.base_alert_handler import NoHandlerException
import tendrl.node_agent.manager.utils as utils
import uuid

LOG = logging.getLogger(__name__)
RECEIVE_DATA_SIZE = 4096
db_client = None


class AlertsManager(gevent.greenlet.Greenlet):

    def read_socket(self, sock, address):
        try:
            data = sock.recv(RECEIVE_DATA_SIZE)
            alert_utils = AlertUtils(db_client)
            alert_json = json.loads(data)
            alert_json['alert_id'] = str(uuid.uuid4())
            alert_json['significance'] = 'HIGH'
            alert_json['node_id'] = utils.get_local_node_context()
            alert_json['ackedby'] = ''
            alert_json['acked'] = False
            alert = alert_utils.to_obj(alert_json)
            AlertHandlerManager(db_client).handle(alert)
        except (
            KeyError,
            TypeError,
            ValueError,
            NoHandlerException
        ) as ex:
            LOG.error('Failed to handle data on alert socket.Error %s' % ex)

    def __init__(self, alerts_socket_addr, alerts_socket_port, etcd_client):
        super(AlertsManager, self).__init__()
        self.hostname = alerts_socket_addr
        self.port = alerts_socket_port
        global db_client
        db_client = etcd_client
        self.server = StreamServer(
            (self.hostname, int(self.port)),
            self.read_socket
        )

    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, _socket_error, ValueError) as ex:
            LOG.error('Error trying to serve the alerting socket forever.\
                Error %s' % ex)

    def stop(self):
        self.server.close()
