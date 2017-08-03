import json
import importlib
import sys

from mock import patch
from mock import MagicMock
from tendrl.node_agent.tests import mock_tendrl_gluster

class TestTendrlGlusterfsNWThroughput(object):
    @patch("netifaces.interfaces")
    @patch("socket.getfqdn")
    @patch("netifaces.ifaddresses")
    @patch("socket.gethostbyname") 
    def test_get_metrics(self, host_ip, ifaddr, fqdn, interfaces):
        interfaces.return_value = ['eth0']
        fqdn.return_value = "dhcp22-11_lab_eng.blr_redhat_com"
        ifaddr.return_value = {2 : [{"addr": "10.77.22.11"}]}
        host_ip.return_value = "10.77.22.11"
        sys.modules["tendrl_gluster"] = mock_tendrl_gluster
        network_throughput = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors.gluster.low_weight."
            "tendrl_glusterfs_peer_network_throughput")
        obj = network_throughput.TendrlGlusterfsNWThroughput()
        obj.get_rx_and_tx = MagicMock(return_value = (34197517194, 12653634011))
        with open("tendrl/node_agent/tests/"
           "tendrl_glusterfs_peer_network_throughput_output.json") as f:
            data = f.read()
            # assert obj.get_metrics() == json.loads(data)
