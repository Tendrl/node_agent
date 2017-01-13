from abc import abstractmethod
import six
from tendrl.node_agent.discovery_modules.plugin import PluginMount


@six.add_metaclass(PluginMount)
class PlatformBasePlugin(object):

    @abstractmethod
    def intialize(self):
        raise NotImplementedError()

    @abstractmethod
    def discover_platform(self):
        raise NotImplementedError()
