import etcd
from tendrl.commons.etcdobj.etcdobj import Server as etcd_server
from tendrl.commons.persistence.etcd_persister import EtcdPersister
from tendrl.node_agent.manager.tendrl_definitions_node_agent import data as \
    def_data
from tendrl.node_agent.persistence.tendrl_definitions import TendrlDefinitions
import time
import yaml


class NodeAgentEtcdPersister(EtcdPersister):
    def __init__(self, config, etcd_client):
        super(NodeAgentEtcdPersister, self).__init__(etcd_client)
        etcd_kwargs = {
            'port': int(config["configuration"]["etcd_port"]),
            'host': config["configuration"]["etcd_connection"]
        }
        self._store = etcd_server(etcd_kwargs=etcd_kwargs)

    def update_cpu(self, cpu):
        self._store.save(cpu)

    def update_memory(self, memory):
        self._store.save(memory)

    def update_os(self, os):
        self._store.save(os)

    def update_service(self, service):
        self._store.save(service)

    def update_node(self, fqdn):
        self._store.save(fqdn)

    def update_node_context(self, context):
        self._store.save(context)

    def update_tendrl_context(self, context):
        self._store.save(context)

    def update_tendrl_definitions(self, definition):
        self._store.save(definition)

    def update_platform(self, platform):
        self._store.save(platform)

    def append_definitions(self):
        try:
            defs_path = 'tendrl_definitions_node_agent/data'
            defs = yaml.load(self._store.client.read(
                defs_path).value.decode("utf-8"))
            perf_defs = yaml.load(def_data)
            for key in perf_defs:
                if key.startswith('namespace.'):
                    defs[key] = perf_defs[key]
            self.update_tendrl_definitions(
                TendrlDefinitions(updated=str(
                    time.time()),
                    data=yaml.safe_dump(defs))
            )
        except etcd.EtcdKeyNotFound:
            self.update_tendrl_definitions(
                TendrlDefinitions(
                    updated=str(time.time()),
                    data=def_data
                )
            )
