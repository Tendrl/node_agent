import os
import importlib
import sys

from mock import patch
from mock import MagicMock
from shutil import copyfile

sys.modules['collectd'] = MagicMock()

SRC_PATH = "tendrl/node_agent/tests/gluster_state_sample.yaml"
DES_PATH = "/var/run/collectd_gstate"

class TendrlGlusterfsMonitoringBase(object):
    CLUSTER_TOPOLOGY = ""
    
    def __init__(self):
        self.CONFIG = dict({"integration_id": "123-12-1-21-12",
                            "peer_name": "dhcp41-169.lab.eng.blr.redhat.com"})
        self._mock_gluster_status()

    @patch("tendrl.node_agent.monitoring.collectd.collectors.\
gluster.utils.exec_command")
    def _mock_gluster_status(self, execu):
        execu.return_value = ("pytest", "")
        copyfile(SRC_PATH, DES_PATH)
        utils = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors.gluster.utils")
        TendrlGlusterfsMonitoringBase.CLUSTER_TOPOLOGY = \
            utils.get_gluster_cluster_topology()
        os.remove(DES_PATH)
