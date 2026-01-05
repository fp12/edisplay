import os
from dataclasses import dataclass, field, fields
from typing import List

import openmeteo_requests
import requests_cache
from retry_requests import retry

from edisplay.secrets import get_config


@dataclass
class MeteoCurrent:
    current: object
    temperature_2m: float = field(init=False)
    precipitation: float = field(init=False)
    rain: float = field(init=False)
    showers: float = field(init=False)
    snowfall: float = field(init=False)
    apparent_temperature: float = field(init=False)
    weather_code: float = field(init=False)

    def __post_init__(self):
        var_counter = 0
        for field_name in [field.name for field in fields(self) if field.name != 'current']:
            setattr(self, field_name, self.current.Variables(var_counter).Value())
            var_counter += 1

    @classmethod
    def get_variables(cls) -> List[str]:
        return [field.name for field in fields(cls) if field.name != 'current']
    
    def __str__(self):
        values = [f'{field.name}={getattr(self, field.name)}' for field in fields(self) if field.name != 'current']
        return self.__class__.__qualname__ + f'({", ".join(values)})'


@dataclass
class MeteoDaily:
    daily: object
    rain_sum: float = field(init=False)
    snowfall_sum: float = field(init=False)

    def __post_init__(self):
        var_counter = 0
        for field_name in [field.name for field in fields(self) if field.name != 'daily']:
            setattr(self, field_name, self.daily.Variables(var_counter).Value())
            var_counter += 1

    @classmethod
    def get_variables(cls) -> List[str]:
        return [field.name for field in fields(cls) if field.name != 'daily']
    
    def __str__(self):
        values = [f'{field.name}={getattr(self, field.name)}' for field in fields(self) if field.name != 'daily']
        return self.__class__.__qualname__ + f'({", ".join(values)})'


def get_info(date_from, date_to):
    cache_session = requests_cache.CachedSession(os.path.join('tmp', '.cache'), expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": get_config('Meteo', 'Latitude'),
        "longitude": get_config('Meteo', 'Longitude'),
        "daily": MeteoDaily.get_variables(),
        "current": MeteoCurrent.get_variables(),
        "timezone": "America/New_York",
        "start_date": date_from,
        "end_date": date_to,
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    meteo_current = MeteoCurrent(response.Current())
    meteo_daily = MeteoDaily(response.Daily())

    return meteo_current, meteo_daily


if __name__ == "__main__":
    meteo_current, meteo_daily = get_info('2025-12-22', '2025-12-22')
    print(meteo_current)
    print(meteo_daily)