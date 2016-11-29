from tendrl.node_agent.persistence.network import Network


class TestNetwork(object):
    def setup_method(self, method):
        interface = {"ipv4": ["10.70.1.1"],
                     "ipv6": "",
                     "netmask": ["255.255.1.1"],
                     "subnet": "",
                     "status": "up",
                     "interface_id": "",
                     "sysfs_id": "",
                     "device_link": "",
                     "interface_type": "",
                     "model": "",
                     "driver_modules": "",
                     "driver": "",
                     "interface_name": "",
                     "hw_address": "",
                     "link_detected": ""
                     }
        self.network = Network(interface)
        result = self.network.to_json_string()
        result_obj = self.network.to_obj(result)
        assert isinstance(result_obj, Network)
