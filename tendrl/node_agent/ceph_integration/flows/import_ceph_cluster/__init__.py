import json
import socket
import uuid

from tendrl.node_agent import flows


def get_package_name(installation_source_type):
    if installation_source_type in ["rpm", "deb"]:
        return "tendrl-ceph-integration"
    else:
        ceph = "git+https://github.com/Tendrl/" \
               "ceph_integration.git@v1.1"
        return ceph


class ImportCephCluster(flows.NodeAgentBaseFlow):
    def run(self):
        cluster_id = self.parameters['Tendrl_context.cluster_id']
        self.parameters['fqdn'] = socket.getfqdn()
        installation_source_type = tendrl_ns.config.data[
            "installation_source_type"
        ]
        self.parameters['Package.pkg_type'] = installation_source_type
        self.parameters['Package.name'] = get_package_name(
            installation_source_type
        )
        with open("/etc/tendrl/ceph-integration/integration_id", "w") as f:
            f.write(cluster_id)
        self.parameters['Node.cmd_str'] = "tendrl-ceph-integration"
        return super(ImportCephCluster, self).run()
