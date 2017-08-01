import socket
from tendrl.commons import config as cmn_config
from tendrl.commons.event import Event
from tendrl.commons.flows import BaseFlow
from tendrl.commons.message import Message


class ConfigureCollectd(BaseFlow):

    def configure_plugin(self, plugin_name, plugin_params):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Starting configuration of %s on %s with %s"
                    "as conf parameters" % (
                        plugin_name,
                        NS.node_context.fqdn,
                        plugin_params
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
            )
        )
        self.parameters['Node.cmd_str'] = "config_manager %s '%s'" % (
            plugin_name,
            plugin_params
        )
        self.parameters['fqdn'] = socket.getfqdn()
        super(ConfigureCollectd, self).run()

    def run(self):
        plugins = cmn_config.load_config(
            'node-agent',
            "/etc/tendrl/node-agent/monitoring_plugins.conf.yaml"
        )
        plugins = plugins.get('plugins')
        plugin_params = {
            'graphite_host': self.parameters['graphite_host'],
            'graphite_port': self.parameters['graphite_port'],
            'Service.name': self.parameters['Service.name'],
            'hostname': NS.node_context.fqdn,
            'integration_id': NS.tendrl_context.integration_id
        }
        for node_plugin in plugins.get('node', []):
            self.configure_plugin(node_plugin, plugin_params)
        for cluster_plugin in plugins.get(NS.tendrl_context.sds_name):
            self.configure_plugin(node_plugin, plugin_params)
