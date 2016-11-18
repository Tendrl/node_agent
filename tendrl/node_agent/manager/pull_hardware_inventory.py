from command import Command
import platform
import socket
import uuid

from tendrl.node_agent.manager import utils as mgr_utils


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


def getNodeDisk():
    '''returns structure

    {"nodename": [{"DevName":   "devicename",
                  "FSType":     "fstype",
                  "FSUUID":     "uuid",
                  "Model":      "model",
                  "MountPoint": ["mountpoint", ...],
                  "Name":       "name",
                  "Parent":     "parentdevicename",
                  "Size":       uint64,
                  "Type":       "type",
                  "Used":       boolean,
                  "SSD":        boolean,
                  "Vendor":     "string",
                  "DiskId":     "uuid"}, ...], ...}
    '''
    devlist = {}
    dev_info = {}
    rv = []
    columes = 'NAME,KNAME,FSTYPE,MOUNTPOINT,UUID,PARTUUID,MODEL,SIZE,TYPE,' \
              'PKNAME,VENDOR'
    keys = columes.split(',')
    lsblk = ("lsblk --all --bytes --noheadings --output='%s' --path --raw" %
             columes)
    cmd = Command({"_raw_params": lsblk})
    out, err = cmd.start()
    if out:
        devlist = map(lambda line: dict(zip(keys, line.split(' '))),
                      out['stdout'].splitlines())
        parents = set([d['PKNAME'] for d in devlist if 'PKNAME' in d])
        for d in devlist:
            in_use = True
            if d['TYPE'] not in ['disk', 'part']:
                continue
            if d['TYPE'] == 'disk':
                if d['KNAME'] in parents:
                    # skip it
                    continue
                else:
                    in_use = False
            elif not d['FSTYPE']:
                in_use = False

            d.update({'INUSE': in_use})
            dev_info.update({d['KNAME']: d})

    for disk in dev_info.values():
        try:
            u = list(bytearray(uuid.UUID(disk["UUID"]).get_bytes()))
        except ValueError:
            # TODO(log the error)
            u = [0] * 16
        if disk['TYPE'] == 'disk':
            ssdStat = isSSD(disk['KNAME'])
        else:
            ssdStat = False
        if disk["SIZE"] == "":
                continue
        rv.append({"DevName": disk["KNAME"],
                   "FSType": disk["FSTYPE"],
                   "FSUUID": u,
                   "Model": disk["MODEL"],
                   "MountPoint": [disk["MOUNTPOINT"]],
                   "Name": disk["NAME"],
                   "Parent": disk["PKNAME"],
                   "Size": long(disk["SIZE"]),
                   "Type": disk["TYPE"],
                   "Used": disk["INUSE"],
                   "SSD": ssdStat,
                   "Vendor": disk.get("VENDOR", ""),
                   "DiskId": u})
    return rv


def isSSD(device):
    temp = 'cat /sys/block/%s/queue/rotational' % device.split("/")[-1]
    cmd = Command({"_raw_params": temp})
    out, err = cmd.start()
    if not out:
        # Log the error
        raise Exception("Failed to get cluster statistics")
    if out == '0':
        return True
    if out == '1':
        return False
    """Rotational attribute not found for

    this device which is not either SSD or HD
    """
    return False


def get_node_inventory():
    node_inventory = {}

    cmd = Command({"_raw_params": "cat /etc/machine-id"})
    out, err = cmd.start()
    out = out['stdout']

    node_inventory["machine_id"] = out

    node_inventory["node_id"] = mgr_utils.get_node_context()

    node_inventory["os"] = getNodeOs()
    node_inventory["cpu"] = getNodeCpu()
    node_inventory["memory"] = getNodeMemory()
    node_inventory["tendrl_context"] = getTendrlContext()
    node_inventory["disk"] = getNodeDisk()

    return node_inventory
