import etcd
from etcd import Client as client
from mock import MagicMock
import sys
sys.modules['tendrl.node_agent.config'] = MagicMock()
sys.modules['__builtin__.open'] = MagicMock()
from tendrl.node_agent.objects.tendrl_context.atoms.compare \
    import Compare
del sys.modules['tendrl.node_agent.config']
del sys.modules['__builtin__.open']

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Test_compare(object):
    def test_comparision_fails_with_key_not_found(self, monkeypatch):
        parameters = {
            'Tendrl_context.cluster_id':
            '3fa8d55f-774a-4839-a92b-dea9e92cd264',
            'Tendrl_context.sds_name': 'gluster',
            'Tendrl_context.sds_version': '3.8.3',
        }
         
        def mock_etcd_client_read(arg, path):
            raise etcd.EtcdKeyNotFound
        monkeypatch.setattr(client, 'read', mock_etcd_client_read)
         
        assert not Compare().run(parameters)

    def test_comparision_succeeds(self, monkeypatch):
        parameters = {
            'Tendrl_context.sds_name': 'gluster',
            'Tendrl_context.sds_version': '3.8.3',
        }

        def mock_etcd_client_read(arg, path):
            result = {
                'newKey': False,
                'raft_index': 5032433,
                'children': [
                    DotDict({
                        u'createdIndex': 125,
                        u'modifiedIndex': 125,
                        u'value': u'3fa8d55f-774a-4839-a92b-dea9e92cd264',
                        u'key': u'/clusters/3fa8d55f-774a-4839-a92b'
                        '-dea9e92cd264/Tendrl_context/cluster_id'}
                    ),
                    DotDict({
                        u'createdIndex': 126,
                        u'modifiedIndex': 126,
                        u'value': u'gluster',
                        u'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                        'dea9e92cd264/Tendrl_context/sds_name'}
                    ),
                    DotDict({
                        u'createdIndex': 127,
                        u'modifiedIndex': 127,
                        u'value': u'3.8.3',
                        u'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                        'dea9e92cd264/Tendrl_context/sds_version'}
                    )
                ],
                'createdIndex': 125,
                'modifiedIndex': 125,
                'value': None,
                'etcd_index': 4164795,
                'expiration': None,
                'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                'dea9e92cd264/Tendrl_context',
                'ttl': None,
                'action': u'get',
                'dir': True
            }
            return DotDict(result)
        monkeypatch.setattr(client, 'read', mock_etcd_client_read)

        assert Compare().run(parameters)

    def test_comparision_fails_because_of_varying_versions(self, monkeypatch):
        assert True
        parameters = {
            'Tendrl_context.sds_name': 'gluster',
            'Tendrl_context.sds_version': '3.8.3',
        }

        def mock_etcd_client_read(arg, path):
             result = {
                  'newKey': False,
                  'raft_index': 5032433,
                  'children': [
                       DotDict({
                            u'createdIndex': 125,
                            u'modifiedIndex': 125,
                            u'value': u'3fa8d55f-774a-4839-a92b-dea9e92cd264',
                            u'key': u'/clusters/3fa8d55f-774a-4839-a92b'
                            '-dea9e92cd264/Tendrl_context/cluster_id'}
                       ),
                       DotDict({
                            u'createdIndex': 126,
                            u'modifiedIndex': 126,
                            u'value': u'gluster',
                            u'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                            'dea9e92cd264/Tendrl_context/sds_name'}
                       ),
                       DotDict({
                            u'createdIndex': 127,
                            u'modifiedIndex': 127,
                            u'value': u'3.8.5',
                            u'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                            'dea9e92cd264/Tendrl_context/sds_version'}
                       )
                  ],
                  'createdIndex': 125,
                  'modifiedIndex': 125,
                  'value': None,
                  'etcd_index': 4164795,
                  'expiration': None,
                  'key': u'/clusters/3fa8d55f-774a-4839-a92b-'
                  'dea9e92cd264/Tendrl_context',
                  'ttl': None,
                  'action': u'get',
                  'dir': True
             }
             return DotDict(result)
        monkeypatch.setattr(client, 'read', mock_etcd_client_read)

        assert not Compare().run(parameters)
