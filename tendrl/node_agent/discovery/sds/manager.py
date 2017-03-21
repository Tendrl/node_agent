import importlib
import inspect
import logging
import os
import sys

from tendrl.node_agent.discovery.sds.discover_sds_plugin \
    import DiscoverSDSPlugin


LOG = logging.getLogger(__name__)


class SDSDiscoveryManager(object):
    def __init__(self):
        try:
            self.load_plugins()
        except (SyntaxError, ValueError, ImportError) as ex:
            raise ValueError('SDSDiscoveryManager init failed %s', ex)

    def load_plugins(self):
        try:
            # Find the path from where to load the plugins
            # The path would be tendrl/node_agent/discovery/sds/plugins
            # TODO(team) Needs re-factoring
            path = os.path.dirname(
                os.path.abspath(
                    sys.modules['tendrl.node_agent.manager'].__file__
                )
            ) + '/../discovery/sds/plugins'
            pkg = 'tendrl.node_agent.discovery.sds.plugins'
            # Loop through the list of files in said path and find
            # out all the file names without extension (.py)
            # Then import all the modules one by one
            for py in [f[:-3] for f in os.listdir(path)
                       if f.endswith('.py') and f != '__init__.py']:
                plugin_name = '.'.join([pkg, py])
                mod = importlib.import_module(plugin_name)
                clsmembers = inspect.getmembers(mod, inspect.isclass)
                for name, cls in clsmembers:
                    exec("from %s import %s" % (plugin_name, name))
        except (SyntaxError, ValueError, ImportError) as ex:
            LOG.error("Failed to load SDS detection plugins. Error %s", ex,
                      exc_info=True)
            raise ex

    def get_available_plugins(self):
        return DiscoverSDSPlugin.plugins
