from tendrl.commons.config import load_config
from tendrl.commons.utils import service_status

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

TENDRL_SERVICES = [
    "tendrl-node-agent",
    "etcd",
    "tendrl-apid",
    "tendrl-gluster-integration",
    "tendrl-ceph-integration",
    "glusterd",
    "ceph-mon@*",
    "ceph-osd@*",

]

config = load_config("node-agent",
                     "/etc/tendrl/node-agent/node-agent.conf.yaml")


def get_service_info(service_name):
    service = service_status.ServiceStatus(service_name,
                                           tendrl_ns.config.data[
                                               'tendrl_ansible_exec_file'])
    return {"exists": service.exists(), "running": service.status()}


def node_service_details():
    service_detail = {}

    for service in TENDRL_SERVICES:
        service_info = get_service_info(service)
        if service_info["exists"]:
            service_detail[service.rstrip("@*")] = service_info

    return service_detail
