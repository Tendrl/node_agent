import logging
import os
import uuid

from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields
from tendrl.commons.utils import cmd_utils

from tendrl.node_agent.objects import base_object
from tendrl.node_agent.persistence import etcd_utils


LOG = logging.getLogger(__name__)


class DetectedCluster(base_object.NodeAgentObject):
    def __init__(self, id=None, sds_pkg_name=None, sds_pkg_version=None,
                 node_id=None, status=None, *args, **kwargs):
        super(DetectedCluster, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/DetectedCluster'
        self.id = id
        self.sds_pkg_name = sds_pkg_name
        self.sds_pkg_version = sds_pkg_version
        self.node_id = node_id

    def save(self, persister):
        cls_etcd = etcd_utils.to_etcdobj(_DetectedClusterEtcd, self)
        persister.save_detected_cluster(cls_etcd())

    def load(self):
        cls_etcd = etcd_utils.to_etcdobj(_DetectedClusterEtcd, self)
        result = tendrl_ns.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()


class _DetectedClusterEtcd(EtcdObj):
    """A table of the Detected cluster, lazily updated
    """
    __name__ = 'nodes/%s/Detected_cluster'

    def render(self):
        self.__name__ = self.__name__ % self.node_id
        return super(_DetectedClusterEtcd, self).render()

    def to_tendrl_obj(self):
        cls = _DetectedClusterEtcd
        result = DetectedCluster()
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result

# Register Tendrl object in the current namespace (tendrl_ns.node_agent)
tendrl_ns.add_object(DetectedCluster, DetectedCluster.__name__)
