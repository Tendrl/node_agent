from tendrl.commons.atoms import base_atom


class Generate(base_atom.BaseAtom):
    def run(self):
        # TODO(rohan) change ini to yaml config and new per component file
        data = "\netcd_connection: {}".format(
            self.config["etcd_connection"]
        )
        file_path = "/etc/tendrl/gluster-integration/" + \
                    "gluster-integration.conf.yaml"
        self.parameters.update({"Config.data": data,
                                "Config.file_path": file_path})
        return True
