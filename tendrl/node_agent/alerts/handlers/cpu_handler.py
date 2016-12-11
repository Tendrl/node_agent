from tendrl.node_agent.alerts.base_alert_handler import AlertHandler


class CpuHandler(AlertHandler):
    def __init__(self):
        AlertHandler.__init__(self)
        self.handles = 'cpu'
