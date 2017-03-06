
import json
import logging
import urllib3

from tendrl.node_agent.provisioner.ceph.provisioner_base import\
    ProvisionerBasePlugin

LOG = logging.getLogger(__name__)


class CephInstallerPlugin(ProvisionerBasePlugin):

    _MGET = 'GET'
    _MPOST = 'POST'
    _CEPH_INSTALLER_API_PORT = '8181'

    def __init__(
        self,
        provisioner_node
    ):
        self.http = urllib3.PoolManager()
        self.provisioner_node = provisioner_node

    def install_mon(self, mons):
        url = 'http://%s:%s/api/mon/install' % (
            self.provisioner_node, self._CEPH_INSTALLER_API_PORT)
        data = {
            "calamari": False,
            "hosts": mons,
            "redhat_storage": False,
            "redhat_use_cdn": True,
            "verbose": False,
        }
        encoded_data = json.dumps(data).encode('utf-8')
        resp = self.http.request(
            self._MPOST,
            url,
            body=encoded_data,
            headers={'Content-Type': 'application/json'})
        if resp.status != 201:
            return None
        try:
            res_data = json.loads(resp.data.decode('utf-8'))
        except (TypeError, ValueError, UnicodeError) as e:
            raise Exception(
                'Server response was not valid JSON: %r' % e)
        return res_data['"identifier"']

    def install_osd(self, osds):
        url = 'http://%s:%s/api/osd/install' % (
            self.provisioner_node, self._CEPH_INSTALLER_API_PORT)
        data = {
            "hosts": osds,
            "redhat_storage": False,
            "redhat_use_cdn": True,
            "verbose": False,
        }
        encoded_data = json.dumps(data).encode('utf-8')
        resp = self.http.request(
            self._MPOST,
            url,
            body=encoded_data,
            headers={'Content-Type': 'application/json'})
        if resp.status != 201:
            return None
        try:
            res_data = json.loads(resp.data.decode('utf-8'))
        except (TypeError, ValueError, UnicodeError) as e:
            raise Exception(
                'Server response was not valid JSON: %r' % e)
        return res_data['"identifier"']

    def configure_mon(self, mons):
        return None

    def configure_osd(self, osds):
        return None

    def task_status(self, task_id):
        return None
