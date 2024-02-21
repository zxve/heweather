import asyncio
import requests
import json
import datetime
import logging

from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout

from homeassistant.const import CONF_API_KEY
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    CONF_DAILYSTEPS,
    CONF_HOURLYSTEPS,
    CONF_ALERT,
    CONF_API_VERSION,
    CONF_LONGITUDE,
    CONF_LATITUDE,
    CONF_STARTTIME,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER,
)

_LOGGER = logging.getLogger(__name__)
# _LOGGER.info("zxve 000")

PLATFORMS = ["sensor", "weather"]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    try:
        api_key = config_entry.data[CONF_API_KEY]
        location_key = config_entry.unique_id
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        api_version = config_entry.data[CONF_API_VERSION]

        _LOGGER.debug("Using location_key: %s, get forecast: %s", location_key, api_version)

        websession = async_get_clientsession(hass)

        coordinator = HeweatherDataUpdateCoordinator(hass, websession, api_key, api_version, location_key, longitude,
                                                     latitude)
        await coordinator.async_refresh()

        if not coordinator.last_update_success:
            raise ConfigEntryNotReady

        undo_listener = config_entry.add_update_listener(update_listener)

        hass.data[DOMAIN][config_entry.entry_id] = {
            COORDINATOR: coordinator,
            UNDO_UPDATE_LISTENER: undo_listener,
        }

        for component in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, component)
            )

        return True
    except Exception as e:
        raise e


async def async_unload_entry(hass, config_entry):
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    await hass.config_entries.async_reload(config_entry.entry_id)


class HeweatherDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, api_key, api_version, location_key, longitude, latitude):
        self.location_key = location_key
        self.longitude = longitude
        self.latitude = latitude
        self.api_version = api_version
        self.api_key = api_key
        self.is_metric = "metric:v2"
        if hass.config.units is METRIC_SYSTEM:
            self.is_metric = "metric:v2"
        else:
            self.is_metric = "imperial"

        update_interval = (
            datetime.timedelta(minutes=60)
        )
        _LOGGER.debug("Data will be update every %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    # @asyncio.coroutine
    def get_data(self, url):
        json_text = requests.get(url).content
        resdata = json.loads(json_text)
        return resdata

    def get_sensor_location(self):
        lat, lon = self.hass.states.get('sensor.location').state.split(",")
        lat = lat.strip()[1:]
        lon = lon.strip()[:-1]
        return lat, lon

    async def _async_update_data(self):
        try:
            async with timeout(10):
                lat, lon = await self.hass.async_add_executor_job(self.get_sensor_location)
                url = str.format("https://devapi.qweather.com/{}/weather/now?location={},{}&key={}", self.api_version,
                                 lon, lat, self.api_key)
                # json_text = requests.get(url).content
                resdata = await self.hass.async_add_executor_job(self.get_data, url)
                resdata['place'] = f'{lat}/{lon}'
                _LOGGER.info(resdata)
        except (
                ClientConnectorError
        ) as error:
            raise UpdateFailed(error)
        _LOGGER.debug("Requests remaining: %s", url)
        return {**resdata, "location_key": self.location_key, "is_metric": self.is_metric}
