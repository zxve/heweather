import asyncio
import datetime

import logging
from async_timeout import timeout
from homeassistant.const import CONF_API_KEY
import async_timeout
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    CONF_API_VERSION,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER, CONF_LOCATION, CONF_LONGITUDE, CONF_LATITUDE, PLATFORMS,
    CONDITION_CLASSES, DISASTER_LEVEL, CONF_DISASTER_MSG, CONF_DISASTER_LEVEL, CONF_DAILYSTEPS, CONF_HOURLYSTEPS,
    CONF_ALERT, CONF_STARTTIME, TIME_BETWEEN_UPDATES,
)
from .weather import HfweatherEntity

_LOGGER = logging.getLogger(__name__)


# _LOGGER.info("zxve 000")


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True

    # try:
    #     api_key = config_entry.data[CONF_API_KEY]
    #     location = config_entry.data[CONF_LOCATION]
    #     location_key = config_entry.unique_id
    #     longitude = config_entry.data[CONF_LONGITUDE]
    #     latitude = config_entry.data[CONF_LATITUDE]
    #     api_version = config_entry.data[CONF_API_VERSION]
    #     disaster_msg = config_entry.options.get(CONF_DISASTER_MSG, "title")
    #     disaster_level = config_entry.options.get(CONF_DISASTER_LEVEL, 1)
    #     dailysteps = config_entry.options.get(CONF_DAILYSTEPS, 3)
    #     hourlysteps = config_entry.options.get(CONF_HOURLYSTEPS, 24)
    #     alert = config_entry.options.get(CONF_ALERT, True)
    #     starttime = config_entry.options.get(CONF_STARTTIME, 0)
    #
    #     coordinator = HfCoordinator(hass, all_apis, api_key, api_version, location_key, longitude, latitude,
    #                                 dailysteps, hourlysteps, starttime, alert, disaster_msg, disaster_level)
    #     await coordinator.async_refresh()
    #
    #     if not coordinator.last_update_success:
    #         raise ConfigEntryNotReady
    #
    #     undo_listener = config_entry.add_update_listener(update_listener)
    #
    #     hass.data[DOMAIN][config_entry.entry_id] = {
    #         COORDINATOR: coordinator,
    #         UNDO_UPDATE_LISTENER: undo_listener,
    #     }
    #
    #     for component in PLATFORMS:
    #         hass.async_create_task(
    #             hass.config_entries.async_forward_entry_setup(config_entry, component)
    #         )
    #
    #     return True
    # except Exception as e:
    #     raise e


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

# class HfCoordinator(DataUpdateCoordinator):
#     def __init__(self, hass, my_apis, api_key, api_version, location_key, longitude, latitude, dailysteps, hourlysteps,
#                  starttime, alert, disaster_msg, disaster_level):
#         self.hass = hass
#         self.location_key = location_key
#         self.longitude = longitude
#         self.latitude = latitude
#         self.api_version = api_version
#         self.api_key = api_key
#         self.dailysteps = dailysteps
#         self.hourlysteps = hourlysteps
#         self.starttime = starttime
#         self.alert = alert
#         self.disaster_msg = disaster_msg
#         self.disaster_level = disaster_level
#         self.my_apis = my_apis
#         self.is_metric = "metric:v2"
#         if hass.config.units is METRIC_SYSTEM:
#             self.is_metric = "metric:v2"
#         else:
#             self.is_metric = "imperial"
#         super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=TIME_BETWEEN_UPDATES)
#
#     async def _async_update_data(self):
#         try:
#             async with timeout(20):
#                 resdata = await self.my_apis(self.hass, self.api_version, self.longitude, self.latitude, self.api_key,
#                                              self.dailysteps, self.hourlysteps, self.starttime, self.alert,
#                                              self.disaster_msg, self.disaster_level)
#         except Exception as e:
#             raise e
#         return {**resdata, "location_key": self.location_key, "is_metric": self.is_metric}
#
#
# async def all_apis(hass, api_version, longitude, latitude, key, dailysteps, hourlysteps, starttime, alert, disaster_msg,
#                    disaster_level):
#     try:
#         async with timeout(15):
#             wdata = await weather_data_update(api_version, longitude, latitude, key, dailysteps, hourlysteps)
#             wsdata = await weather_sensor_data_update(api_version, longitude, latitude, key, disaster_msg,
#                                                       disaster_level, alert)
#             sdata = await suggestion_data_update(hass, api_version, longitude, latitude, key, alert)
#
#     except Exception as e:
#         raise e
#
#     return {"wdata": wdata, "wsdata": wsdata, "sdata": sdata}
