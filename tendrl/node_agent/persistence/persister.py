from tendrl.commons.persistence.etcd_persister import EtcdPersister


class NodeAgentEtcdPersister(EtcdPersister):
    def __init__(self, etcd_orm):
        super(NodeAgentEtcdPersister, self).__init__(etcd_orm)

    def update_cpu(self, cpu):
        self.etcd_orm.save(cpu)

    def update_memory(self, memory):
        self.etcd_orm.save(memory)

    def update_os(self, os):
        self.etcd_orm.save(os)

    def update_service(self, service):
        self.etcd_orm.save(service)

    def update_node(self, fqdn):
        self.etcd_orm.save(fqdn)

    def update_node_context(self, context):
        self.etcd_orm.save(context)

    def update_tendrl_context(self, context):
        self.etcd_orm.save(context)

    def update_tendrl_definitions(self, definition):
        self.etcd_orm.save(definition)

    def update_platform(self, platform):
        self.etcd_orm.save(platform)
