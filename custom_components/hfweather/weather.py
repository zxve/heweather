import logging
import aiohttp

from datetime import timedelta, datetime
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature, ATTR_FORECAST_TIME, ATTR_FORECAST_CONDITION, ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW, Forecast, ATTR_FORECAST_HUMIDITY, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_NATIVE_WIND_SPEED
)
from homeassistant.const import (
    CONF_NAME, UnitOfVolumetricFlux, UnitOfPressure, UnitOfSpeed, UnitOfLength, UnitOfTemperature, ATTR_ATTRIBUTION,
)
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    MANUFACTURER, CONDITION_CLASSES, CONF_LOCATION, CONF_API_KEY, CONF_API_VERSION, CONF_LONGITUDE, CONF_LATITUDE,
    CONF_DAILYSTEPS, CONF_HOURLYSTEPS, TIME_BETWEEN_UPDATES
)

# PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    try:
        name = config_entry.data[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        _LOGGER.debug("metric: %s", coordinator.data["is_metric"])

        async_add_entities([HfweatherEntity(name, coordinator)], False)

        name = config_entry.data[CONF_NAME]
        location = config_entry.data[CONF_LOCATION]
        location_key = config_entry.unique_id
        api_key = config_entry.data[CONF_API_KEY]
        api_version = config_entry.data[CONF_API_VERSION]
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        dailysteps = config_entry.options.get(CONF_DAILYSTEPS, 3)
        hourlysteps = config_entry.options.get(CONF_HOURLYSTEPS, 24)

        wdata = await weather_data_update(api_version, longitude, latitude, api_key, dailysteps, hourlysteps)
        async_track_time_interval(hass, weather_data_update, TIME_BETWEEN_UPDATES)

        async_add_entities([HfweatherEntity(name, {"location_key": location_key, "wdata": wdata})], False)

    except Exception as e:
        raise e


class HfweatherEntity(CoordinatorEntity, WeatherEntity):
    """Representation of a weather condition."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS

    def __init__(self, name, coordinator):
        """Initialize the  weather."""
        _LOGGER.info("zxve 000")
        self._name = name
        self._object_id = 'localweather'
        self.coordinator = coordinator
        self.wdata = coordinator.data["wdata"]
        _LOGGER.info(self.coordinator.data)
        self._updatetime = self.wdata["updatetime"]
        self._attr_unique_id = coordinator.data["location_key"]
        self._attr_supported_features = 0
        self._attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
        self._attr_supported_features |= WeatherEntityFeature.FORECAST_HOURLY
        super().__init__(coordinator, context=None)

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
        if self.wdata["condition"]:
            match_list = [k for k, v in CONDITION_CLASSES.items() if self.wdata["condition"] in v]
            return match_list[0] if match_list else 'unknown'
        else:
            return 'unknown'

    #    @property
    #    def attribution(self):
    #        """Return the attribution."""
    #        return 'Powered by Home Assistant'

    # @property
    # def device_state_attributes(self):
    #     """设置其它一些属性值."""
    #     if self._condition is not None:
    #         return {
    #             ATTR_ATTRIBUTION: ATTRIBUTION,
    #             ATTR_UPDATE_TIME: self._updatetime
    #         }

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     self._attr_condition = "多云"

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

        return forecast_hourly_data


async def weather_data_update(api_version, longitude, latitude, key, dailysteps, hourlysteps):
    forecast_url = f"https://devapi.qweather.com/{api_version}/weather/{dailysteps}d?location={longitude},{latitude}&key={key}"
    weather_now_url = f"https://devapi.qweather.com/{api_version}/weather/now?location={longitude},{latitude}&key={key}"
    forecast_hourly_url = f"https://devapi.qweather.com/{api_version}/weather/{hourlysteps}h?location={longitude},{latitude}&key={key}"
    params = {"location": f"{longitude}/{latitude}", "key": key}
    data = {}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(weather_now_url) as response:
                json_data = await response.json()
                weather = json_data["now"]
            async with session.get(forecast_url) as response:
                json_data = await response.json()
                forecast = json_data
            async with session.get(forecast_hourly_url) as response:
                json_data = await response.json()
                forecast_hourly = json_data

    except Exception as e:
        raise e

    data["temperature"] = float(weather["temp"])
    data["humidity"] = float(weather["humidity"])
    data["pressure"] = weather["pressure"]
    data["condition"] = weather["text"]
    data["wind_speed"] = weather["windSpeed"]
    data["wind_bearing"] = weather["windDir"]
    data["visibility"] = weather["vis"]
    data["precipitation"] = float(weather["precip"])

    data["feelslike"] = float(weather["feelsLike"])
    data["dew"] = float(weather["dew"])
    data["cloud"] = int(weather["cloud"])

    data["windScale"] = weather["windScale"]
    data["updatetime"] = weather["obsTime"]

    datemsg = forecast["daily"]

    # forec_cond = []
    # forec_text = []
    daily_tmp = []
    for n in range(dailysteps):
        for i, j in CONDITION_CLASSES.items():
            if datemsg[n]["textDay"] in j:
                # forec_cond.append(i)
                # forec_text.append(datemsg[n]["textDay"])

                daily_tmp.append(
                    [i, int(datemsg[n]["tempMax"]), int(datemsg[n]["tempMin"]), datemsg[n]["textDay"]]
                )
    data["forecast"] = daily_tmp
    # data["forecast"] = [
    #     [forec_cond[0], int(datemsg[0]["tempMax"]), int(datemsg[0]["tempMin"]), forec_text[0]],
    #     [forec_cond[1], int(datemsg[1]["tempMax"]), int(datemsg[1]["tempMin"]), forec_text[1]],
    #     [forec_cond[2], int(datemsg[2]["tempMax"]), int(datemsg[2]["tempMin"]), forec_text[2]],
    #     [forec_cond[3], int(datemsg[3]["tempMax"]), int(datemsg[3]["tempMin"]), forec_text[3]],
    #     [forec_cond[4], int(datemsg[4]["tempMax"]), int(datemsg[4]["tempMin"]), forec_text[4]],
    #     [forec_cond[5], int(datemsg[5]["tempMax"]), int(datemsg[5]["tempMin"]), forec_text[5]],
    #     [forec_cond[6], int(datemsg[6]["tempMax"]), int(datemsg[6]["tempMin"]), forec_text[6]]
    # ]

    hourlymsg = forecast_hourly["hourly"]
    # forecast_hourly = []
    # forec_text = []
    hourly_tmp = []
    for n in range(hourlysteps):
        for i, j in CONDITION_CLASSES.items():
            if hourlymsg[n]["text"] in j:
                # forecast_hourly.append(i)
                # forec_text.append(hourlymsg[n]["text"])

                hourly_tmp.append(
                    [i, float(hourlymsg[n]["temp"]), float(hourlymsg[n]["humidity"]),
                     float(hourlymsg[n]["precip"]), hourlymsg[n]["windDir"], int(hourlymsg[n]["windSpeed"]),
                     float(hourlymsg[n]["pop"]), hourlymsg[n]["text"]]
                )
    data["forecast_hourly"] = hourly_tmp
    # data["forecast_hourly"] = [
    #     [forecast_hourly[0], float(hourlymsg[0]["temp"]), float(hourlymsg[0]["humidity"]),
    #      float(hourlymsg[0]["precip"]), hourlymsg[0]["windDir"], int(hourlymsg[0]["windSpeed"]),
    #      float(hourlymsg[0]["pop"]), forec_text[0]],
    #     [forecast_hourly[1], float(hourlymsg[1]["temp"]), float(hourlymsg[1]["humidity"]),
    #      float(hourlymsg[1]["precip"]), hourlymsg[1]["windDir"], int(hourlymsg[1]["windSpeed"]),
    #      float(hourlymsg[1]["pop"]), forec_text[1]],
    #     [forecast_hourly[2], float(hourlymsg[2]["temp"]), float(hourlymsg[2]["humidity"]),
    #      float(hourlymsg[2]["precip"]), hourlymsg[2]["windDir"], int(hourlymsg[2]["windSpeed"]),
    #      float(hourlymsg[2]["pop"]), forec_text[2]],
    #     [forecast_hourly[3], float(hourlymsg[3]["temp"]), float(hourlymsg[3]["humidity"]),
    #      float(hourlymsg[3]["precip"]), hourlymsg[3]["windDir"], int(hourlymsg[3]["windSpeed"]),
    #      float(hourlymsg[3]["pop"]), forec_text[3]],
    #     [forecast_hourly[4], float(hourlymsg[4]["temp"]), float(hourlymsg[4]["humidity"]),
    #      float(hourlymsg[4]["precip"]), hourlymsg[4]["windDir"], int(hourlymsg[4]["windSpeed"]),
    #      float(hourlymsg[4]["pop"]), forec_text[4]],
    #     [forecast_hourly[5], float(hourlymsg[5]["temp"]), float(hourlymsg[5]["humidity"]),
    #      float(hourlymsg[5]["precip"]), hourlymsg[5]["windDir"], int(hourlymsg[5]["windSpeed"]),
    #      float(hourlymsg[5]["pop"]), forec_text[5]],
    #     [forecast_hourly[6], float(hourlymsg[6]["temp"]), float(hourlymsg[6]["humidity"]),
    #      float(hourlymsg[6]["precip"]), hourlymsg[6]["windDir"], int(hourlymsg[6]["windSpeed"]),
    #      float(hourlymsg[6]["pop"]), forec_text[6]],
    #     [forecast_hourly[7], float(hourlymsg[7]["temp"]), float(hourlymsg[7]["humidity"]),
    #      float(hourlymsg[7]["precip"]), hourlymsg[7]["windDir"], int(hourlymsg[7]["windSpeed"]),
    #      float(hourlymsg[7]["pop"]), forec_text[7]],
    #     [forecast_hourly[8], float(hourlymsg[8]["temp"]), float(hourlymsg[8]["humidity"]),
    #      float(hourlymsg[8]["precip"]), hourlymsg[8]["windDir"], int(hourlymsg[8]["windSpeed"]),
    #      float(hourlymsg[8]["pop"]), forec_text[8]],
    #     [forecast_hourly[9], float(hourlymsg[9]["temp"]), float(hourlymsg[9]["humidity"]),
    #      float(hourlymsg[9]["precip"]), hourlymsg[9]["windDir"], int(hourlymsg[9]["windSpeed"]),
    #      float(hourlymsg[9]["pop"]), forec_text[9]],
    #     [forecast_hourly[10], float(hourlymsg[10]["temp"]), float(hourlymsg[10]["humidity"]),
    #      float(hourlymsg[10]["precip"]), hourlymsg[10]["windDir"], int(hourlymsg[10]["windSpeed"]),
    #      float(hourlymsg[10]["pop"]), forec_text[10]],
    #     [forecast_hourly[11], float(hourlymsg[11]["temp"]), float(hourlymsg[11]["humidity"]),
    #      float(hourlymsg[11]["precip"]), hourlymsg[11]["windDir"], int(hourlymsg[11]["windSpeed"]),
    #      float(hourlymsg[11]["pop"]), forec_text[11]],
    #     [forecast_hourly[12], float(hourlymsg[12]["temp"]), float(hourlymsg[12]["humidity"]),
    #      float(hourlymsg[12]["precip"]), hourlymsg[12]["windDir"], int(hourlymsg[12]["windSpeed"]),
    #      float(hourlymsg[12]["pop"]), forec_text[12]],
    #     [forecast_hourly[13], float(hourlymsg[13]["temp"]), float(hourlymsg[13]["humidity"]),
    #      float(hourlymsg[13]["precip"]), hourlymsg[13]["windDir"], int(hourlymsg[13]["windSpeed"]),
    #      float(hourlymsg[13]["pop"]), forec_text[13]],
    #     [forecast_hourly[14], float(hourlymsg[14]["temp"]), float(hourlymsg[14]["humidity"]),
    #      float(hourlymsg[14]["precip"]), hourlymsg[14]["windDir"], int(hourlymsg[14]["windSpeed"]),
    #      float(hourlymsg[14]["pop"]), forec_text[14]],
    #     [forecast_hourly[15], float(hourlymsg[15]["temp"]), float(hourlymsg[15]["humidity"]),
    #      float(hourlymsg[15]["precip"]), hourlymsg[15]["windDir"], int(hourlymsg[15]["windSpeed"]),
    #      float(hourlymsg[15]["pop"]), forec_text[15]],
    #     [forecast_hourly[16], float(hourlymsg[16]["temp"]), float(hourlymsg[16]["humidity"]),
    #      float(hourlymsg[16]["precip"]), hourlymsg[16]["windDir"], int(hourlymsg[16]["windSpeed"]),
    #      float(hourlymsg[16]["pop"]), forec_text[16]],
    #     [forecast_hourly[17], float(hourlymsg[17]["temp"]), float(hourlymsg[17]["humidity"]),
    #      float(hourlymsg[17]["precip"]), hourlymsg[17]["windDir"], int(hourlymsg[17]["windSpeed"]),
    #      float(hourlymsg[17]["pop"]), forec_text[17]],
    #     [forecast_hourly[18], float(hourlymsg[18]["temp"]), float(hourlymsg[18]["humidity"]),
    #      float(hourlymsg[18]["precip"]), hourlymsg[18]["windDir"], int(hourlymsg[18]["windSpeed"]),
    #      float(hourlymsg[18]["pop"]), forec_text[18]],
    #     [forecast_hourly[19], float(hourlymsg[19]["temp"]), float(hourlymsg[19]["humidity"]),
    #      float(hourlymsg[19]["precip"]), hourlymsg[19]["windDir"], int(hourlymsg[19]["windSpeed"]),
    #      float(hourlymsg[19]["pop"]), forec_text[19]],
    #     [forecast_hourly[20], float(hourlymsg[20]["temp"]), float(hourlymsg[20]["humidity"]),
    #      float(hourlymsg[20]["precip"]), hourlymsg[20]["windDir"], int(hourlymsg[20]["windSpeed"]),
    #      float(hourlymsg[20]["pop"]), forec_text[20]],
    #     [forecast_hourly[21], float(hourlymsg[21]["temp"]), float(hourlymsg[21]["humidity"]),
    #      float(hourlymsg[21]["precip"]), hourlymsg[21]["windDir"], int(hourlymsg[21]["windSpeed"]),
    #      float(hourlymsg[21]["pop"]), forec_text[21]],
    #     [forecast_hourly[22], float(hourlymsg[22]["temp"]), float(hourlymsg[22]["humidity"]),
    #      float(hourlymsg[22]["precip"]), hourlymsg[22]["windDir"], int(hourlymsg[22]["windSpeed"]),
    #      float(hourlymsg[22]["pop"]), forec_text[22]],
    #     [forecast_hourly[23], float(hourlymsg[23]["temp"]), float(hourlymsg[23]["humidity"]),
    #      float(hourlymsg[23]["precip"]), hourlymsg[23]["windDir"], int(hourlymsg[23]["windSpeed"]),
    #      float(hourlymsg[23]["pop"]), forec_text[23]]
    # ]
    return data
