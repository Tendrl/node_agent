import os

from tendrl.commons.atoms import base_atom


class CheckNodeUp(base_atom.BaseAtom):
    def run(self, parameters):
        fqdn = parameters.get("fqdn")
        response = os.system("ping -c 1 " + fqdn)
        # and then check the response...
        if response == 0:
            return True
        else:
            return False
