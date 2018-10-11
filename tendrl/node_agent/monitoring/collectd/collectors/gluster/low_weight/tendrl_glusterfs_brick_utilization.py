import ast
import collectd
import etcd
import json
import os
import shlex
import socket
import subprocess
from subprocess import Popen
import threading
import traceback

from tendrl_gluster import TendrlGlusterfsMonitoringBase

import utils as tendrl_glusterfs_utils


class TendrlBrickUtilizationPlugin(
    TendrlGlusterfsMonitoringBase
):
    etcd_client = {}

    def __init__(self):
        self.provisioner_only_plugin = False
        TendrlGlusterfsMonitoringBase.__init__(self)
        if not self.etcd_client:
            _etcd_args = dict(
                host=self.CONFIG['etcd_host'],
                port=int(self.CONFIG['etcd_port'])
            )
            etcd_ca_cert_file = self.CONFIG.get("etcd_ca_cert_file")
            etcd_cert_file = self.CONFIG.get("etcd_cert_file")
            etcd_key_file = self.CONFIG.get("etcd_key_file")
            if (
                etcd_ca_cert_file and
                str(etcd_ca_cert_file) != "" and
                etcd_cert_file and
                str(etcd_cert_file) != "" and
                etcd_key_file and
                str(etcd_key_file) != ""
            ):
                _etcd_args.update(
                    {
                        "ca_cert": str(self.CONFIG['etcd_ca_cert_file']),
                        "cert": (
                            str(self.CONFIG['etcd_cert_file']),
                            str(self.CONFIG['etcd_key_file'])
                        ),
                        "protocol": "https"
                    }
                )
            self.etcd_client = etcd.Client(**_etcd_args)

    def get_brick_utilization(self):
        bricks_utilization = {}
        try:
            bricks = self.etcd_client.read(
                '/clusters/%s/Bricks/all/%s' % (
                    self.CONFIG['integration_id'],
                    self.CONFIG['peer_name']
                )
            )
            for brick in bricks.leaves:
                try:
                    brick_data = self.etcd_client.read(
                        "%s/data" % (brick.key)
                    ).value
                    brick_data = json.loads(brick_data)
                    utilizations = bricks_utilization.get(
                        brick_data["vol_name"], []
                    )
                    brick_utilization = brick_data['utilization']
                    brick_utilization['hostname'] = self.CONFIG['peer_name']
                    brick_utilization['brick_path'] = \
                        brick_data["brick_path"].split(":")[-1]
                    utilizations.append(brick_data['utilization'])
                    bricks_utilization[brick_data["vol_name"]] = utilizations
                
                except (
                    ValueError,
                    SyntaxError,
                    etcd.EtcdKeyNotFound, 
                    KeyError,
                    TypeError,
                    AttributeError
                ):
                    _msg = "Unable to fetch brick utilization for "\
                        "integration_id (%s), peer_name  (%s) brick key "\
                        "(%s)" % (
                            self.CONFIG['integration_id'],
                            self.CONFIG['peer_name'],
                            brick.key
                        )
                    collectd.warning(_msg)
                    collectd.warning(traceback.format_exc())
        except etcd.EtcdKeyNotFound:
            _msg = "Unable to fetch bricks utilization for "\
                "integration_id (%s), peer_name  (%s)" % (
                    self.CONFIG['integration_id'],
                    self.CONFIG['peer_name']
                )
            collectd.warning(_msg)
            collectd.warning(traceback.format_exc())
        return bricks_utilization

    def get_metrics(self):
        ret_val = {}
        stats = self.get_brick_utilization()
        for vol, brick_usages in stats.iteritems():
            for brick_usage in brick_usages:
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "utilization.gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('total')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_percent')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_used_percent')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s" \
                    ".thin_pool_meta_data_utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('metadata_used_percent')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "thin_pool_meta_data_utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('metadata_used')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "inode_utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_inode')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "inode_utilization.gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('total_inode')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "inode_utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_percent_inode')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_used')
                t_name = "clusters.%s.volumes.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        vol,
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_size')
                t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                    "gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used')
                t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                    "gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('total')
                t_name = "clusters.%s.nodes.%s.bricks.%s.utilization." \
                    "percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_percent')
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_used_percent')
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "thin_pool_meta_data_utilization.percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('metadata_used_percent')
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "thin_pool_meta_data_utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('metadata_used')
                t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                    "gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_inode')
                t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                    "gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('total_inode')
                t_name = "clusters.%s.nodes.%s.bricks.%s.inode_utilization." \
                    "percent-percent_bytes"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('used_percent_inode')
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.gauge-used"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_used')
                t_name = "clusters.%s.nodes.%s.bricks.%s." \
                    "thin_pool_utilization.gauge-total"
                ret_val[
                    t_name % (
                        self.CONFIG['integration_id'],
                        self.CONFIG['peer_name'].replace(".", "_"),
                        brick_usage.get('brick_path').replace("/", "|")
                    )
                ] = brick_usage.get('thinpool_size')
        return ret_val
