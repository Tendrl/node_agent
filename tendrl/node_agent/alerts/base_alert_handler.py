import datetime
import etcd
import importlib
import inspect
import logging
import os
import six
from tendrl.commons.alert import AlertUtils
from tendrl.commons.config import TendrlConfig
from tendrl.commons.singleton import to_singleton

config = TendrlConfig("node-agent", "/etc/tendrl/tendrl.conf")
LOG = logging.getLogger(__name__)


class NoHandlerException(Exception):
    pass


class HandlerMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'handlers'):
            cls.handlers = []
        else:
            cls.register_handler(cls)

    def register_handler(cls, handler):
        instance = handler()
        cls.handlers.append(instance)


@six.add_metaclass(HandlerMount)
class AlertHandler(object):
    def __init__(self):
        self.time_stamp = datetime.datetime.now().isoformat()
        self.alert = None
        self.handles = ''

    def update_alert(self):
        # Fetch alerts in etcd
        try:
            alerts = AlertUtils().get_alerts()
            # Check if similar alert already exists
            for curr_alert in alerts:
                # If similar alert exists, update the similar alert to etcd
                if AlertUtils().is_same(self.alert, curr_alert):
                    self.alert = AlertUtils().update(self.alert, curr_alert)
                    AlertUtils().store_alert(self.alert)
                    return
                # else add this new alert to etcd
            AlertUtils().store_alert(self.alert)
        except etcd.EtcdKeyNotFound:
            AlertUtils().store_alert(self.alert)
        except etcd.EtcdConnectionFailed as ex:
            LOG.error(
                'Failed to fetch existing alerts.Error %s' % ex,
                exc_info=True
            )

    def handle(self, alert_obj):
        try:
            self.alert = alert_obj
            self.alert.significance = 'HIGH'
            self.update_alert()
        except Exception as ex:
            LOG.error(
                'Failed to handle the alert %s.Error %s'
                % (str(alert_obj.to_json_string()), str(ex)),
                exc_info=True
            )


@to_singleton
class AlertHandlerManager(object):
    def load_handlers(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/handlers'
            pkg = 'tendrl.node_agent.alerts.handlers'
            for py in [f[:-3] for f in os.listdir(path)
                       if f.endswith('.py') and f != '__init__.py']:
                handler_name = '.'.join([pkg, py])
                mod = importlib.import_module(handler_name)
                clsmembers = inspect.getmembers(mod, inspect.isclass)
                for name, cls in clsmembers:
                    exec("from %s import %s" % (handler_name, name))
        except (SyntaxError, ValueError, ImportError) as ex:
            LOG.error('Failed to load the alert handlers. Error %s' %
                      ex, exc_info=True)
            raise ex

    def __init__(self):
        try:
            self.load_handlers()
            etcd_kwargs = {
                'port': int(config.get("commons", "etcd_port")),
                'host': config.get("commons", "etcd_connection")
            }
            self.etcd_client = etcd.Client(**etcd_kwargs)
            alert_handlers = []
            for handler in AlertHandler.handlers:
                alert_handlers.append(handler.handles)
            self.etcd_client.write(
                '/alerting/alert_types/node_agent',
                alert_handlers
            )
        except (SyntaxError, ValueError, ImportError) as ex:
            raise ex

    def handle(self, alert):
        for handler in AlertHandler.handlers:
            if handler.handles == alert.resource:
                handler.handle(alert)
                return
        raise NoHandlerException(
            'No alert handler defined for %s and hence cannot handle alert %s'
            % (alert['resource'], str(alert))
        )
