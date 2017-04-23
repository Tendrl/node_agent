# flake8: noqa
import socket
import time


def create_ceph(parameters):
    # install the packages
    status, mons, osds = install_packages(parameters)
    if not status:
        return status
    # Configure Mons
    cluster_mons, failed = create_mons(parameters, mons)
    if not cluster_mons:
        return False
    # Configure osds
    failed = create_osds(parameters, cluster_mons, osds)

    return True



def install_packages(parameters):
    plugin = tendrl_ns.provisioner.get_plugin()
    mons = []
    osds = []
    for key, value in parameters["node_configuration"].iteritems():
        if "mon" in value["role"].lower():
            # TODO might require fqdn instead of ip?
            mons.append(value["provisioning_ip"])
        else if "osd" in value["role"].lower():
            # TODO might require fqdn instead of ip?
            osds.append(value["provisioning_ip"])
     task_id = plugin.install_mon(mons)
     status = sync_task_status(task_id)
     if not status:
         return status, mons, osds
     task_id = plugin.install_osd(mons)
      status = sync_task_status(task_id)
      if not status:
          return status, mons, osds
    return mons, osds

def create_mons(parameters, mons):
    created_mons = []
    failed = []
    plugin = tendrl_ns.provisioner.get_plugin()
    for key, value in parameters["node_configuration"].iteritems():
        if "mon" in value["role"].lower() and value["provisioning_ip"] in mons:
            task_id = plugin.configure_mon(
                # TODO need to get the hostname and pass
                value["provisioning_ip"],
                value["TendrlContext.integration_id"],
                value["name"],
                value["cluster_network"],
                pvalue["public_network"],
                created_mons
                )
                status = sync_task_status(task_id)
                if not status:
                    failed.append(value["provisioning_ip"])
                else:
                    # If success add the MON to the created list
                    created_mons.append({"host":"","interface":value["monitor_interface"]})
    return created_mons, failed

def create_osds(parameters, mons, osds):
    failed = []
    plugin = tendrl_ns.provisioner.get_plugin()
    for key, value in parameters["node_configuration"].iteritems():
        if "osd" in value["role"].lower() and value["provisioning_ip"] in osds:
            #construct the devices list
            if value[journal_colocation]:
                devices = []
            else:
                devices = {}
            for device in value["storage_disks"]
                if value[journal_colocation]:
                    devices.append(device["device"])
                else:
                    devices[device["device"]] = device[journal]
                task_id = plugin.configure_osd(
                    # TODO need to get the hostname and pass
                    value["provisioning_ip"],
                    devices,
                    value["TendrlContext.integration_id"],
                    value["name"],
                    value["journal_size"],
                    value["cluster_network"],
                    pvalue["public_network"],
                    mons
                    )
                    status = sync_task_status(task_id)
                    if not status:
                        failed.append(value["provisioning_ip"])
    return failed

def sync_task_status(task_id):
    status = False
    count = 0
    plugin = tendrl_ns.provisioner.get_plugin()
    while (count < 90):
        time.sleep( 10 )
        resp = plugin.task_status(task_id)
        if resp:
            if resp["ended"] != "":
                if resp["succeeded"]:
                    status = True
                return status
    return status
