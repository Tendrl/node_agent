class Generate(object):
    def run(self, parameters):
        data = "[ceph_integration]\n# Path to log file\n"\
               "log_level = DEBUG\n" \
               "log_cfg_path = /etc/tendrl/ceph_integration_logging.yaml"
        file_path = "/etc/tendrl/tendrl.conf"
        parameters.update({"Config.data": data, "Config.file_path": file_path})
        return True
