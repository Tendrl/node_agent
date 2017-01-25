import json
import socket
import uuid

from tendrl.node_agent import flows
from tendrl.node_agent.gluster_integration.flows.import_gluster_cluster import ImportGlusterCluster
from tendrl.node_agent.ceph_integration.flows.import_ceph_cluster import ImportCephCluster


class ImportCluster(flows.NodeAgentBaseFlow):
    def run(self):
        curr_node_id = tendrl_ns.node_context.node_id
        cluster_id = self.parameters['cluster_id']
        node_list = self.parameters['cluster_nodes[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if curr_node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                    # create same flow for each node in node list except $this
                    job = {"cluster_id": cluster_id,
                           "node_ids": [node],
                           "run": self.name, "status": "new", "parameters":
                               new_params, "parent": self.job['request_id'],
                           "type": "node"}
                    if "etcd_orm" in job['parameters']:
                        del job['parameters']['etcd_orm']
                    if "manager" in job['parameters']:
                        del job['parameters']['manager']

                    self.etcd_orm.client.write("/queue/%s" % uuid.uuid4(),
                                               json.dumps(job))
        if curr_node_id in node_list:
            if parameters["cluster_type"] == "ceph":
                return super(ImportCephCluster, self).run()
            if parameters["cluster_type"] == "gluster":
                return super(ImportGlusterCluster, self).run()
