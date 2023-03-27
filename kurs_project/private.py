import json

from django.core.exceptions import ImproperlyConfigured
# https://ru.stackoverflow.com/questions/728740/%d0%9d%d1%83%d0%b6%d0%bd%d0%be-%d0%bb%d0%b8-%d1%83%d0%ba%d0%b0%d0%b7%d1%8b%d0%b2%d0%b0%d1%82%d1%8c-%d0%bf%d0%b0%d1%80%d0%be%d0%bb%d1%8c-%d0%b1%d0%b0%d0%b7%d1%8b-%d0%b4%d0%b0%d0%bd%d0%bd%d1%8b%d1%85-%d0%b2-settings-py-django


class PrivateConfig(object):
    def __init__(self, path):
        self._path = path
        self._check_path()
        self._config = None
        self._read()

    def _check_path(self):
        pass

    def _read(self):
        try:
            with open(self._path) as f:
                self._config = json.loads(f.read())
        except FileNotFoundError:
            raise ImproperlyConfigured(
                "Error opening private config file at '{}'".format(self._path)
            )

    def get(self, key, subkey=None):
        try:
            if subkey is not None:
                return self._config[key][subkey]
            else:
                return self._config[key]
        except KeyError:
            error_msg = "Private JSON-file has not key '{0}''{1}'".format(key, subkey)
            raise ImproperlyConfigured(error_msg)
