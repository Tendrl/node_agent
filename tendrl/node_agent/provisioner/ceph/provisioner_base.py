from abc import abstractmethod
import six


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        instance = plugin()
        cls.plugins.append(instance)


@six.add_metaclass(PluginMount)
class ProvisionerBasePlugin(object):

    @abstractmethod
    def install_mon(self, mons):
        raise NotImplementedError()

    @abstractmethod
    def install_osd(self, osds):
        raise NotImplementedError()

    @abstractmethod
    def configure_mon(self, mons):
        raise NotImplementedError()

    @abstractmethod
    def configure_osd(self, osds):
        raise NotImplementedError()

    @abstractmethod
    def task_status(self, task_id):
        raise NotImplementedError()
