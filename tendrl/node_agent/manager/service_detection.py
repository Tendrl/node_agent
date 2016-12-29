from command import Command
import logging
import psutil
from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.manager import utils as mgr_utils

config = TendrlConfig()
LOG = logging.getLogger(__name__)

NAMES=["httpd", "glusterd", "sshd", "tendrl-node-agent"]

class Service(object):

    def __init__(self):
        self.names = NAMES

    def put(self, names):
        # This can be used to set the names externally
        self.names = names

    def get_details(self):
        '''returns structure
        {"name":           "Service Name",
        "command":        "Execution Script",
        "exe_path":       "Execution Path",
        "status":         "Service Status",
        "cpu_usage_per":  "Cpu Usage Percentage",
        "mem_msage_per":  "Memory Usage Percentage",
        "fds_count":      "FDs Count",
        "threads_count":  "Number of Threads",
        "open_files_cnt": "Number of open files"}
        '''

        services = []
        rv = {}
        try:
            pDet = [psutil.Process(p) for p in psutil.get_pid_list() \
                    if psutil.Process(p).name() in self.names]
        except psutil.NoSuchProcess as e:
            # Process state changed during verification
            # Can be simply ignored.
            pass

        for p in pDet:
            if p.name() not in rv:
                rv[p.name()] = {"name":           p.name(),
                                "command":        p.cmdline()[-1],
                                "exe_path":       p.exe(),
                                "status":         p.status(),
                                "cpu_usage_per":  p.cpu_percent(),
                                "mem_usage_per":  p.get_memory_percent(),
                                "fds_count":      p.num_fds(),
                                "threads_count":  p.num_threads(),
                                "open_files_cnt": len(p.open_files())}
            else:
                rv[p.name()]["cpu_usage_per"] += p.cpu_percent()
                rv[p.name()]["mem_usage_per"] += p.get_memory_percent()
                rv[p.name()]["fds_count"] += p.num_fds()
                rv[p.name()]["threads_count"] += p.num_threads()
                rv[p.name()]["open_files_cnt"] += len(p.open_files())
        return [rv[service] for service in rv]

    # TODO: Add function to find the reason for stopped service
    # Whether its not enabled or any other reason
