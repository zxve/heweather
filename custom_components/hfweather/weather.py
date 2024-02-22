import logging

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.weather import (
    WeatherEntity,
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

CONDITION_MAP_CN = {
    '100': '晴空之日',  # 白天
    '101': '云沉之日',  # 白天
    '102': '云影之日',  # 白天
    '103': '日光云影',  # 白天
    '104': '阴云密布',
    '150': '清澈之夜',  # 晚上
    '151': '云沉之夜',  # 晚上
    '152': '云影之日',  # 晚上
    '153': '星光云隐',  # 晚上
    '300': '阵雨之日',  # 白天
    '301': '强阵雨日',  # 白天
    '302': '雷阵雨',
    '303': '强雷阵雨',
    '304': '雷雨冰雹',
    '305': '细雨飘飘',
    '306': '中雨滂沱',
    '307': '大雨倾盆',
    '308': '暴雨如注',
    '309': '毛毛雨/细雨',
    '310': '暴雨',
    '311': '大暴雨',
    '312': '特大暴雨',
    '313': '冻雨交加',
    '314': '小到中雨',
    '315': '中到大雨',
    '316': '大到暴雨',
    '317': '暴雨到大暴雨',
    '318': '大暴雨到特大暴雨',
    '350': '阵雨之夜',  # 晚上
    '351': '强阵雨夜',  # 晚上
    '399': '雨',
    '400': '小雪纷飞',
    '401': '中雪漫天',
    '402': '大雪茫茫',
    '403': '暴雪肆虐	',
    '404': '雨夹雪',
    '405': '雨雪天气',
    '406': '阵雨雪日',  # 白天
    '407': '阵雪之日',  # 白天
    '408': '小到中雪',
    '409': '中到大雪',
    '410': '大到暴雪',
    '456': '阵雨雪夜',  # 晚上
    '457': '阵雪之夜',  # 晚上
    '499': '雪',
    '500': '淡雾飘渺',
    '501': '迷蒙之雾',
    '502': '霾',
    '503': '扬沙飞尘',
    '504': '浮尘',
    '507': '沙尘暴起',
    '508': '强沙尘暴',
    '509': '浓雾',
    '510': '强浓雾',
    '511': '中度霾',
    '512': '重度霾',
    '513': '严重霾',
    '514': '大雾',
    '515': '特强浓雾',
    '900': '热',
    '901': '冷',
    '999': '未知'
}
CONDITION_MAP = {
    '100': 'sunny',  # 白天
    '101': 'partlycloudy',  # 白天
    '102': 'partlycloudy',  # 白天
    '103': 'partlycloudy',  # 白天
    '104': 'cloudy',
    '150': 'clear-night',  # 晚上
    '151': 'partlycloudy',  # 晚上
    '152': 'partlycloudy',  # 晚上
    '153': 'partlycloudy',  # 晚上
    '300': 'rainy',  # 白天
    '301': 'rainy',  # 白天
    '302': 'lightning-rainy',
    '303': 'lightning-rainy',
    '304': 'hail',
    '305': 'rainy',
    '306': 'rainy',
    '307': 'pouring',
    '308': 'pouring',
    '309': 'rainy',
    '310': 'pouring',
    '311': 'pouring',
    '312': 'pouring',
    '313': 'rainy',
    '314': 'rainy',
    '315': 'pouring',
    '316': 'pouring',
    '317': 'pouring',
    '318': 'pouring',
    '350': 'rainy',  # 晚上
    '351': 'rainy',  # 晚上
    '399': 'rainy',
    '400': 'snowy',
    '401': 'snowy',
    '402': 'snowy',
    '403': 'snowy	',
    '404': 'snowy-rainy',
    '405': 'snowy-rainy',
    '406': 'snowy',  # 白天
    '407': 'snowy',  # 白天
    '408': 'snowy',
    '409': 'snowy',
    '410': 'snowy',
    '456': 'snowy',  # 晚上
    '457': 'snowy',  # 晚上
    '499': 'snowy',
    '500': 'fog',
    '501': 'fog',
    '502': 'fog',
    '503': 'fog',
    '504': 'fog',
    '507': 'fog',
    '508': 'fog',
    '509': 'fog',
    '510': 'fog',
    '511': 'fog',
    '512': 'fog',
    '513': 'fog',
    '514': 'fog',
    '515': 'fog',
    '900': 'sunny',
    '901': 'cloudy',
    '999': '未知'
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    _LOGGER.debug("metric: %s", coordinator.data["is_metric"])
    async_add_entities([HfweatherEntity(name, coordinator)], False)


class HfweatherEntity(WeatherEntity):
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
        icon = self.coordinator.data["now"]["icon"]
        return CONDITION_MAP.get(icon, None)

    @property
    def native_temperature(self):
        return self.coordinator.data["now"]['temp']

    @property
    def native_temperature_unit(self):
        return TEMP_CELSIUS if self.coordinator.data["is_metric"] == "metric:v2" else TEMP_FAHRENHEIT

    @property
    def humidity(self):
        return float(self.coordinator.data["now"]['humidity'])

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
        return self.coordinator.data["now"]['vis']

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
    #     data = super(HfweatherEntity, self).state_attributes
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
