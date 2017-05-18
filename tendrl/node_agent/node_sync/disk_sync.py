from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons.utils import cmd_utils


def get_node_disks():
    rv = {}
    rv["disks"] = []
    rv["free_disks_id"] = {}
    rv["used_disks_id"] = {}
    disks, err = get_all_disks()
    if err == "":
        columns = 'NAME,KNAME,PKNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,' \
                  'UUID,TYPE,' \
                  'RA,RO,RM,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,' \
                  'MIN-IO,OPT-IO,' \
                  'PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,DISC-ALN,' \
                  'DISC-GRAN,DISC-MAX,' \
                  'DISC-ZERO'
        keys = columns.split(',')
        lsblk = (
            "lsblk --all --bytes --noheadings --output='%s' --path --raw" %
            columns)
        cmd = cmd_utils.Command(lsblk)
        out, err, rc = cmd.run()
        if not err:
            devlist = map(
                lambda line: dict(zip(keys, line.split(' '))),
                out.splitlines())
            all_parents = []
            parent_ids = []
            for dev_info in devlist:
                if dev_info['NAME'] in disks.keys():
                    device_name = dev_info['NAME']
                    disks[device_name]['disk_kernel_name'] = dev_info['KNAME']
                    disks[device_name]['parent_name'] = dev_info['PKNAME']
                    disks[device_name]['major_to_minor_no'] = dev_info['MAJ:MIN']
                    disks[device_name]['fstype'] = dev_info['FSTYPE']
                    disks[device_name]['mount_point'] = dev_info['MOUNTPOINT']
                    disks[device_name]['label'] = dev_info['LABEL']
                    disks[device_name]['fsuuid'] = dev_info['UUID']
                    disks[device_name]['disk_type'] = dev_info['TYPE']
                    disks[device_name]['read_ahead'] = dev_info['RA']
                    if dev_info['RO'] == '0':
                        disks[device_name]['read_only'] = False
                    else:
                        disks[device_name]['read_only'] = True
                    if dev_info['RM'] == '0':
                        disks[device_name]['removable_device'] = False
                    else:
                        disks[device_name]['removable_device'] = True
                    disks[device_name]['size'] = dev_info['SIZE']
                    disks[device_name]['state'] = dev_info['STATE']
                    disks[device_name]['owner'] = dev_info['OWNER']
                    disks[device_name]['group'] = dev_info['GROUP']
                    disks[device_name]['mode'] = dev_info['MODE']
                    disks[device_name]['alignment'] = dev_info['ALIGNMENT']
                    disks[device_name]['min_io_size'] = dev_info['MIN-IO']
                    disks[device_name]['optimal_io_size'] = dev_info['OPT-IO']
                    disks[device_name]['phy_sector_size'] = dev_info['PHY-SEC']
                    disks[device_name]['log_sector_size'] = dev_info['LOG-SEC']
                    if disks[device_name]['disk_type'] == "disk":
                        disks[device_name]['ssd'] = is_ssd(dev_info['ROTA'])
                    else:
                        disks[device_name]['ssd'] = False
                    disks[device_name]['scheduler_name'] = dev_info['SCHED']
                    disks[device_name]['req_queue_size'] = dev_info['RQ-SIZE']
                    disks[device_name]['discard_align_offset'] = dev_info[
                        'DISC-ALN']
                    disks[device_name]['discard_granularity'] = dev_info[
                        'DISC-GRAN']
                    disks[device_name]['discard_max_bytes'] = dev_info[
                        'DISC-MAX']
                    disks[device_name]['discard_zeros_data'] = dev_info[
                        'DISC-ZERO']
                    if disks[device_name]['disk_type'] == 'part':
                        disks[device_name]['used'] = True
                        rv['disks'].append(disks[device_name])
                        rv['used_disks_id'][device_name] = disks[device_name]['disk_id']
                            
                    if disks[device_name]['disk_type'] == "disk":
                        all_parents.append(disks[device_name])
                if dev_info['TYPE'] != 'disk':
                    parent_ids.append(dev_info['PKNAME'])
            for parent in all_parents:
                if parent['device_name'] in parent_ids:
                    parent['used'] = True
                    rv['disks'].append(parent)
                    rv['used_disks_id'][parent['device_name']] = parent['disk_id']
                else:
                    parent['used'] = False
                    rv['disks'].append(parent)
                    rv['free_disks_id'][parent['device_name']] = parent['disk_id']
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": str(err)}
                )
            )
    else:
        Event(
            Message(
                priority="error",
                publisher=NS.publisher_id,
                payload={"message": str(err)}
            )
        )
    return rv


def get_all_disks():
    disks = {}
    # Block will give all disk and partitons and cdroms details
    cmd = cmd_utils.Command('hwinfo --block')
    out, err, rc = cmd.run()
    if not err:
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
            disks[devlist['device_name']] = devlist
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
