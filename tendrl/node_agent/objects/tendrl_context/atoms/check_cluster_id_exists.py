import etcd
from tendrl.node_agent.config import TendrlConfig

config = TendrlConfig()


class CheckClusterIdExists(object):
    def run(self, parameters):
        cluster_id = parameters.get('Tendrl_context.cluster_id')
        sds_name = parameters.get("Tendrl_context.sds_name")
        sds_version = parameters.get("Tendrl_context.sds_version")

        etcd_kwargs = {'port': int(config.get("common", "etcd_port")),
                       'host': config.get("common", "etcd_connection")}

        client = etcd.Client(**etcd_kwargs)

        path = "/clusters/%s/Tendrl_context" % cluster_id
        try:
            tendrl_context = client.read(path)
        except etcd.EtcdKeyNotFound:
            return False
        etcd_sds_name = ""
        etcd_sds_version = ""
        for el in tendrl_context.children:
            if el.key.split('/')[-1] == "sds_name":
                etcd_sds_name = el.value
            if el.key.split('/')[-1] == "sds_version":
                etcd_sds_version = el.value
        if etcd_sds_version == sds_version and etcd_sds_name == sds_name:
            return True
        else:
            return False
