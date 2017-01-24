import logging
from tendrl.commons.message import Message


LOG = logging.getLogger(__name__)


class Logger(object):
    logger_priorities = {"notice": "info",
                         "info": "info",
                         "error": "error",
                         "debug": "debug",
                         "warning": "warning",
                         "critical": "critical"
                         }
    def __init__(self, message):
        self.message = message
        self.push_messages()
        if "request_id" in message.payload:
            """ If request_id is present then

            it is considered as operation
            """
            self._logger(self.push_operation())
        else:
            self._logger(self.message.payload["message"])

    def push_operation(self):
        tendrl_ns.etcd_orm.client.write(
            self.message.payload["request_id"],
            Message.to_json(self.message),
            append=True)
        log_message = ("%s:%s") % (
            self.message.payload["request_id"],
            self.message.payload["message"])
        return log_message

    def push_messages(self):
        if self.message.priority not in [
            Message.priorities.INFO, Message.priorities.DEBUG]:
            # Stroring messages cluster wise
            if "cluster_id" in self.message.payload:
                tendrl_ns.etcd_orm.client.write(
                    ("clusters/%s/Messages/%s") % (
                        self.message.payload["cluster_id"],
                        self.message.message_id),
                    Message.to_json(self.message)
                )
            # storing messages node wise
            else:
                tendrl_ns.etcd_orm.client.write(
                    ("nodes/%s/Messages/%s") % (
                        self.message.node_id,
                        self.message.message_id),
                    Message.to_json(self.message)
                )
            # storing messages global wise
            tendrl_ns.etcd_orm.client.write(
                ("Messages/%s") % (
                    self.message.message_id),
                Message.to_json(self.message)
            )

    def _logger(self, log_message):
        # Invalid message
        if isinstance(log_message, Message):
            log_message = Message.to_json(log_message)
        message = ("%s - %s - %s:%s - %s - %s - %s") % (
            self.message.timestamp,
            self.message.publisher,
            self.message.caller["filename"],
            self.message.caller["line_no"],
            self.message.caller["function"],
            self.message.priority.upper(),
            log_message
        )
        try:
            method = getattr(LOG, Logger.logger_priorities[self.message.priority])
        except AttributeError:
            raise NotImplementedError(self.message.priority)
        method(message)
