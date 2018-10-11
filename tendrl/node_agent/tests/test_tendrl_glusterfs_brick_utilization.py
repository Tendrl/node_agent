import etcd
import importlib
import json
import maps
import sys

from mock import MagicMock
from mock import patch
from tendrl.node_agent.tests import mock_gluster_state

sys.modules['tendrl_gluster'] = mock_gluster_state
sys.modules['collectd'] = MagicMock()
utils = importlib.import_module(
    "tendrl.node_agent."
    "monitoring.collectd.collectors.gluster.utils")
sys.modules['utils'] = utils
from tendrl.node_agent.monitoring.collectd.collectors.gluster. \
    low_weight import tendrl_glusterfs_brick_utilization as brick_utilization
del sys.modules['utils']
del sys.modules['collectd']
del sys.modules['tendrl_gluster']


def read(param):
    if "data" in param.split("/")[-1]:
        with open(
            "tendrl/node_agent/tests/samples/"
                "brick_utilization.json") as f:
            return maps.NamedDict(value=f.read())
    else:
        key = "/clusters/%s/Bricks/all/%s" % (
            "7bccda8c-8c85-45a8-8be0-3f71f4db7db7",
            "10.70.41.169"
        )
        return maps.NamedDict(leaves=[maps.NamedDict(key=key)])


class TestTendrlGlusterfsBrickUtilization(object):
    @patch.object(etcd, "Client")
    def test_gluster_brick_utilization(self, client):
        client = etcd.Client()
        client.return_value = client
        with patch.object(client, "read", read):
            obj = brick_utilization.TendrlBrickUtilizationPlugin()
            with open("tendrl/node_agent/tests/output/"
                      "tendrl_glusterfs_brick_utilization_output.json"
                      ) as f:
                assert obj.get_metrics() == json.loads(f.read())
