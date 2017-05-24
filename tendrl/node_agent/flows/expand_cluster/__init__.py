from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.flows.create_cluster import \
    utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message
from tendrl.node_agent.flows.expand_cluster import ceph_help


class ExpandCluster(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")

        supported_sds = NS.compiled_definitions.get_parsed_defs()['namespace.tendrl']['supported_sds']
        sds_name = self.parameters["TendrlContext.sds_name"]
        if sds_name not in supported_sds:
            raise FlowExecutionFailedError("SDS (%s) not supported" % sds_name)

        ssh_job_ids = []
        if "ceph" in sds_name:
            ssh_job_ids = create_cluster_utils.ceph_create_ssh_setup_jobs(
                self.parameters
            )
        else:
            pass

        all_ssh_jobs_done = False
        while not all_ssh_jobs_done:
            all_status = []
            for job_id in ssh_job_ids:
                all_status.append(
                    NS.etcd_orm.client.read("/queue/%s/status" % job_id).value
                )
            if all([status for status in all_status if status == "finished"]):
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id = self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "SSH setup completed for all the nodes"
                        }
                    )
                )
                all_ssh_jobs_done = True

        # SSH setup jobs finished above, now install sds bits and expand cluster
        if "ceph" in sds_name:
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id = self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Expanding ceph cluster %s" % integration_id
                    }
                )
            )
            ceph_help.expand_cluster(self.parameters)
        else:
            pass
