"""初始化"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_API_VERSION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .hf import HfCoordinator

from .const import (
    CONF_ALERT,
    CONF_DAILYSTEPS,
    CONF_HOURLYSTEPS,
    CONF_STARTTIME,
    CONF_INTERVAL,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER,
    CONF_DISASTER_MSG,
    CONF_DISASTER_LEVEL,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

_LOGGER.info("zxve 000")


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """hf setup entry"""
    try:
        hass.data.setdefault(DOMAIN, {})
        api_key = config_entry.data[CONF_API_KEY]
        location_key = config_entry.unique_id
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        api_version = config_entry.data[CONF_API_VERSION]
        dailysteps = config_entry.options.get(CONF_DAILYSTEPS, 7)
        hourlysteps = config_entry.options.get(CONF_HOURLYSTEPS, 24)
        disaster_msg = config_entry.options.get(CONF_DISASTER_MSG, "title")
        disaster_level = config_entry.options.get(CONF_DISASTER_LEVEL, 1)
        alert = config_entry.options.get(CONF_ALERT, True)
        starttime = config_entry.options.get(CONF_STARTTIME, 0)
        interval = config_entry.options.get(CONF_INTERVAL, 10)
        # _LOGGER.debug("Using location_key: %s, get forecast: %s", location_key, api_version)
        websession = async_get_clientsession(hass)
        coordinator = HfCoordinator(
            hass,
            websession,
            api_key,
            api_version,
            location_key,
            longitude,
            latitude,
            dailysteps,
            hourlysteps,
            disaster_msg,
            disaster_level,
            alert,
            starttime,
            interval,
        )
        await coordinator.async_config_entry_first_refresh()
        undo_listener = config_entry.add_update_listener(update_listener)
        hass.data[DOMAIN][config_entry.entry_id] = {
            COORDINATOR: coordinator,
            UNDO_UPDATE_LISTENER: undo_listener,
        }
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

        return True
    except Exception as e:
        _LOGGER.info("init setup entry: %s", e)
        raise e


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)
