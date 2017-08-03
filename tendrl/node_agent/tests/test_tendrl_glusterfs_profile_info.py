import json
import importlib
import sys

from mock import patch
from tendrl.node_agent.tests import mock_tendrl_gluster


class TestTendrlGlusterfsProfileInfo(object):
    def test_get_metrics(self):
        sys.modules["tendrl_gluster"] = mock_tendrl_gluster
        sys.modules["utils"]  = self
        profile_info = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors."
            "gluster.low_weight.tendrl_glusterfs_profile_info")
        obj = profile_info.TendrlGlusterfsProfileInfo()
        with open("tendrl/node_agent/tests/"
            "tendrl_glusterfs_profile_info_output.json") as f:
            data= f.read()
            assert obj.get_metrics() == json.loads(data)
    
    def exec_command(self, cmd):
        with open("tendrl/node_agent/tests/gluster_volume_profile_sample.yaml") as f:
            return (f.read(), None)
