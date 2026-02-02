import asyncio
import aiohttp

import redis
from celery import shared_task

from edisplay.secrets import get_secret
from edisplay.redis_utils import redis_to_int, redis_to_bool


class DevicePresence:
    def __init__(self, ids):
        self.ids =  ids
        self.connected = []
        self.changed = []

        r = redis.Redis(host='localhost', port=6379, db=0)
        for id_ in ids:
            if monitored_device := get_secret('Devices')[id_]:
                mac = monitored_device['mac']
                result = r.get(mac)
                self.connected.append(redis_to_bool(result))
                result = r.get(f'{mac}-Updated')
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


async def update_device_presence_impl():
    # lazy imports
    from asusrouter import AsusRouter, AsusData
    from asusrouter.modules.connection import ConnectionState

    async with aiohttp.ClientSession() as session:
        r = redis.Redis(host='localhost', port=6379, db=0)

        router = AsusRouter(
            hostname=get_secret('Router', 'IP'),
            username=get_secret('Router', 'Username'),
            password=get_secret('Router', 'Password'),
            use_ssl=True,
            session=session,
        )

        try:
            debug_msg = 'Device presence: '
            if await router.async_connect():
                all_devices = await router.async_get_data(AsusData.CLIENTS)
                monitored_devices = get_secret('Devices')
                for id_, monitored_device in monitored_devices.items():
                    if monitored_device['monitored'] is True:
                        mac = monitored_device['mac']
                        if device := all_devices.get(mac):
                            # storing status update as well
                            previous = redis_to_int(r.get(mac))
                            connected = 1 if device.state == ConnectionState.CONNECTED else 0
                            updated = 1 if connected != previous else 0
                            r.setex(f'{mac}-Updated', 130, updated)
                            r.setex(mac, 130, connected)
                            debug_msg += f'{id_}: {bool(previous)}>{bool(connected)} | '

            print(debug_msg)

        except Exception as e:
            print(f'update_device_presence raised an Exception: {e}')

        finally:
            await router.async_disconnect()


@shared_task
def update_device_presence():
    asyncio.run(update_device_presence_impl())


def is_device_connected(id_):
    if monitored_device := get_secret('Devices')[id_]:
        r = redis.Redis(host='localhost', port=6379, db=0)
        result = r.get(monitored_device['mac'])
        return redis_to_bool(result)
    return False


def has_device_status_changed_recently(id_):
    if monitored_device := get_secret('Devices')[id_]:
        mac = monitored_device['mac']
        r = redis.Redis(host='localhost', port=6379, db=0)
        result = r.get(f'{mac}-Updated')
        return redis_to_bool(result)
    return False


def are_devices_connected(ids, comp):
    r = redis.Redis(host='localhost', port=6379, db=0)
    results = []
    for id_ in ids:
        if monitored_device := get_secret('Devices')[id_]:
            result = r.get(monitored_device['mac'])
            results.append(redis_to_bool(result))

    return comp(results)


def get_devices_presence(ids):
    return DevicePresence(ids)
