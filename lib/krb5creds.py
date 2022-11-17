import ctypes
from .krb5 import krb5
import logging


class Krb5Creds():

    def __init__(self, username, password):
        self.principal, self.domain = username.split('@')
        self.principal = '%s@%s' % (self.principal, self.domain.upper())
        self.creds = password

    def init_creds_password(self):
        try:
            logging.debug('KRB5: Authentications start user: %s' %
                          self.principal)
            krb5.get_init_creds_password(self.principal, self.creds)
            logging.debug('KRB5: Authentications end user: %s' %
                          self.principal)
            return (0, "Ok")
        except BaseException as e:
            logging.debug('KRB5: Authentications error user: %s error = %s' % (
                self.principal, e.args))
            if (str(e.args).find("Preauthentication failed") != -1):
                return (1, "KRB5: Preauthentication failed")
            elif (str(e.args).find("Password has expired") != -1):
                return (2, "KRB5: Password has expired")
            elif (str(e.args).find("not found in Kerberos database") != -1):
                return (3, "KRB5: User '%s' not found" % self.principal)
            else:
                return (3, "KRB5: %s" % e.args)

    def change_password(self, password_new):
        try:
            logging.debug('KRB5: Change password start user: %s' %
                          self.principal)
            krb5.change_password(self.principal, self.creds, password_new)
            logging.debug('KRB5: Change password end user: %s' %
                          self.principal)
            return (0, "Ok")
        except BaseException as e:
            logging.debug('KRB5: Authentications error user: %s error = %s' % (
                self.principal, e.args))
            if (str(e.args).find("Password does not meet complexity requirements") != -1):
                return (1, "KRB5: Password does not meet complexity requirements")
            elif (str(e.args).find("Password is already in password history") != -1):
                return (2, "KRB5: Password is already in password history")
            elif (str(e.args).find("Password change rejected, password changes") != -1):
                return (3, "KRB5: Password change rejected, the minimum password age may not have elapsed.")
            else:
                return (4, "KRB5: %s" % e.args)

    def set_password(self, password_new):
        try:
            logging.debug('KRB5: Set password start user: %s' %
                          self.principal)
            krb5.set_password(self.principal, password_new)
            logging.debug('KRB5: Set password end user: %s' %
                          self.principal)
            return (0, "Ok")
        except BaseException as e:
            logging.debug('KRB5: Authentications error user: %s error = %s' % (
                self.principal, e.args))
            return (4, "KRB5: %s" % e.args)
