import json
import importlib
import sys

from mock import patch
from tendrl.node_agent.tests import mock_tendrl_gluster


class TestTendrlGlusterfsHealthCounters(object):
    def test_get_metrics(self):
        sys.modules["tendrl_gluster"] = mock_tendrl_gluster
        sys.modules["utils"] = self
        health_counter = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors."
            "gluster.low_weight.tendrl_glusterfs_health_counters")
        obj = health_counter.TendrlGlusterfsHealthCounters()
        data = None
        with open("tendrl/node_agent/tests/"
            "tendrl_glusterfs_health_counters_outpout.json") as f:
            assert obj.get_metrics() == json.loads(
                f.read().replace("\'", '"'))

    def get_volume_state_mapping(self, status):
        return {
            'Started': 0,
            'Stopped': 2
        }.get(status, 1)

    def get_brick_state_mapping(self, status):
        return {
            'Started': 0,
            'Stopped': 2
        }.get(status, 1)
