import logging
from datetime import datetime

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.weather import (
    WeatherEntity,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED
)
from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    CONF_NAME
)
from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    MANUFACTURER
)

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)

CONDITION_MAP = {
    'CLEAR_DAY': 'sunny',
    'CLEAR_NIGHT': 'clear-night',
    'PARTLY_CLOUDY_DAY': 'partlycloudy',
    'PARTLY_CLOUDY_NIGHT': 'partlycloudy',
    'CLOUDY': 'cloudy',
    'LIGHT_HAZE': 'fog',
    'MODERATE_HAZE': 'fog',
    'HEAVY_HAZE': 'fog',
    'LIGHT_RAIN': 'rainy',
    'MODERATE_RAIN': 'rainy',
    'HEAVY_RAIN': 'pouring',
    'STORM_RAIN': 'pouring',
    'FOG': 'fog',
    'LIGHT_SNOW': 'snowy',
    'MODERATE_SNOW': 'snowy',
    'HEAVY_SNOW': 'snowy',
    'STORM_SNOW': 'snowy',
    'DUST': 'fog',
    'SAND': 'fog',
    'THUNDER_SHOWER': 'lightning-rainy',
    'HAIL': 'hail',
    'SLEET': 'snowy-rainy',
    'WIND': 'windy',
    'HAZE': 'fog',
    'RAIN': 'rainy',
    'SNOW': 'snowy'
}

CONDITION_MAP2 = {
    'CLEAR_DAY': '晴空之日',
    'CLEAR_NIGHT': '清澈之夜',
    'PARTLY_CLOUDY_DAY': '云影之日',
    'PARTLY_CLOUDY_NIGHT': '云掩之夜',
    'CLOUDY': '云沉之日',
    'LIGHT_HAZE': '淡雾飘渺',
    'MODERATE_HAZE': ' 中度雾霾',
    'HEAVY_HAZE': '重度雾霾',
    'LIGHT_RAIN': '细雨飘飘',
    'MODERATE_RAIN': '中雨滂沱',
    'HEAVY_RAIN': '大雨倾盆',
    'STORM_RAIN': '暴雨如注',
    'FOG': '迷蒙之雾',
    'LIGHT_SNOW': '小雪纷飞',
    'MODERATE_SNOW': '中雪漫天',
    'HEAVY_SNOW': '大雪茫茫',
    'STORM_SNOW': '暴雪肆虐',
    'DUST': '扬沙飞尘',
    'SAND': '沙尘暴起',
    'THUNDER_SHOWER': '雷雨降临',
    'HAIL': '冰雹落下',
    'SLEET': '冻雨交加',
    'WIND': '狂风呼啸',
    'HAZE': '浓雾笼罩',
    'RAIN': '阴雨连绵',
    'SNOW': '白雪皑皑'
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    _LOGGER.debug("metric: %s", coordinator.data["is_metric"])
    async_add_entities([HeweatherEntity(name, coordinator)], False)


class HeweatherEntity(WeatherEntity):
    def __init__(self, name, coordinator):
        self.coordinator = coordinator
        _LOGGER.debug("coordinator: %s", coordinator.data["updateTime"])
        self._name = name
        self._attrs = {}
        self._unit_system = "Metric" if self.coordinator.data["is_metric"] == "metric:v2" else "Imperial"

    @property
    def name(self):
        return self._name

    @property
    def attribution(self):
        return ATTRIBUTION

    @property
    def unique_id(self):
        _LOGGER.debug("weather_unique_id: %s", self.coordinator.data["location_key"])
        return self.coordinator.data["location_key"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.data["location_key"])},
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def condition(self):
        skycon = self.coordinator.data["now"]["text"]
        return CONDITION_MAP.get(skycon, None)

    @property
    def native_temperature(self):
        return self.coordinator.data["now"]['temperature']

    @property
    def native_temperature_unit(self):
        return TEMP_CELSIUS if self.coordinator.data["is_metric"] == "metric:v2" else TEMP_FAHRENHEIT

    @property
    def humidity(self):
        return self.coordinator.data["now"]['humidity']

    @property
    def native_wind_speed(self):
        """风速"""
        return self.coordinator.data["now"]['windSpeed']

    @property
    def wind_bearing(self):
        """风向"""
        return self.coordinator.data["now"]['windDir']

    @property
    def native_visibility(self):
        """能见度"""
        return self.coordinator.data["now"]['visibility']

    @property
    def native_pressure(self):
        return self.coordinator.data["now"]['pressure']

    # @property
    # def pm25(self):
    #     """pm25，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['pm25']
    #
    # @property
    # def pm10(self):
    #     """pm10，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['pm10']
    #
    # @property
    # def o3(self):
    #     """臭氧，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['o3']
    #
    # @property
    # def no2(self):
    #     """二氧化氮，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['no2']
    #
    # @property
    # def so2(self):
    #     """二氧化硫，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['so2']
    #
    # @property
    # def co(self):
    #     """一氧化碳，质量浓度值"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['co']
    #
    # @property
    # def aqi(self):
    #     """AQI（国标）"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['aqi']['chn']
    #
    # @property
    # def aqi_description(self):
    #     """AQI（国标）"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['description']['chn']
    #
    # @property
    # def aqi_usa(self):
    #     """AQI USA"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['aqi']['usa']
    #
    # @property
    # def aqi_usa_description(self):
    #     """AQI USA"""
    #     return self.coordinator.data["result"]['realtime']['air_quality']['description']['usa']
    #
    # @property
    # def forecast_hourly(self):
    #     """实时天气预报描述-小时"""
    #     return self.coordinator.data['result']['hourly']['description']
    #
    # @property
    # def forecast_minutely(self):
    #     """实时天气预报描述-分钟"""
    #     return self.coordinator.data['result']['minutely']['description']
    #
    # @property
    # def forecast_minutely_probability(self):
    #     """分钟概率"""
    #     return self.coordinator.data['result']['minutely']['probability']
    #
    # @property
    # def forecast_alert(self):
    #     """天气预警"""
    #     alert = self.coordinator.data['result']['alert'] if 'alert' in self.coordinator.data['result'] else ""
    #     return alert
    #
    # @property
    # def forecast_keypoint(self):
    #     """实时天气预报描述-注意事项"""
    #     return self.coordinator.data['result']['forecast_keypoint']

    # @property
    # def state_attributes(self):
    #     data = super(HeweatherEntity, self).state_attributes
    #     data['forecast_hourly'] = self.forecast_hourly
    #     data['forecast_minutely'] = self.forecast_minutely
    #     data['forecast_probability'] = self.forecast_minutely_probability
    #     data['forecast_keypoint'] = self.forecast_keypoint
    #     data['forecast_alert'] = self.forecast_alert
    #     data['pm25'] = self.pm25
    #     data['pm10'] = self.pm10
    #     data['skycon'] = self.coordinator.data['result']['realtime']['skycon']
    #     data['o3'] = self.o3
    #     data['no2'] = self.no2
    #     data['so2'] = self.so2
    #     data['co'] = self.co
    #     data['aqi'] = self.aqi
    #     data['aqi_description'] = self.aqi_description
    #     data['aqi_usa'] = self.aqi_usa
    #     data['aqi_usa_description'] = self.aqi_usa_description
    #
    #     data['hourly_precipitation'] = self.coordinator.data['result']['hourly']['precipitation']
    #     data['hourly_temperature'] = self.coordinator.data['result']['hourly']['temperature']
    #     data['hourly_cloudrate'] = self.coordinator.data['result']['hourly']['cloudrate']
    #     data['hourly_skycon'] = self.coordinator.data['result']['hourly']['skycon']
    #     data['hourly_wind'] = self.coordinator.data['result']['hourly']['wind']
    #     data['hourly_visibility'] = self.coordinator.data['result']['hourly']['visibility']
    #     data['hourly_aqi'] = self.coordinator.data['result']['hourly']['air_quality']['aqi']
    #     data['hourly_pm25'] = self.coordinator.data['result']['hourly']['air_quality']['pm25']
    #
    #     return data

    # @property
    # def forecast(self):
    #     forecast_data = []
    #     for i in range(len(self.coordinator.data['result']['daily']['temperature'])):
    #         time_str = self.coordinator.data['result']['daily']['temperature'][i]['date'][:10]
    #         data_dict = {
    #             ATTR_FORECAST_TIME: datetime.strptime(time_str, '%Y-%m-%d'),
    #             ATTR_FORECAST_CONDITION: CONDITION_MAP[self.coordinator.data['result']['daily']['skycon'][i]['value']],
    #             "skycon": self.coordinator.data['result']['daily']['skycon'][i]['value'],
    #             ATTR_FORECAST_PRECIPITATION: self.coordinator.data['result']['daily']['precipitation'][i]['avg'],
    #             ATTR_FORECAST_TEMP: self.coordinator.data['result']['daily']['temperature'][i]['max'],
    #             ATTR_FORECAST_TEMP_LOW: self.coordinator.data['result']['daily']['temperature'][i]['min'],
    #             ATTR_FORECAST_WIND_BEARING: self.coordinator.data['result']['daily']['wind'][i]['avg']['direction'],
    #             ATTR_FORECAST_WIND_SPEED: self.coordinator.data['result']['daily']['wind'][i]['avg']['speed']
    #         }
    #         forecast_data.append(data_dict)
    #
    #     return forecast_data

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        _LOGGER.debug("weather_update: %s", self.coordinator.data['updateTime'])

        await self.coordinator.async_request_refresh()
