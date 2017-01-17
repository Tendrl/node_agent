from tendrl.commons.utils.service_status import ServiceStatus

TENDRL_SERVICE_TAGS = {
    "tendrl-node-agent": "tendrl/node",
    "etcd": "tendrl/server",
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


def get_service_info(service_name):
    service = ServiceStatus(service_name)
    return {"exists": service.exists(), "running": service.status()}


def node_service_details():
    service_detail = {}

    for service in TENDRL_SERVICES:
        service_info = get_service_info(service)
        if service_info["exists"]:
            service_detail[service.rstrip("@*")] = service_info

    return service_detail
