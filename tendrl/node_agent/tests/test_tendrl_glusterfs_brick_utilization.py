import json
import importlib
import sys

from mock import patch
from tendrl.node_agent.tests import mock_tendrl_gluster


class TestBrickUtilization(object):
    @patch("subprocess.Popen")
    def test_get_metrics(self, popen):
        popen.return_value = self
        sys.modules["tendrl_gluster"] = mock_tendrl_gluster
        brick_utilization = importlib.import_module("tendrl.node_agent."
            "monitoring.collectd.collectors."
            "gluster.low_weight.tendrl_glusterfs_brick_utilization")
        obj = brick_utilization.TendrlGlusterfsBrickUtilization()
        with open("tendrl/node_agent/tests/"
            "tendrl_glusterfs_brick_utilization_output.json") as f:
            obj.get_metrics() == json.loads(json.dumps(f.read()))

    def communicate(self):
        return "LVM2_LV_UUID=9cKThx-Pgn0-pgPc-kbZM-d8qO-f5fi-B9s95i" \
            "$LVM2_LV_NAME=swap$LVM2_DATA_PERCENT=$LVM2_POOL_LV=" \
            "$LVM2_LV_ATTR=-wi-ao----$LVM2_LV_SIZE=2048.00" \
            "$LVM2_LV_PATH=/dev/cl_dhcp43-74/swap$LVM2_LV_METADATA" \
            "_SIZE=$LVM2_METADATA_PERCENT=$LVM2_VG_NAME=cl_dhcp43-74\n" \
            "LVM2_LV_UUID=GvhUDG-FLjn-dNZ3-JPfg-IOBi-AKsn-SIQyH2$LVM2_LV_NAME" \
            "=root$LVM2_DATA_PERCENT=$LVM2_POOL_LV=$LVM2_LV_ATTR=-wi-ao" \
            "----$LVM2_LV_SIZE=17404.00$LVM2_LV_PATH=/dev/cl_dhcp43-74/" \
            "root$LVM2_LV_METADATA_SIZE=$LVM2_METADATA_PERCENT=$LVM2_VG" \
            "_NAME=cl_dhcp43-74", None
