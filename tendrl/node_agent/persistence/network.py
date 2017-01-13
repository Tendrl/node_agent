import json
import time


class Network(object):
    """A table of the Network, lazily updated

    """
    __name__ = 'nodes/%s/Networks/%s'

    def __init__(self, interface):
        self.updated = str(time.time())
        self.node_id = interface["node_id"]
        self.interface = interface["interface_name"]
        self.interface_id = interface["interface_id"]
        self.ipv4 = interface["ipv4"]
        self.ipv6 = interface["ipv6"]
        self.netmask = interface["netmask"]
        self.subnet = interface["subnet"]
        self.status = interface["status"]
        self.sysfs_id = interface["sysfs_id"]
        self.device_link = interface["device_link"]
        self.interface_type = interface["interface_type"]
        self.model = interface["model"]
        self.driver_modules = interface["driver_modules"]
        self.driver = interface["driver"]
        self.hw_address = interface["hw_address"]
        self.link_detected = interface["link_detected"]

    def to_json_string(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def to_obj(json_str):
        return Network(json.loads(json_str))
