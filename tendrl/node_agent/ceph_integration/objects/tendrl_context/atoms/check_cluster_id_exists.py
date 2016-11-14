import etcd
import json


from tendrl.node_agent.config import TendrlConfig

config = TendrlConfig()


class Compare(object):
    def run(self, **kwargs):
        sds_name = kwargs.get("sds_name")
        sds_version = kwargs.get("sds_version")
        etcd_kwargs = {'port': int(config.get("bridge_common", "etcd_port")),
                       'host': config.get("bridge_common", "etcd_connection")}
        client = etcd.Client(**etcd_kwargs)
        # get the node_agent_key some how
        # for now reading it from the json file

        with open("/etc/tendrl/tendrl-node-inventory.json") as f:
            j = json.loads(f.read())
            node_uuid = j["node_uuid"]

        path = "/nodes/%s/tendrl_context" % node_uuid
        tendrl_context = client.read(path)
        tc = json.loads(tendrl_context.value.decode('utf-8'))
        status = kwargs("status")
        if tc["sds_version"] == sds_version and tc["sds_name"] == sds_name:
            status.append(
                ("Compare",
                 "Sds version and sds names are matched successfully")
            )
        else:
            status.append(
                ("Compare",
                 "Sds version and sds names do not match")
            )
        return status
