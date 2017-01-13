import pytest
from tendrl.node_agent.discovery_modules.platform import base


class TestBase(object):
    def test_base(self):
        self.obj = base.PlatformBasePlugin()
        with pytest.raises(NotImplementedError):
            self.obj.intialize()
            self.obj.discover_platform()
