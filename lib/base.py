
import os
import logging
from lib.conf import Conf
from flask import Flask
import datetime


class Base(Flask):
    def __init__(self, *args, **kwargs):

        self.path_app = kwargs.pop('path_app')

        Flask.__init__(self, *args, **kwargs)

        self.file_conf = self.path_app + os.sep + 'settings.ini'
        self.log_file_def = self.path_app + os.sep + \
            os.path.basename(__file__) + '.log'
        self.conf = Conf(self.file_conf)
        self.logger_start()

        self.secret_key = b'9ebd5625be90386df3b476e3a38006ff'
        self.config['SESSION_USE_SIGNER'] = True
        self.permanent_session_lifetime = datetime.timedelta(minutes=5)

    def logger_start(self):
        l = self.conf.get_setting_str('debug_level')
        if l == 'critical':
            level = logging.CRITICAL
        elif l == 'error':
            level = logging.ERROR
        elif l == 'warning':
            level = logging.WARNING
        elif l == 'info':
            level = logging.INFO
        elif l == 'debug':
            level = logging.DEBUG
        else:
            level = logging.NOTSET

        logging.basicConfig(filename=self.conf.get_setting_str('logfile', self.log_file_def),
                            level=level, format='[%(asctime)s] %(levelname)s: %(message)s ', datefmt='%d-%b-%y %H:%M:%S')
