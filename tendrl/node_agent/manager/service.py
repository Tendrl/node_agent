from tendrl.common.etcdobj.etcdobj import EtcdObj
from tendrl.common.etcdobj import fields

class Service(EtcdObj):
    """Data structure for service details

    """
    __name__ = 'nodes/%s/Services/%s'

    node_id = fields.StrField("node_id")
    name = fields.StrField("name")
    command = fields.StrField("command")
    exe_path = fields.StrField("exe_path")
    status = fields.StrField("status")
    cpu_usage_per = fields.StrField("cpu_usage_per")
    mem_msage_per = fields.StrField("mem_msage_per")
    fds_count = fields.StrField("fds_count")
    threads_count = fields.StrField("threads_count")
    open_files_cnt = fields.StrField("open_files_cnt")

    def render(self):
        self.__name__ = self.__name__ % (
            self.node_id,
            self.name)
        return super(Service, self).render()
