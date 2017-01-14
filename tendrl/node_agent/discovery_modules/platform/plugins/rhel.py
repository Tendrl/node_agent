import logging
import platform
from tendrl.node_agent.discovery_modules.platform import base


LOG = logging.getLogger(__name__)


class RHELPlugin(base.PlatformBasePlugin):

    def intialize(self):
        return

    def discover_platform(self):
        osinfo = {}
        os_out = platform.linux_distribution()

        osinfo = {
            'Name': os_out[0],
            'OSVersion': os_out[1],
            'KernelVersion': platform.release()
        }
        return osinfo
