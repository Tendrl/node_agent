from gevent.server import StreamServer
from mock import MagicMock
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.commons.log'] = MagicMock()
from tendrl.node_agent.alerts.alert_socket import AlertsManager
from tendrl.node_agent.alerts.alert_socket import config
del sys.modules['tendrl.commons.log']
del sys.modules['tendrl.commons.config']


class TestAlertsManager(object):
    def test_constructor(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "tendrl_alerts_socket_port":
                return '12345'
            if parameter == 'tendrl_alerts_socket_addr':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        manager = AlertsManager()
        assert isinstance(manager.hostname, str)
        assert isinstance(manager.port, str)
        assert isinstance(manager.server, StreamServer)
        # cleanup server instance
        manager.stop()

    def test_start(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "tendrl_alerts_socket_port":
                return '12345'
            if parameter == 'tendrl_alerts_socket_addr':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        manager = AlertsManager()

        def mock_start():
            return

        monkeypatch.setattr(manager, 'start', mock_start)
        manager.start()
        # cleanup server instance
        manager.stop()

    def test_stop(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "tendrl_alerts_socket_port":
                return '12345'
            if parameter == 'tendrl_alerts_socket_addr':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        manager = AlertsManager()

        def mock_stop():
            return

        monkeypatch.setattr(manager, 'stop', mock_stop)
        manager.stop()
