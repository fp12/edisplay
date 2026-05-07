import asyncio
import aiohttp

from redis import Redis
from celery import shared_task

from edisplay.secrets import get_secret
from edisplay.redis_utils import redis_to_int
from edisplay.logging_config import network_presence_logger as logger


CONNECTION_EXPIRATION = 900  # 15min


async def update_device_presence_impl():
    from asusrouter import AsusRouter, AsusData
    from asusrouter.modules.connection import ConnectionState

    max_retries = 3
    retry_delay = 5  # seconds

    async with aiohttp.ClientSession() as session:
        r = Redis(host='localhost', port=6379, db=0)

        router = AsusRouter(
            hostname=get_secret('Router', 'IP'),
            username=get_secret('Router', 'Username'),
            password=get_secret('Router', 'Password'),
            use_ssl=True,
            session=session,
        )

        for attempt in range(max_retries):
            try:
                if await router.async_connect():
                    if all_devices := await router.async_get_data(AsusData.CLIENTS):
                        debug_msg = 'Device presence: '
                        monitored_devices = get_secret('Devices')
                        for id_, monitored_device in monitored_devices.items():
                            if monitored_device['monitored'] is True:
                                previous = redis_to_int(r.get(id_))
                                connected = False

                                for mac in monitored_device['mac']:
                                    if device := all_devices.get(mac):
                                        connected = connected or device.state == ConnectionState.CONNECTED
                                    else:
                                        logger.warning(f'Unregistered device {id_} with mac {mac}')

                                connected = int(connected)
                                updated = 1 if connected != previous else 0
                                r.setex(f'{id_}-Updated', CONNECTION_EXPIRATION, updated)
                                r.setex(id_, CONNECTION_EXPIRATION, connected)
                                debug_msg += f'{id_}: {bool(previous)}>{bool(connected)} | '
                        logger.info(debug_msg)
                    else:
                        logger.warning('Could not devices list from router')

                break  # exit retry loop

            except Exception as e:
                logger.warning(f'update_device_presence raised an Exception: {e}')
                if attempt == max_retries - 1:
                    raise  # let owning task handle it

            finally:
                await router.async_disconnect()
                
                tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                for task in tasks:
                    task.cancel()
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.25)
            
            logger.warning(f'Retrying. Attempt {attempt}/{max_retries}.')
            await asyncio.sleep(retry_delay)


@shared_task
def update_device_presence(ignore_result=True):
    try:
        asyncio.run(update_device_presence_impl())
    except Exception as exc:
        logger.error(f'update_device_presence failed: {exc}')
