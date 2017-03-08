from tendrl.node_agent import flows


class SetupSSH(flows.NodeAgentBaseFlow):
    def run(self):
        prov_node = self.parameters.get("provisioner_node")
        plugin = tendrl_ns.provisioner.get_plugin()

        # The TODO COMMENTED CODE to be added to the main create cluster flow
        # Commmented code WILL BE REMOVED after that
        # node_list = self.parameters['Node[]']
        # node_context = tendrl_ns.node_context.load()
        # if len(node_list) > 1 and "provisioner" in node_context.tags:
        #     # This is the master node for this flow
        #     for node in node_list:
        #         if tendrl_ns.node_context.node_id != node:
        #             new_params = self.parameters.copy()
        #             new_params['Node[]'] = [node]
        #             # create flow for each node in node list except $this
        #             Job(job_id=str(uuid.uuid4()),
        #                 integration_id=integration_id,
        #                 run="tendrl.node_agent.flows.SetupSSH",
        #                 status="new",
        #                 parameters=new_params,
        #                 type="node",
        #                 parent=self.parameters['request_id'],
        #                 node_ids=[node]).save()
        #
        #             Event(
        #                 Message(
        #                     priority="info",
        #                     publisher=tendrl_ns.publisher_id,
        #                     payload={
        #                         "message": "Setup SSH job created on node"
        #                         " %s" % node
        #                     },
        #                     request_id=self.parameters['request_id'],
        #                     flow_id=self.uuid,
        #                     cluster_id=tendrl_ns.tendrl_context.integration_id,
        #                 )
        #             )
        #
        # else:
        plugin.setup(prov_node)
