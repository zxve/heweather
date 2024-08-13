'''
weather platform配置
'''
import logging
from datetime import datetime, timedelta
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast, WeatherEntity,
    WeatherEntityFeature,
)

from homeassistant.const import (
    # ATTR_ATTRIBUTION,
    CONF_NAME,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux
)

from homeassistant.helpers.device_registry import DeviceEntryType

from .const import (
    ATTRIBUTION, CONDITION_CLASSES, COORDINATOR, DOMAIN, MANUFACTURER, TIME_BETWEEN_UPDATES
)

# PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)
# SCAN_INTERVAL = timedelta(seconds=TIME_BETWEEN_UPDATES)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """weather setup entry"""

    try:
        name = config_entry.data[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
        async_add_entities([HfweatherEntity(name, coordinator)], update_before_add=True)

    except Exception as e:
        _LOGGER.info("hew- weather setup entry: %s", e)
        raise e


class HfweatherEntity(WeatherEntity):
    """Representation of a weather condition."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    # _attr_supported_features = (
    #     WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
    #     # | WeatherEntityFeature.FORECAST_TWICE_DAILY
    # )

    def __init__(self, name, coordinator):
        """Initialize the  weather."""
        self._name = name
        self._object_id = 'localweather'
        self.wdata = coordinator.data["wdata"]
        self.coordinator = coordinator
        _LOGGER.info("hew- coordinator:%s", coordinator.data)
        self._updatetime = self.wdata["updatetime"]
        self._attr_unique_id = coordinator.data["location_key"]
        self._attr_supported_features = 0
        self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
        self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY

    @property
    def name(self):
        """返回实体的名字."""
        # return '和风天气'
        return self._name

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

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
        if self.wdata["condition"]:
            match_list = [k for k, v in CONDITION_CLASSES.items() if self.wdata["condition"] in v]
            return match_list[0] if match_list else 'unknown'
        else:
            return 'unknown'

    # @property
    # def device_state_attributes(self):
    #     """设置其它一些属性值."""
    #     if self._condition is not None:
    #         return {
    #             ATTR_ATTRIBUTION: ATTRIBUTION,
    #             ATTR_UPDATE_TIME: self._updatetime
    #         }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        # await self.async_update_listeners({"daily", "hourly"})

    async def update_from_client(self):
        """update client"""
        self.async_write_ha_state()

    async def async_update(self):
        """Update Colorfulclouds entity."""
        await self.coordinator.async_request_refresh()
        # self.async_write_ha_state()

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
                reftime += timedelta(days=1)
                forecast_data.append(data_dict)

        _LOGGER.info("hew- forecast_data:%s", forecast_data)
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

            reftime += timedelta(hours=1)
            forecast_hourly_data.append(data_dict)

        _LOGGER.info("hew- forecast_hourly_data:%s", forecast_hourly_data)

        return forecast_hourly_data
