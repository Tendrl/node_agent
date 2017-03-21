from tendrl.commons import etcdobj
from tendrl.commons.message import Message as message
from tendrl.commons import objects


class Message(message, objects.BaseObject):
    def __init__(self, **message_arg):
        super(Message, self).__init__(**message_arg)
        self.value = 'Messages/events/%s'
        self._etcd_cls = _MessageEtcd

    def load_definition(self):
        return {}


class _MessageEtcd(etcdobj.EtcdObj):
    """Message object, lazily updated

    """
    __name__ = 'Messages/events/%s'
    _tendrl_cls = Message

    def render(self):
        self.__name__ = self.__name__ % (
            self.message_id
        )
        return super(_MessageEtcd, self).render()
