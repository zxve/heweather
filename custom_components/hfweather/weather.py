import logging
from datetime import timedelta, datetime
from homeassistant.core import callback

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature, ATTR_FORECAST_TIME, ATTR_FORECAST_CONDITION, ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW, Forecast, ATTR_FORECAST_HUMIDITY, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_NATIVE_WIND_SPEED
    # ATTR_FORECAST_CONDITION,
    # ATTR_FORECAST_PRECIPITATION,
    # ATTR_FORECAST_TEMP,
    # ATTR_FORECAST_TEMP_LOW,
    # ATTR_FORECAST_TIME,
    # ATTR_FORECAST_WIND_BEARING,
    # ATTR_FORECAST_WIND_SPEED
)
from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    CONF_NAME, PRECIPITATION_MILLIMETERS_PER_HOUR, PRESSURE_HPA, SPEED_KILOMETERS_PER_HOUR, LENGTH_KILOMETERS
)
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    MANUFACTURER, CONDITION_CLASSES, DEFAULT_TIME
)

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    try:
        name = config_entry.data[CONF_NAME]

        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
        _LOGGER.debug("metric: %s", coordinator.data["is_metric"])

        async_add_entities([HfweatherEntity(name, coordinator)], False)
    except Exception as e:
        raise e


class HfweatherEntity(WeatherEntity, CoordinatorEntity):
    """Representation of a weather condition."""

    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_precipitation_unit = PRECIPITATION_MILLIMETERS_PER_HOUR
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = LENGTH_KILOMETERS

    def __init__(self, name, coordinator, location):
        """Initialize the  weather."""
        self._name = name
        self._object_id = 'localweather'
        self.coordinator = coordinator
        self.wdata = coordinator.data["wdata"]
        self._updatetime = None
        self._attr_unique_id = 'localweather_' + location
        self._attr_supported_features = 0
        self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
        self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY

    @property
    def name(self):
        """返回实体的名字."""
        # return '和风天气'
        return self._name

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return self._attr_unique_id

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE
        }

    @property
    def native_dew_point(self):
        """Return the native_dew_point."""
        return self.wdata["dew"]

    @property
    def native_apparent_temperature(self):
        """Return the native_apparent_temperature."""
        return self.wdata["feelslike"]

    @property
    def cloud_coverage(self):
        """Return the cloud_coverage."""
        return self.wdata["cloud"]

    @property
    def native_temperature(self):
        """Return the temperature."""
        return self.wdata["temperature"]

    @property
    def native_temperature_unit(self):
        """Return the unit of measurement."""
        return self._attr_native_temperature_unit

    @property
    def humidity(self):
        """Return the humidity."""
        return self.wdata["humidity"]

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self.wdata["wind_speed"]

    @property
    def wind_bearing(self):
        """Return the wind speed."""
        return self.wdata["wind_bearing"]

    @property
    def native_pressure(self):
        """Return the pressure."""
        return self.wdata["pressure"]

    @property
    def native_visibility(self):
        """Return the visibility."""
        return self.wdata["visibility"]

    @property
    def native_precipitation(self):
        """Return the precipitation."""
        return self.wdata["precipitation"]

    @property
    def condition(self):
        """Return the weather condition."""
        if self._condition:
            match_list = [k for k, v in CONDITION_CLASSES.items() if self.wdata["condition"] in v]
            return match_list[0] if match_list else 'unknown'
        else:
            return 'unknown'

    #    @property
    #    def attribution(self):
    #        """Return the attribution."""
    #        return 'Powered by Home Assistant'

    #    @property
    #    def device_state_attributes(self):
    #        """设置其它一些属性值."""
    #        if self._condition is not None:
    #            return {
    #                ATTR_ATTRIBUTION: ATTRIBUTION,
    #                ATTR_UPDATE_TIME: self._updatetime
    #            }
    async def async_forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast."""
        reftime = datetime.now()

        forecast_data = []
        if self.wdata["forecast"]:
            for entry in self.wdata["forecast"]:
                data_dict = {
                    ATTR_FORECAST_TIME: reftime.isoformat(),
                    ATTR_FORECAST_CONDITION: entry[0],
                    ATTR_FORECAST_NATIVE_TEMP: entry[1],
                    ATTR_FORECAST_NATIVE_TEMP_LOW: entry[2],
                    'text': entry[3]
                }
                reftime = reftime + timedelta(days=1)
                forecast_data.append(data_dict)

        return forecast_data

    async def async_forecast_hourly(self) -> list[Forecast]:
        """Return the daily forecast."""
        reftime = datetime.now()

        forecast_hourly_data = []
        for entry in self.wdata["forecast_hourly"]:
            data_dict = {
                ATTR_FORECAST_TIME: reftime.isoformat(),
                ATTR_FORECAST_CONDITION: entry[0],
                ATTR_FORECAST_NATIVE_TEMP: entry[1],
                ATTR_FORECAST_HUMIDITY: entry[2],
                # "native_precipitation": entry[3],
                ATTR_FORECAST_WIND_BEARING: entry[4],
                ATTR_FORECAST_NATIVE_WIND_SPEED: entry[5],
                "precipitation_probability": entry[6],
                'text': entry[7]
            }

            reftime = reftime + timedelta(hours=1)
            forecast_hourly_data.append(data_dict)

        return forecast_hourly_data

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()
