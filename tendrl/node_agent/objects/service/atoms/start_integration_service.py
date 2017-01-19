from tendrl.commons.atoms import base_atom
from tendrl.commons.utils \
    import service


class StartIntegrationService(base_atom.BaseAtom):
    def run(self):
        # write the cluster_id to cluster_id file
        if self.parameters.get("Tendrl_context.sds_name") == "gluster":
            cluster_id_path = "/etc/tendrl/gluster-integration/tendrl_context"
        elif self.parameters.get("Tendrl_context.sds_name") == "ceph":
            cluster_id_path = "/etc/tendrl/ceph-integration/tendrl_context"
        else:
            return False
        try:
            with open(cluster_id_path, "w") as f:
                f.write(self.parameters.get("Tendrl_context.cluster_id"))
        except IOError:
            # TODO(darshan) log here
            return False

        # start service
        service_name = "tendrl-" + self.parameters.get(
            "Tendrl_context.sds_name") + "d"
        s = service.Service(
            service_name,
            self.config['tendrl_ansible_exec_file']
        )
        message, success = s.start()
        # TODO(darshan) log here
        return success
