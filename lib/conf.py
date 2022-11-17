import configparser
import os


class Conf:

    def __init__(self, file_conf):
        self.file_conf = file_conf
        self.config = configparser.ConfigParser()
        self.get_config()

    def get_config(self):
        if not os.path.exists(self.file_conf):
            self.create_config()
            return
        self.config.read(self.file_conf)

    def create_config(self):
        self.config.add_section("stats")
        self.config.set("stats", "debug_level", "info")

        with open(self.file_conf, "w") as config_file:
            self.config.write(config_file)

    def get_setting_list(self, setting, defualt=[], section='stats'):
        if section in self.config and setting in self.config[section]:
            return [e.strip() for e in self.config[section].get(setting).split(',')] if self.config[section].get(setting) != None else defualt
        else:
            return defualt

    def get_setting_str(self, setting, defualt='', section='stats'):
        if section in self.config and setting in self.config[section]:
            return self.config[section].get(setting, defualt)
        else:
            return defualt

    def get_setting_int(self, setting, defualt=None, section='stats'):
        if section in self.config and setting in self.config[section]:
            return self.config[section].getint(setting, defualt)
        else:
            return defualt

    def get_setting_bool(self, setting, defualt=False, section='stats'):
        if section in self.config and setting in self.config[section]:
            return self.config[section].getboolean(setting, fallback=defualt)
        else:
            return defualt
