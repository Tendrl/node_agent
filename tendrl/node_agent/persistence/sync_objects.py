from tendrl.bridge_common.etcdobj.etcdobj import EtcdObj
from tendrl.bridge_common.etcdobj import fields


class SyncObject(EtcdObj):
    """A table for storing a FIFO of ClusterMonitor 'sync objects', i.e.

    cluster maps.

    """
    __name__ = 'nodes/%s/raw_map'

    data = fields.StrField("data")
    updated = fields.StrField("updated")
