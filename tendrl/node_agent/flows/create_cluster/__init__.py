# flake8: noqa

import json
import uuid


from tendrl.node_agent import flows
from tendrl.node_agent.flows.create_cluster.ceph_help import create_ceph


class CreateCluster(flows.NodeAgentBaseFlow):
    def run(self):
        self.pre_run = []
        self.atoms = []
        self.post_run = []

        integration_id = self.parameters['TendrlContext.integration_id']
        tendrl_ns.tendrl_context.integration_id = integration_id
        tendrl_ns.tendrl_context.save()
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if tendrl_ns.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    job = {"integration_id": integration_id,
                           "node_ids": [node],
                           "run": "tendrl.node_agent.flows.SetupSSH",
                           "status": "new",
                           "parameters": new_params,
                           "parent": self.parameters['request_id'],
                           "type": "node"
                           }

                    tendrl_ns.etcd_orm.client.write("/queue/%s" % uuid.uuid4(),
                                               json.dumps(job))

        # TODO Check the jobs are completed
        # only successful nodes will be taken up for cluster creation


        sds_name = self.parameters['sds_type']
        if "ceph" in sds_name.lower():
            create_ceph(tendrl_ns.tendrl_context.integration_id)
