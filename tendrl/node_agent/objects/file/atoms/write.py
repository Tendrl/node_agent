from tendrl.commons.atoms import base_atom


class Write(base_atom.BaseAtom):
    def run(self):
        data = self.parameters.get("Config.data")
        file_path = self.parameters.get("Config.file_path")
        attributes = {}
        attributes["block"] = data
        attributes["dest"] = file_path
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            with open(file_path, 'w') as f:
                for line in lines:
                    if line.startswith("etcd_connection"):
                        line = "etcd_connection: {}\n".format(
                            self.config["etcd_connection"]
                        )
                    f.write(line)
        except Exception as e:
            raise e
        return True
