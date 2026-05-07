from redis import Redis

from edisplay.secrets import get_secret
from edisplay.redis_utils import redis_to_bool


class DevicePresence:
    def __init__(self, ids):
        self.ids = ids
        self.connected = []
        self.changed = []

        r = Redis(host='localhost', port=6379, db=0)
        for id_ in ids:
            if get_secret('Devices')[id_]:
                result = r.get(id_)
                self.connected.append(redis_to_bool(result))
                result = r.get(f'{id_}-Updated')
                self.changed.append(redis_to_bool(result))
    
    def all_connected(self):
        return all(self.connected)

    def any_connected(self):
        return any(self.connected)

    def all_changed(self):
        return all(self.changed)

    def any_changed(self):
        return any(self.changed)

    def is_connected(self, id_):
        try:
            index = self.ids.index(id_)
            return self.connected[index]
        except ValueError:
            return False

    def are_connected(self, ids):
        try:
            result = True
            for id_ in ids:
                index = self.ids.index(id_)
                result = result and self.connected[index]
            return result
        except ValueError:
            return False

    def is_any_connected(self, ids):
        result = []
        for id_ in ids:
            result.append(self.is_connected(id_))
        return any(result)

    def has_changed(self, id_):
        try:
            index = self.ids.index(id_)
            return self.changed[index]
        except ValueError:
            return False

    def have_changed(self, ids):
        try:
            result = True
            for id_ in ids:
                index = self.ids.index(id_)
                result = result and self.changed[index]
            return result
        except ValueError:
            return False


def get_devices_presence():
    return DevicePresence(['id0', 'id1', 'id2'])
