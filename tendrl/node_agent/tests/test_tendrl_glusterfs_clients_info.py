import importlib
import sys

from mock import patch
from mock import MagicMock


class TestTendrlGlusterfsClientsInfo(object):
    def test_read_callback(self):
        mock = sys.modules["glusterfs"]  = MagicMock()
        sys.modules["glusterfs.utils"] = MagicMock()
        client_info = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors."
            "gluster.heavy_weight.tendrl_glusterfs_clients_info")
        client_info.tendrl_glusterfs_utils = self
        client_info.CONFIG["graphite_host"] = "127.0.0.1"
        client_info.CONFIG["graphite_port"] = "10800"
        client_info.CONFIG["integration_id"] = "123-132-13-13-31"
        client_info.tendrl_glusterfs_utils.write_graphite = MagicMock()
        client_info.read_callback()
        client_info.tendrl_glusterfs_utils.\
write_graphite.assert_called_once_with(
    'clusters.123-132-13-13-31.volumes.GlusterVolume.connections_count',
    8,
    '127.0.0.1',
    '10800')

    def exec_command(self, cmd):
        with open(
            "tendrl/node_agent/tests/gluster_volume_status.xml") as f:
            return f.read(), None

    
