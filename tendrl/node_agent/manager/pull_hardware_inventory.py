from command import Command
import logging
import netaddr
import netifaces as ni
import platform
import socket
from tendrl.node_agent.manager import utils as mgr_utils

LOG = logging.getLogger(__name__)


def getNodeCpu():
    '''returns structure

    {"nodename": [{"Architecture":   "architecture",

                   "CpuOpMode":      "cpuopmode",

                   "CPUs":           "cpus",

                   "VendorId":       "vendorid",

                   "ModelName":      "modelname",

                   "CPUFamily":      "cpufamily",

                   "Model":          "Model",

                   "CoresPerSocket": "corespersocket"}, ...], ...}

    '''
    cmd = Command({"_raw_params": "lscpu"})
    out, err = cmd.start()
    out = out['stdout']
    cpuinfo = {}
    if out:
        info_list = out.split('\n')
        cpuinfo = {
            'Architecture': info_list[0].split(':')[1].strip(),
            'CpuOpMode': info_list[1].split(':')[1].strip(),
            'CPUs': info_list[3].split(':')[1].strip(),
            'VendorId': info_list[9].split(':')[1].strip(),
            'ModelName': info_list[12].split(':')[1].strip(),
            'CPUFamily': info_list[10].split(':')[1].strip(),
            'Model': info_list[11].split(':')[1].strip(),
            'CoresPerSocket': info_list[6].split(':')[1].strip()
        }
    else:
            cpuinfo = {
                'Architecture': '', 'CpuOpMode': '',
                'CPUs': '', 'VendorId': '',
                'ModelName': '', 'CPUFamily': '',
                'Model': '', 'CoresPerSocket': ''
            }

    return cpuinfo


def getNodeMemory():
    '''returns structure

    {"nodename": [{"TotalSize": "totalsize",

                   "SwapTotal": "swaptotal",

                   "Type":      "type"}, ...], ...}

    '''

    cmd = Command({"_raw_params": "cat /proc/meminfo"})
    out, err = cmd.start()
    out = out['stdout']

    memoinfo = {}
    if out:
        info_list = out.split('\n')
        memoinfo = {
            'TotalSize': info_list[0].split(':')[1].strip(),
            'SwapTotal': info_list[14].split(':')[1].strip()
        }
    else:
        memoinfo = {
            'TotalSize': '',
            'SwapTotal': ''
        }

    return memoinfo


def getNodeOs():
    cmd = Command({"_raw_params": "getenforce"})
    out, err = cmd.start()
    se_out = out['stdout']

    osinfo = {}
    os_out = platform.linux_distribution()

    osinfo = {
        'Name': os_out[0],
        'OSVersion': os_out[1],
        'KernelVersion': platform.release(),
        'SELinuxMode': se_out,
        'FQDN': socket.getfqdn()
    }

    return osinfo


def getTendrlContext():
    tendrl_context = {"sds_name": "", "sds_version": ""}
    cmd = Command({"_raw_params": "gluster --version"})
    out, err = cmd.start()
    if out["rc"] == 0:
        nvr = out['stdout']
        tendrl_context["sds_name"] = nvr.split()[0]
        tendrl_context["sds_version"] = nvr.split()[1]
        return tendrl_context

    cmd = Command({"_raw_params": "ceph --version"})
    out, err = cmd.start()
    if out["rc"] == 0:
        nvr = out['stdout']
        tendrl_context["sds_name"] = nvr.split()[0]
        tendrl_context["sds_version"] = nvr.split()[2].split("-")[0]

    return tendrl_context


def get_node_disks():
    rv = {}
    rv["disks"] = []
    rv["free_disks_id"] = []
    rv["used_disks_id"] = []
    disks, err = get_all_disks()
    if err == "":
        columns = 'NAME,KNAME,PKNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,UUID,' \
            'RA,RO,RM,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,MIN-IO,OPT-IO,' \
            'PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,DISC-ALN,DISC-GRAN,DISC-MAX,' \
            'DISC-ZERO'
        keys = columns.split(',')
        lsblk = (
            "lsblk --all --bytes --noheadings --output='%s' --path --raw" %
            columns)
        cmd = Command({"_raw_params": lsblk})
        out, err = cmd.start()
        if not err:
            if not out['stderr']:
                devlist = {}
                devlist = map(lambda line: dict(zip(keys, line.split(' '))),
                              out['stdout'].splitlines())
                for disk in disks:
                    for dev_info in devlist:
                        if dev_info['NAME'] == disk['device_name']:
                            disk['disk_kernel_name'] = dev_info['KNAME']
                            disk['parent_name'] = dev_info['PKNAME']
                            disk['major_to_minor_no'] = dev_info['MAJ:MIN']
                            disk['fstype'] = dev_info['FSTYPE']
                            disk['mount_point'] = dev_info['MOUNTPOINT']
                            disk['label'] = dev_info['LABEL']
                            disk['fsuuid'] = dev_info['UUID']
                            disk['read_ahead'] = dev_info['RA']
                            if dev_info['RO'] == '0':
                                disk['read_only'] = False
                            else:
                                disk['read_only'] = True
                            if dev_info['RM'] == '0':
                                disk['removable_device'] = False
                            else:
                                disk['removable_device'] = True
                            disk['size'] = dev_info['SIZE']
                            disk['state'] = dev_info['STATE']
                            disk['owner'] = dev_info['OWNER']
                            disk['group'] = dev_info['GROUP']
                            disk['mode'] = dev_info['MODE']
                            disk['alignement'] = dev_info['ALIGNMENT']
                            disk['min_io_size'] = dev_info['MIN-IO']
                            disk['optimal_io_size'] = dev_info['OPT-IO']
                            disk['phy_sector_size'] = dev_info['PHY-SEC']
                            disk['log_sector_size'] = dev_info['LOG-SEC']
                            if disk['disk_type'] == "disk":
                                disk['ssd'] = is_ssd(dev_info['ROTA'])
                            else:
                                disk['ssd'] = False
                            disk['scheduler_name'] = dev_info['SCHED']
                            disk['req_queue_size'] = dev_info['RQ-SIZE']
                            disk['discard_align_offset'] = dev_info['DISC-ALN']
                            disk['discard_granularity'] = dev_info['DISC-GRAN']
                            disk['discard_max_bytes'] = dev_info['DISC-MAX']
                            disk['discard_zeroes_data'] = dev_info['DISC-ZERO']
                            rv['disks'].append(disk)
                            if disk['disk_type'] == "disk":
                                rv['free_disks_id'].append(disk['disk_id'])
                            else:
                                rv['used_disks_id'].append(disk['disk_id'])
            else:
                LOG.error(out['stderr'])
        else:
            LOG.error(err)
    else:
        LOG.error(err)
    return rv


def get_all_disks():
    disks = []
    # Block will give all disk and partitons and cdroms details
    cmd = Command({"_raw_params": 'hwinfo --block'})
    out, err = cmd.start()
    if not err:
        if not out['stderr']:
            out = out['stdout']
            all_disks = []
            parents = []
            for blocks in out.split('\n\n'):
                devlist = {"disk_id": "",
                           "parent_id": "",
                           "disk_type": "",
                           "model": "",
                           "vendor": "",
                           "serial_no": "",
                           "device_name": "",
                           "sysfs_id": "",
                           "sysfs_busid": "",
                           "sysfs_device_link": "",
                           "driver_modules": "",
                           "driver": "",
                           "device_files": "",
                           "device_number": "",
                           "device": "",
                           "drive_status": "",
                           "rmversion": "",
                           "bios_id": "",
                           "geo_bios_edd": "",
                           "geo_bios_legacy": "",
                           "geo_logical": ""
                           }
                for line in blocks.split('\n'):
                    if "Unique ID" in line:
                        devlist["disk_id"] = \
                            line.split(':')[1].lstrip()
                    elif "Parent ID" in line:
                        devlist["parent_id"] = \
                            line.split(':')[1].lstrip()
                    elif "Hardware Class" in line:
                        devlist["disk_type"] = \
                            line.split(':')[1].lstrip()
                    elif "Model" in line:
                        devlist["model"] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Vendor" in line:
                        devlist["vendor"] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Serial ID" in line:
                        devlist["serial_no"] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Device File:" in line:
                        devlist["device_name"] = \
                            line.split(':')[1].lstrip()
                    elif "Revision" in line:
                        devlist["rmversion"] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Drive status" in line:
                        devlist["drive_status"] = \
                            line.split(':')[1].lstrip()
                    elif "SysFS ID" in line:
                        devlist["sysfs_id"] = \
                            line.split(':')[1].lstrip()
                    elif "SysFS BusID" in line:
                        devlist["sysfs_busid"] = \
                            line.split(':')[1].lstrip()
                    elif "SysFS Device Link" in line:
                        devlist["sysfs_device_link"] = \
                            line.split(':')[1].lstrip()
                    elif "Driver Modules" in line:
                        driver_modules = \
                            line.split(':')[1].lstrip()
                        devlist["driver_modules"] = \
                            driver_modules.replace('"', "").split(', ')
                    elif "Driver" in line:
                        driver = line.split(':')[1].lstrip()
                        devlist["driver"] = \
                            driver.replace('"', "").split(', ')
                    elif "Device Files" in line:
                        device_files = \
                            line.split(':')[1].lstrip()
                        devlist["device_files"] = \
                            device_files.split(', ')
                    elif "Device Number" in line:
                        devlist["device_number"] = \
                            line.split(':')[1].lstrip()
                    elif "Device" in line:
                        devlist["device"] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "BIOS id" in line:
                        devlist["bios_id"] = \
                            line.split(':')[1].lstrip()
                    elif "Geometry (Logical)" in line:
                        devlist["geo_logical"] = \
                            line.split(':')[1].lstrip()
                    elif "Geometry (BIOS EDD)" in line:
                        devlist["geo_bios_edd"] = \
                            line.split(':')[1].lstrip()
                    elif "Geometry (BIOS Legacy)" in line:
                        devlist["geo_bios_legacy"] = \
                            line.split(':')[1].lstrip()
                if devlist["disk_type"] == "disk":
                    all_disks.append(devlist)
                elif devlist["disk_type"] == "partition":
                    devlist["used"] = True
                    disks.append(devlist)
                    parents.append(devlist["parent_id"])
            for disk in all_disks:
                if not disk["disk_id"] in parents:
                    disk["used"] = False
                    disks.append(disk)
        else:
            err = out['stderr']
    return disks, err


def is_ssd(rotational):
    if rotational == '0':
        return True
    if rotational == '1':
        return False
    """Rotational attribute not found for
    this device which is not either SSD or HD
    """
    return False


def get_node_network():
    """return

           {"interface_name": {"ipv4": ["ipv4address", ...],
                               "ipv6": ["ipv6address, ..."],
                               "netmask": ["subnet", ...],
                               "subnet": "subnet",
                               "status":"up/down",
                               "interface_id": "",
                               "sysfs_id": "",
                               "device_link": "",
                               "interface_type": "",
                               "model": "",
                               "driver_modules": "",
                               "drive": "",
                               "hw_address": "",
                               "link_detected": ""
                              }, ...
           }
    """
    rv = {}
    network_interfaces = get_node_interface()
    cmd = Command({"_raw_params": 'hwinfo --network'})
    out, err = cmd.start()
    if not err:
        if not out['stderr']:
            out = out['stdout']
            for interface in out.split('\n\n'):
                devlist = {"interface_id": "",
                           "sysfs_id": "",
                           "device_link": "",
                           "interface_type": "",
                           "model": "",
                           "driver_modules": "",
                           "drive": "",
                           "interface_name": "",
                           "hw_address": "",
                           "link_detected": ""}
                for line in interface.split('\n'):
                    if "Unique ID" in line:
                        devlist['interface_id'] = \
                            line.split(':')[1].lstrip()
                    elif "SysFS ID" in line:
                        devlist['sysfs_id'] = \
                            line.split(':')[1].lstrip()
                    elif "SysFS Device Link" in line:
                        devlist['device_link'] = \
                            line.split(':')[1].lstrip()
                    elif "Hardware Class" in line:
                        devlist['interface_type'] = \
                            line.split(':')[1].lstrip()
                    elif "Model" in line:
                        devlist['model'] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Driver Modules" in line:
                        devlist['driver_modules'] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Driver" in line:
                        devlist['driver'] = \
                            line.split(':')[1].lstrip().replace('"', "")
                    elif "Device File" in line:
                        devlist['interface_name'] = \
                            line.split(':')[1].lstrip()
                    elif "HW Address" in line:
                        devlist['hw_address'] = \
                            line.split(':')[1].lstrip()
                    elif "Link detected" in line:
                        devlist['link_detected'] = \
                            line.split(':')[1].lstrip()
                if devlist["interface_name"] in network_interfaces:
                    interface_name = devlist["interface_name"]
                    network_interfaces[interface_name].update(devlist)
                    rv[interface_name] = network_interfaces[interface_name]
        else:
            LOG.error(out['stderr'])
    else:
        LOG.error(err)

    return rv


def get_node_interface():
    '''returns structure

    {"interface_name": {"ipv4": ["ipv4address", ...],
                        "ipv6": ["ipv6address", ...]
                        "netmask": ["subnet", ...],
                        "subnet": "subnet",
                        "status":"up/down"},...}
    '''
    interfaces = ni.interfaces()
    rv = {}
    invalid = 'lo'
    for interface in interfaces:
        if interface != invalid:
            IPv4 = []
            IPv6 = []
            netmask = []
            subnet = ""
            status, err = Check_interface_status(interface)
            if err == "":
                if is_ipv4_present(interface):
                    ipv4_addr_list = ni.ifaddresses(interface)[ni.AF_INET]
                    for ipv4_addr_detail in ipv4_addr_list:
                        IPv4.append(ipv4_addr_detail['addr'])
                        netmask.append(ipv4_addr_detail['netmask'])
                    subnet = get_subnet(IPv4[0], netmask[0])
                if is_ipv6_present(interface):
                    ipv6_addr_list = ni.ifaddresses(interface)[ni.AF_INET6]
                    for ipv6_addr_detail in ipv6_addr_list:
                        IPv6.append(ipv6_addr_detail['addr'])
            else:
                LOG.error(err)

            rv[interface] = (
                {
                    "ipv4": IPv4,
                    "ipv6": IPv6,
                    "netmask": netmask,
                    "subnet": subnet,
                    "status": status
                })
    return rv


def is_ipv4_present(interface):
    addr = ni.ifaddresses(interface)
    return ni.AF_INET in addr


def is_ipv6_present(interface):
    addr = ni.ifaddresses(interface)
    return ni.AF_INET6 in addr


def get_subnet(ipv4, netmask):
    cidr = netaddr.IPNetwork('%s/%s' % (ipv4, netmask))
    network = ("%s/%s") % (str(cidr.network), str(cidr).split('/')[-1])
    return network


def Check_interface_status(interface):
    status = ""
    cmd = Command(
        {"_raw_params": "cat /sys/class/net/%s/operstate" % interface})
    out, err = cmd.start()
    if err == "":
        if out["stderr"] == "":
            status = out["stdout"]
        else:
            err = out["stderr"]
    return status, err


def get_node_inventory():
    node_inventory = {}
    cmd = Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    out = out['stdout']

    node_inventory["machine_id"] = out

    node_inventory["node_id"] = mgr_utils.get_local_node_context()

    node_inventory["os"] = getNodeOs()
    node_inventory["cpu"] = getNodeCpu()
    node_inventory["memory"] = getNodeMemory()
    node_inventory["tendrl_context"] = getTendrlContext()
    node_inventory["disks"] = get_node_disks()
    node_inventory["network"] = get_node_network()

    return node_inventory
