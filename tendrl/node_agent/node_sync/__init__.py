import etcd
import gevent

from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons import sds_sync

from tendrl.node_agent.node_sync import disk_sync

# TODO(darshan) this has to be moved to Definition file

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-apid",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*"
]

TENDRL_SERVICE_TAGS = {
    "tendrl-node-agent": "tendrl/node",
    "etcd": "tendrl/central-store",
    "tendrl-apid": "tendrl/server",
    "tendrl-gluster-integration": "tendrl/integration/gluster",
    "tendrl-ceph-integration": "tendrl/integration/gluster",
    "glusterd": "gluster/server",
    "ceph-mon": "ceph/mon",
    "ceph-osd": "ceph/osd"
}


class NodeAgentSyncThread(sds_sync.StateSyncThread):
    def _run(self):
        message = Message(Message.priorities.INFO,
                          Message.publishers.COMMONS,
                          {"message": "%s running" % self.__class__.__name__})
        Event(message)

        while not self._complete.is_set():
            try:
                interval = 10
                if tendrl_ns.first_node_inventory_sync:
                    interval = 2
                    tendrl_ns.first_node_inventory_sync = False

                gevent.sleep(interval)
                tags = []
                # update node agent service details
                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, Updating Service "
                                              "data"
                                   })
                Event(message)
                for service in TENDRL_SERVICES:
                    s = tendrl_ns.node_agent.objects.Service(service=service)
                    if s.running:
                        tags.append(TENDRL_SERVICE_TAGS[service.strip("@*")])
                    s.save()
                gevent.sleep(interval)

                # updating node context with latest tags
                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, updating node "
                                              "context data with tags"
                                   })
                Event(message)
                tags = "\n".join(tags)
                tendrl_ns.node_agent.objects.NodeContext(tags=tags).save()
                gevent.sleep(interval)

                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, Updating OS data"})
                Event(message)
                tendrl_ns.node_agent.objects.Os().save()
                gevent.sleep(interval)

                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, Updating cpu"})
                Event(message)
                tendrl_ns.node_agent.objects.Cpu().save()
                gevent.sleep(interval)

                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, Updating memory"})
                Event(message)
                tendrl_ns.node_agent.objects.Memory().save()
                gevent.sleep(interval)

                message = Message(Message.priorities.INFO,
                                  Message.publishers.COMMONS,
                                  {"message": "node_sync, Updating disks"})
                Event(message)
                try:
                    tendrl_ns.etcd_orm.client.delete(
                        ("nodes/%s/Disks") % tendrl_ns.node_context.node_id,
                        recursive=True)
                except etcd.EtcdKeyNotFound as ex:
                    message = Message(Message.priorities.DEBUG,
                                      Message.publishers.COMMONS,
                                      {"message": "Given key is not present"
                                                  " in etcd . %s", ex
                                       })
                    Event(message)
                disks = disk_sync.get_node_disks()
                if "disks" in disks:
                    for disk in disks['disks']:
                        tendrl_ns.node_agent.objects.Disk(**disk).save()
                if "used_disks_id" in disks:
                    for disk in disks['used_disks_id']:
                        tendrl_ns.etcd_orm.client.write(
                            ("nodes/%s/Disks/used/%s") % (
                                tendrl_ns.node_context.node_id, disk), "")
                if "free_disks_id" in disks:
                    for disk in disks['free_disks_id']:
                        tendrl_ns.etcd_orm.client.write(
                            ("nodes/%s/Disks/free/%s") % (
                                tendrl_ns.node_context.node_id, disk), "")

            except Exception as ex:
                message = Message(Message.priorities.ERROR,
                                  Message.publishers.COMMONS,
                                  {"message": ex})
                Event(message)

        message = Message(Message.priorities.INFO,
                          Message.publishers.COMMONS,
                          {"message": "%s complete" % self.__class__.__name__})
        Event(message)
