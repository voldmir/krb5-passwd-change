from .krb5creds import Krb5Creds
from flask import Flask, session
from datetime import timedelta
from .conf import Conf
import os
import logging

from .captcha.image import ImageCaptcha
from random import SystemRandom
import base64


class Base(Flask):
    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)

        self.path_app = os.path.abspath(os.path.dirname(__file__) + "/../")
        self.conf = Conf(self.path_app + os.sep + "settings.ini")

        self.log_file_def = self.path_app + os.sep + self.name + ".log"

        self.krb5_config = self.path_app + os.sep + "krb5.conf"

        self.log_file = self.conf.get_setting_str("logfile", self.log_file_def)
        self.logger_start()

        self.secret_key = str.encode(self.conf.get_setting_str("secret_key"))
        self.config["SESSION_USE_SIGNER"] = (
            self.conf.get_setting_bool("session_use_signer")
            if self.secret_key
            else False
        )
        self.permanent_session_lifetime = timedelta(
            minutes=self.conf.get_setting_int("permanent_session_lifetime", 5)
        )

        self.krb5 = Krb5Creds(self.logger)
        if os.path.exists(self.krb5_config):
            self.krb5.setConfFile(self.krb5_config)

        self.realms = {}
        for key, val in dict(self.conf.get_section("realms")).items():
            for name in [x.strip() for x in val.split(",")]:
                self.realms[name] = key

    def upn_replace(self, login):
        for key, val in self.realms.items():
            if key in login:
                return login.replace(key, val, 1)
        return login

    def logger_start(self):
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s ", "%d-%m-%Y %H:%M:%S"
        )

        fileHandler = logging.FileHandler(self.log_file)
        # fileHandler.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)

    def captcha_generate(self):
        captcha_answer = SystemRandom().randrange(10**4)
        captcha_answer = str(captcha_answer).zfill(4)
        image_generator = ImageCaptcha(width=110, height=38, font_sizes=[30])
        image_data = image_generator.generate(captcha_answer)
        base64_captcha = base64.b64encode(image_data.getvalue()).decode("ascii")
        session["captcha_answer"] = captcha_answer
        return "data:image/jpeg;base64,%s" % base64_captcha
