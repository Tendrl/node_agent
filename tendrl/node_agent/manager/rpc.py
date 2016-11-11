import json
import logging
import re
import traceback
import uuid

import etcd
import gevent.event

from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.flows.flow_execution_exception import \
    FlowExecutionFailedError
from tendrl.node_agent.manager.command import Command
from tendrl.node_agent.manager import utils


config = TendrlConfig()
LOG = logging.getLogger(__name__)


class EtcdRPC(object):

    def __init__(self):
        etcd_kwargs = {'port': int(config.get("bridge_common", "etcd_port")),
                       'host': config.get("bridge_common", "etcd_connection")}

        self.client = etcd.Client(**etcd_kwargs)
        node_agent_key = utils.configure_tendrl_uuid()
        cmd = Command({"_raw_params": "cat %s" % node_agent_key})
        out, err = cmd.start()
        self.node_id = out['stdout']

    def _process_job(self, raw_job, job_key):
        # Pick up the "new" job that is not locked by any other bridge
        if raw_job['status'] == "new" and raw_job["type"] == "node":
                raw_job['status'] = "processing"
                # Generate a request ID for tracking this job
                # further by tendrl-api
                req_id = str(uuid.uuid4())
                raw_job['request_id'] = "%s/flow_%s" % (
                    self.node_id, req_id)
                self.client.write(job_key, json.dumps(raw_job))
                LOG.info("Processing JOB %s" % raw_job[
                    'request_id'])
                try:
                    result, err = self.invoke_flow(
                        raw_job['flow'], raw_job
                    )
                except FlowExecutionFailedError as e:
                    LOG.error(e)
                    raise
                if err != "":
                    raw_job['status'] = "failed"
                    LOG.error("JOB %s Failed. Error: %s" % (raw_job[
                        'request_id'], err))
                else:
                    raw_job['status'] = "finished"

                raw_job["response"] = {
                    "result": result,
                    "error": err
                }
                return raw_job, True
        else:
            return raw_job, False

    def _acceptor(self):
        while True:
            jobs = self.client.read("/queue")
            gevent.sleep(2)
            for job in jobs.children:
                executed = False
                raw_job = json.loads(job.value.decode('utf-8'))
                try:
                    raw_job, executed = self._process_job(raw_job, job.key)
                except FlowExecutionFailedError as e:
                    LOG.error("Failed to execute job: %s. Error: %s" % (
                        str(job), str(e)))

                if executed:
                    self.client.write(job.key, json.dumps(raw_job))
                    break

    def run(self):
        self._acceptor()

    def stop(self):
        pass

    def invoke_flow(self, flow_path, job):
        the_flow = None
        flow_path = flow_path.lower().split(".")
        flow_module = flow_path[:-1]
        kls_name = flow_path[-1:]
        if "tendrl" in flow_path and "flows" in flow_path:
            exec("from %s import %s as the_flow" % (flow_module, kls_name))
        return the_flow(job).run()

    def convert_flow_name(self, flow_name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', flow_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class EtcdThread(gevent.greenlet.Greenlet):
    """Present a ZeroRPC API for users

    to request state changes.

    """

    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(EtcdThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()
        self._server = EtcdRPC()

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)

        self._complete.set()
        if self._server:
            self._server.stop()

    def _run(self):

        while not self._complete.is_set():
            try:
                LOG.info("%s run..." % self.__class__.__name__)
                self._server.run()
            except Exception:
                LOG.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)

        LOG.info("%s complete..." % self.__class__.__name__)
