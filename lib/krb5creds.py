import ctypes
from .krb5 import krb5
import tempfile
import os
import json


class Krb5Creds:
    def __init__(self, logger):
        self.logger = logger
        self.cache = self._setCache()

    def __del__(self):
        self._clearCache(self.cache)

    def modify_principal(self, username):
        if "@" in username:
            user, domain = username.split("@")
            return "%s@%s" % (user, domain.upper())
        else:
            return username

    def init_creds_password(self, username, password, ip=None):
        try:
            principal = self.modify_principal(username)
            krb5.get_init_creds_password(principal, password)
            self.logger.info(
                "init_creds_password: ip = %s user = %s, login good.", ip, principal
            )
            return (
                0,
                "Ваш пароль еще действителен, но его можно изменить при необходимости.",
            )
        except BaseException as e:
            self.logger.error(
                "init_creds_password: ip = %s user = %s error = %s",
                ip,
                principal,
                e.args,
            )
            if (
                e.args[0].find("Preauthentication failed") != -1
                or e.args[0].find("not found in Kerberos database") != -1
                or e.args[0].find("Cannot find KDC for realm") != -1
            ):
                return (1, "Неправильно введен логин или пароль.")
            elif e.args[0].find("Password has expired") != -1:
                return (2, "Ваш пароль истек, придумайте новый.")
            else:
                return (
                    3,
                    "Что-то пошло не так, обратитесь к администратору.",
                )

    def change_password(self, username, password, password_new, ip=None):
        try:
            principal = self.modify_principal(username)
            krb5.change_password(principal, password, password_new)
            self.logger.info(
                "change_password: ip = %s user = %s, the password change good.",
                ip,
                principal,
            )
            return "Пароль успешно изменен."
        except BaseException as e:
            self.logger.error(
                "change_password: ip = %s user = %s error = %s", ip, principal, e.args
            )
            if e.args[0].find("Password change rejected") != -1:
                return "Операция отклонена: новый пароль не соответствует парольной политике."
            elif e.args[0].find("Access denied") != -1:
                return "Операция отклонена: нет прав, обратитесь к администратору."
            else:
                return "Что-то пошло не так, обратитесь к администратору."

    def set_password(self, username, password_new, ip=None):
        try:
            principal = self.modify_principal(username)
            krb5.set_password(principal, password_new)
            self.logger.info(
                "change_password: ip = %s user = %s, the password reset good.",
                ip,
                principal,
            )
            return "Пароль успешно сброшен."
        except BaseException as e:
            self.logger.error(
                "set_password: ip = %s user = %s error = %s", ip, principal, e.args
            )
            if e.args[0].find("Password change rejected") != -1:
                return "Операция отклонена: новый пароль не соответствует парольной политике."
            elif e.args[0].find("Access denied") != -1:
                return "Операция отклонена: нет прав, обратитесь к администратору."
            else:
                return "Что-то пошло не так, обратитесь к администратору."

    def _environ(self, name):
        return os.environ.get(name)

    def _set_environ(self, name, value=None):
        if value is None:
            try:
                del os.environ[name]
            except KeyError:
                pass
        else:
            os.environ[name] = value

    def setConfFile(self, fname):
        self._set_environ("KRB5_CONFIG", fname)

    def _setCache(self, cache=None):
        if cache is None:
            cache = os.path.join(
                tempfile.gettempdir(),
                "krb5_cc_" + next(tempfile._get_candidate_names()),
            )

        self._set_environ("KRB5CCNAME", cache)
        return cache

    def _clearCache(self, cache):
        if os.path.exists(cache):
            os.remove(cache)
        self._set_environ("KRB5CCNAME")
