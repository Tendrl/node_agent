import os


class CheckServiceStatus(object):
    def run(self, parameters):
        service_name = parameters.get("Service.name")
        response = os.system("systemctl status %s" % service_name)
        # and then check the response...
        if response == 0:
            return True
        else:
            return False
