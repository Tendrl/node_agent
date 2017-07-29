#! /usr/bin/env python

from etcd import Client as etcd_client
from jinja2 import Environment
from jinja2 import FileSystemLoader
import json
import os
import platform
import socket
from sys import argv
from tendrl.commons.config import load_config
from tendrl.commons.utils.service import Service

collectd_os_specifics = {
    'Fedora': {
        'config': '/etc/collectd.conf',
        'moduledirconfig': '/usr/lib64/collectd/',
        'pluginconf': '/etc/collectd.d',
        'socketgroup': 'wheel',
    },
    'centos': {
        'config': '/etc/collectd.conf',
        'pluginconf': '/etc/collectd.d',
        'moduledirconfig': '/usr/lib64/collectd/',
        'socketgroup': 'wheel',
    },
    'redhat': {
        'config': '/etc/collectd.conf',
        'pluginconf': '/etc/collectd.d',
        'moduledirconfig': '/usr/lib64/collectd/',
        'socketgroup': 'wheel',
    },
}[platform.dist()[0]]

TEMPLATE_ROOT = '/etc/collectd_template'


class ConfigManager(object):

    def __init__(self, conf_name, data):
        self.template_path = '%s/%s.jinja' % (TEMPLATE_ROOT, conf_name)
        if conf_name == 'collectd':
            self.config_path = collectd_os_specifics['config']
        else:
            self.config_path = '%s/%s.conf' % (
                collectd_os_specifics['pluginconf'], conf_name)
        self.data = data
        self.data.update(collectd_os_specifics)
        self.data['hostname'] = socket.getfqdn()

    def generate_config_file(self):
        j2_env = Environment(
            loader=FileSystemLoader(
                os.path.dirname(self.template_path)
            )
        )
        template = j2_env.get_template(os.path.basename(self.template_path))
        conf_str = template.render(self.data)
        text_file = open(self.config_path, "w")
        text_file.write("%s\n" % conf_str)
        text_file.close()


def main():
    conf_name = argv[1]
    data = json.loads(argv[2])
    ConfigManager(conf_name, data).generate_config_file()
    config = load_config(
        'node-monitoring',
        '/etc/tendrl/node-monitoring/node-monitoring.conf.yaml'
    )
    central_store = etcd_client(
        host=config['etcd_connection'],
        port=config['etcd_port']
    )
    with open('/etc/machine-id') as f:
        machine_id = f.read().strip('\n')
    node_id = central_store.read(
        '/indexes/machine_id/%s' % machine_id
    ).value
    return Service(
        'collectd',
        publisher_id='node_monitoring',
        node_id=node_id,
        socket_path=config['logging_socket_path'],
        enabled=True
    ).restart()


if __name__ == '__main__':
    main()
