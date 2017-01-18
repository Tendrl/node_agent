from gevent.server import StreamServer
from mock import MagicMock
import sys
sys.modules['tendrl.commons.config'] = MagicMock()
sys.modules['tendrl.commons.log'] = MagicMock()
from tendrl.node_agent.alerts.alert_socket import AlertsManager
del sys.modules['tendrl.commons.log']
del sys.modules['tendrl.commons.config']


class TestAlertsManager(object):
    def test_constructor(self, monkeypatch):
        etcd_client = MagicMock()
        manager = AlertsManager('0.0.0.0', '12345', etcd_client)
        assert isinstance(manager.hostname, str)
        assert isinstance(manager.port, str)
        assert isinstance(manager.server, StreamServer)
        # cleanup server instance
        manager.stop()

    def test_start(self, monkeypatch):
        etcd_client = MagicMock()
        manager = AlertsManager('0.0.0.0', '12345', etcd_client)

        def mock_start():
            return

        monkeypatch.setattr(manager, 'start', mock_start)
        manager.start()
        # cleanup server instance
        manager.stop()

    def test_stop(self, monkeypatch):
        etcd_client = MagicMock()
        manager = AlertsManager('0.0.0.0', '12345', etcd_client)

        def mock_stop():
            return

        monkeypatch.setattr(manager, 'stop', mock_stop)
        manager.stop()
