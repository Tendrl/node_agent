from mock import MagicMock
import sys
import tempfile
sys.modules['logging'] = MagicMock()
from tendrl.node_agent.manager import utils
del sys.modules['logging']


def test_get_local_node_context():
    myfile = tempfile.NamedTemporaryFile()
    with open(myfile.name, 'w') as f:
         f.write('1234-1234-123456-1234')
    utils.NODE_CONTEXT = myfile.name
    assert utils.get_local_node_context() == '1234-1234-123456-1234'
    utils.delete_local_node_context()



def test_set_local_node_context():
    myfile = tempfile.NamedTemporaryFile()
    utils.NODE_CONTEXT = myfile.name
    node_id = utils.set_local_node_context()
    with open(myfile.name, 'r') as f:
        assert f.read() == node_id
    utils.delete_local_node_context()



def test_get_node_context():
    obj = MagicMock()
    obj.value = "1234-1234-123456-1234"
    utils.get_node_context(obj,"")
    assert obj.value == "1234-1234-123456-1234"