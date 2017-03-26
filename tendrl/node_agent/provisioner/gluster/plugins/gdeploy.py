from tendrl.node_agent.provisioner.gluster.provisioner_base import\
    ProvisionerBasePlugin
from tendrl.commons.event import Event
from tendrl.commons.message import Message

try:
    import python_gdeploy.actions
except ImportError:
    Event(
        Message(
            priority="info",
            publisher=NS.publisher_id,
            payload={
                "message": "python-gdeploy is not installed in this node"
            },
            cluster_id=NS.tendrl_context.integration_id,
        )
    )

from python_gdeploy.actions import install_gluster
from python_gdeploy.actions import configure_gluster_service
from python_gdeploy.actions import configure_gluster_firewall
from python_gdeploy.actions import create_cluster
from python_gdeploy.actions import gluster_brick_provision
from python_gdeploy.actions import create_gluster_volume


class GdeployPlugin(ProvisionerBasePlugin):
    def __init__(self):
        ProvisionerBasePlugin.__init__(self)

    def setup_gluster_node(self, hosts, packages=None, repo=None):
        out, err, rc = install_gluster.install_gluster_packages(
            hosts,
            packages,
            repo
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster packages installed successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while installing glusterfs packages"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        out, err, rc = configure_gluster_service.configure_gluster_service(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "glusterd service started successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while starting glusterd service"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        out, err, rc = configure_gluster_firewall.configure_gluster_firewall(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster firewall configured successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while configuring gluster firewall"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True

    def create_gluster_cluster(self, hosts):
        out, err, rc = create_cluster.create_cluster(
            hosts
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster cluster created successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while creating gluster cluster"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True

    def gluster_provision_bricks(self, brick_dictionary, disk_type=None,
                                 disk_count=None, stripe_count=None):
        out, err, rc = gluster_brick_provision.provison_disks(
            brick_dictionary,
            disk_type,
            disk_count,
            stripe_count
        )
        if rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "gluster bricks provisioned successfully"
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
        else:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Error while provisioning gluster bricks"
                        ". Details: %s" % str(out)
                    },
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False
        return True
