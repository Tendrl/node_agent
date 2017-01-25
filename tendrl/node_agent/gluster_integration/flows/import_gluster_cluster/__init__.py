import json
import socket
import uuid

from tendrl.node_agent import flows


def get_package_name(installation_source_type):
    if installation_source_type in ["rpm", "deb"]:
        return "tendrl-gluster-integration"
    else:
        gluster = "git+https://github.com/Tendrl/" \
                  "gluster_integration.git@v1.1"
        return gluster


class ImportGlusterCluster(flows.NodeAgentBaseFlow):
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
        with open("/etc/tendrl/gluster-integration/integration_id", "w") as f:
            f.write(cluster_id)
        self.parameters['Node.cmd_str'] = "tendrl-gluster-integration"
        return super(ImportGlusterCluster, self).run()
