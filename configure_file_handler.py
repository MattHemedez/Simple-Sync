from pathlib import Path
import json


CONF_FILE_PATH = Path("conf.json")


class ConfigurationHandler:
    def __init__(self):
        self.conf = dict()
        try:
            if self.conf_file_exists():
                self.read_conf()
            else:
                self.init_conf()
        except json.decoder.JSONDecodeError:
            self.init_conf()

    def init_conf(self):
        self.conf = {"file_dir_path": Path("files/").resolve()}
        self.save_conf()

    def conf_file_exists(self):
        return CONF_FILE_PATH.exists()

    def get_conf_entry(self, key):
        return self.conf[key]

    def change_conf_entry(self, conf_key: str, conf_value):
        if conf_key in self.conf:
            self.conf[conf_key] = conf_value
        else:
            raise KeyError(conf_key)

    def save_conf(self):
        with open(CONF_FILE_PATH, "w") as conf_file:
            json.dump(self.conf, conf_file)

    def read_conf(self):
        with open(CONF_FILE_PATH, "r") as conf_file:
            self.conf = json.load(conf_file)


if __name__ == "__main__":
    conf_handler = ConfigurationHandler()
    print("File Directory Path: ", Path(conf_handler.get_conf_entry("file_dir_path")).resolve())
