from _socket import error as _socket_error
import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from io import BlockingIOError
import logging
from tendrl.commons.alert import AlertUtils
from tendrl.commons.config import ConfigNotFound
from tendrl.commons.config import TendrlConfig
from tendrl.node_agent.alerts.base_alert_handler import AlertHandlerManager
from tendrl.node_agent.alerts.base_alert_handler import NoHandlerException
import tendrl.node_agent.manager.utils as utils
import uuid
import yaml

config = TendrlConfig("node-agent", "/etc/tendrl/tendrl.conf")
LOG = logging.getLogger(__name__)
RECEIVE_DATA_SIZE = 4096


class AlertsManager(gevent.greenlet.Greenlet):

    def read_socket(self, sock, address):
        try:
            data = sock.recv(RECEIVE_DATA_SIZE)
            alert_utils = AlertUtils()
            alert_json = yaml.safe_load(data)
            alert_json['alert_id'] = str(uuid.uuid4())
            alert_json['significance'] = 'HIGH'
            alert_json['node_id'] = utils.get_local_node_context()
            alert_json['ackedby'] = ''
            alert_json['acked'] = False
            alert = alert_utils.to_obj(alert_json)
            AlertHandlerManager().handle(alert)
        except (
            KeyError,
            TypeError,
            ValueError,
            NoHandlerException
        ) as ex:
            LOG.error('Failed to handle data on alert socket.Error %s' % ex)

    def __init__(self):
        super(AlertsManager, self).__init__()
        try:
            self.hostname = config.get(
                "node-agent",
                "tendrl_alerts_socket_addr"
            )
            self.port = config.get(
                "node-agent",
                "tendrl_alerts_socket_port"
            )
            self.server = StreamServer(
                (self.hostname, int(self.port)),
                self.read_socket
            )
        except ConfigNotFound as ex:
            LOG.error('Failed to fetch alerting socket configurations.\
                Error %s' % ex)

    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, _socket_error, ValueError) as ex:
            LOG.error('Error trying to serve the alerting socket forever.\
                Error %s' % ex)

    def stop(self):
        self.server.close()
