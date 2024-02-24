import logging
from datetime import timedelta, datetime
import asyncio
import async_timeout
import aiohttp
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
from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    MANUFACTURER, CONDITION_CLASSES, DEFAULT_TIME, CONF_LOCATION, CONF_KEY, CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
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
    try:
        name = config_entry.data[CONF_NAME]
        location = config_entry.data[CONF_LOCATION]
        api_key = config_entry.data[CONF_API_KEY]
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        data = WeatherData(hass, longitude, latitude, api_key)

        async_add_entities([HfweatherEntity(name, data, location)], False)
    except Exception as e:
        raise e


# # 集成安装
# async def async_setup_entry(hass, config_entry, async_add_entities):
#     _LOGGER.debug(f"register_static_path: {ROOT_PATH + ':custom_components/qweather/local'}")
#     hass.http.register_static_path(ROOT_PATH, hass.config.path('custom_components/qweather/local'), False)
#     hass.components.frontend.add_extra_js_url(hass, ROOT_PATH + '/qweather-card/qweather-card.js?ver=' + VERSION)
#     hass.components.frontend.add_extra_js_url(hass, ROOT_PATH + '/qweather-card/qweather-more-info.js?ver=' + VERSION)
#
#     _LOGGER.info("setup platform weather.Heweather...")
#
#     name = config_entry.data.get(CONF_NAME)
#     key = config_entry.data[CONF_API_KEY]
#     location = config_entry.data[CONF_LOCATION]
#     #unique_id = config_entry.unique_id
#     longitude = round(config_entry.data[CONF_LONGITUDE],2)
#     latitude = round(config_entry.data[CONF_LATITUDE],2)
#     update_interval_minutes = config_entry.options.get(CONF_UPDATE_INTERVAL, 10)
#     dailysteps = config_entry.options.get(CONF_DAILYSTEPS, 7)
#     if dailysteps != 7 and dailysteps !=3:
#         dailysteps = 7
#     hourlysteps = config_entry.options.get(CONF_HOURLYSTEPS, 24)
#     if hourlysteps != 24:
#         hourlysteps = 24
#     alert = config_entry.options.get(CONF_ALERT, True)
#     life = config_entry.options.get(CONF_LIFEINDEX, True)
#     starttime = config_entry.options.get(CONF_STARTTIME, 0)
#     gird_weather = config_entry.options.get(CONF_GIRD, False)
#
#     #data = WeatherData(hass, name, unique_id, api_key, longitude, latitude, dailysteps ,hourlysteps, alert, life, starttime, gird_weather)
#     #location = config.get(CONF_LOCATION)
#     #key = config.get(CONF_KEY)
#     data = WeatherData(hass, location, key)
#     await data.async_update(dt_util.now())
#     async_track_time_interval(hass, data.async_update, timedelta(minutes = update_interval_minutes))
#     _LOGGER.debug('[%s]刷新间隔时间: %s 分钟', name, update_interval_minutes)
#     async_add_entities([HeWeather(data, location)], True)

# @asyncio.coroutine

class HfweatherEntity(WeatherEntity):
    """Representation of a weather condition."""

    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_precipitation_unit = PRECIPITATION_MILLIMETERS_PER_HOUR
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = LENGTH_KILOMETERS

    def __init__(self, name, data, location):
        """Initialize the  weather."""
        self._name = name
        self._object_id = 'localweather'
        self._condition = None
        self._temperature = None
        self._humidity = None
        self._pressure = None
        self._wind_speed = None
        self._wind_bearing = None
        self._visibility = None
        self._precipitation = None
        self._forecast = None
        self._forecast_hourly = None
        self._dew = None
        self._feelslike = None
        self._cloud = None

        self._data = data
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
    def should_poll(self):
        """attention No polling needed for a demo weather condition."""
        return True

    @property
    def native_dew_point(self):
        """Return the native_dew_point."""
        return self._dew

    @property
    def native_apparent_temperature(self):
        """Return the native_apparent_temperature."""
        return self._feelslike

    @property
    def cloud_coverage(self):
        """Return the cloud_coverage."""
        return self._cloud

    @property
    def native_temperature(self):
        """Return the temperature."""
        return self._temperature

    @property
    def native_temperature_unit(self):
        """Return the unit of measurement."""
        return self._attr_native_temperature_unit

    @property
    def humidity(self):
        """Return the humidity."""
        return self._humidity

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self._wind_speed

    @property
    def wind_bearing(self):
        """Return the wind speed."""
        return self._wind_bearing

    @property
    def native_pressure(self):
        """Return the pressure."""
        return self._pressure

    @property
    def native_visibility(self):
        """Return the visibility."""
        return self._visibility

    @property
    def native_precipitation(self):
        """Return the precipitation."""
        return self._precipitation

    @property
    def condition(self):
        """Return the weather condition."""
        if self._condition:
            match_list = [k for k, v in CONDITION_CLASSES.items() if self._condition in v]
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
        for entry in self._forecast:
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
        for entry in self._forecast_hourly:
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
            # [forecast_hourly[0], float(hourlymsg[0]["temp"]), float(hourlymsg[0]["humidity"]), float(hourlymsg[0]["precip"]), hourlymsg[0]["windDir"], int(hourlymsg[0]["windSpeed"])],

            reftime = reftime + timedelta(hours=1)
            forecast_hourly_data.append(data_dict)

        return forecast_hourly_data

    # @asyncio.coroutine
    async def async_update(self, now=DEFAULT_TIME):
        """update函数变成了async_update."""
        self._updatetime = self._data.updatetime
        # self._name = self._data.name
        self._condition = self._data.condition
        self._temperature = self._data.temperature
        _attr_native_temperature_unit = self._data.temperature_unit
        self._humidity = self._data.humidity
        self._pressure = self._data.pressure
        self._wind_speed = self._data.wind_speed
        self._wind_bearing = self._data.wind_bearing
        self._visibility = self._data.visibility
        self._precipitation = self._data.precipitation
        self._dew = self._data.dew
        self._feelslike = self._data.feelslike
        self._cloud = self._data.cloud

        self._forecast = self._data.forecast
        self._forecast_hourly = self._data.forecast_hourly
        _LOGGER.info("success to update informations")


class WeatherData():
    """天气相关的数据，存储在这个类中."""

    def __init__(self, hass, longitude, latitude, key):
        """初始化函数."""
        self._hass = hass
        self._forecast_url = f"https://devapi.qweather.com/v7/weather/7d?location={longitude},{latitude}&key={key}"
        self._weather_now_url = f"https://devapi.qweather.com/v7/weather/now?location={longitude},{latitude}&key={key}"
        self._forecast_hourly_url = f"https://devapi.qweather.com/v7/weather/24h?location={longitude},{latitude}&key={key}"
        self._params = {"location": f"{longitude}/{latitude}", "key": key}

        # self._name = None
        self._condition = None
        self._temperature = None
        self._temperature_unit = None
        self._humidity = None
        self._pressure = None
        self._wind_speed = None
        self._wind_bearing = None
        self._visibility = None
        self._precipitation = None
        self._dew = None
        self._feelslike = None
        self._cloud = None

        self._forecast = None
        self._forecast_hourly = None
        self._updatetime = None

    @property
    def condition(self):
        """天气情况."""
        return self._condition

    @property
    def temperature(self):
        """温度."""
        return self._temperature

    @property
    def temperature_unit(self):
        """温度单位."""
        return TEMP_CELSIUS

    @property
    def humidity(self):
        """湿度."""
        return self._humidity

    @property
    def pressure(self):
        """气压."""
        return self._pressure

    @property
    def dew(self):
        """露点温度"""
        return self._dew

    @property
    def feelslike(self):
        """体感温度"""
        return self._feelslike

    @property
    def cloud(self):
        """云量"""
        return self._cloud

    @property
    def wind_speed(self):
        """风速."""
        return self._wind_speed

    @property
    def wind_bearing(self):
        """风向."""
        return self._wind_bearing

    @property
    def visibility(self):
        """能见度."""
        return self._visibility

    @property
    def precipitation(self):
        """当前小时累计降水量."""
        return self._precipitation

    @property
    def forecast(self):
        """天预报."""
        return self._forecast

    @property
    def forecast_hourly(self):
        """小时预报."""
        return self._forecast_hourly

    @property
    def updatetime(self):
        """更新时间."""
        return self._updatetime

    # @asyncio.coroutine
    async def async_update(self, now):
        """从远程更新信息."""
        _LOGGER.info("Update from JingdongWangxiang's OpenAPI...")

        """
        # 异步模式的测试代码
        import time
        _LOGGER.info("before time.sleep")
        time.sleep(40)
        _LOGGER.info("after time.sleep and before asyncio.sleep")
        asyncio.sleep(40)
        _LOGGER.info("after asyncio.sleep and before yield from asyncio.sleep")
        #yield from
        await asyncio.sleep(40)
        _LOGGER.info("after yield from asyncio.sleep")
        """

        # 通过HTTP访问，获取需要的信息
        # 此处使用了基于aiohttp库的async_get_clientsession
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            connector = aiohttp.TCPConnector(limit=10)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(self._weather_now_url) as response:
                    json_data = await response.json()
                    weather = json_data["now"]
                async with session.get(self._forecast_url) as response:
                    json_data = await response.json()
                    forecast = json_data
                async with session.get(self._forecast_hourly_url) as response:
                    json_data = await response.json()
                    forecast_hourly = json_data

        except(asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Error while accessing: %s", self._weather_now_url)
            _LOGGER.error("Error while accessing: %s", self._forecast_url)
            _LOGGER.error("Error while accessing: %s", self._forecast_hourly_url)
            return

        self._temperature = float(weather["temp"])
        self._humidity = float(weather["humidity"])
        self._pressure = weather["pressure"]
        self._condition = weather["text"]
        self._wind_speed = weather["windSpeed"]
        self._wind_bearing = weather["windDir"]
        self._visibility = weather["vis"]
        self._precipitation = float(weather["precip"])

        self._feelslike = float(weather["feelsLike"])
        self._dew = float(weather["dew"])
        self._cloud = int(weather["cloud"])

        # self._windScale = weather["windScale"]
        self._updatetime = weather["obsTime"]

        datemsg = forecast["daily"]

        forec_cond = []
        forec_text = []
        for n in range(7):
            for i, j in CONDITION_CLASSES.items():
                if datemsg[n]["textDay"] in j:
                    forec_cond.append(i)
                    forec_text.append(datemsg[n]["textDay"])

        self._forecast = [
            [forec_cond[0], int(datemsg[0]["tempMax"]), int(datemsg[0]["tempMin"]), forec_text[0]],
            [forec_cond[1], int(datemsg[1]["tempMax"]), int(datemsg[1]["tempMin"]), forec_text[1]],
            [forec_cond[2], int(datemsg[2]["tempMax"]), int(datemsg[2]["tempMin"]), forec_text[2]],
            [forec_cond[3], int(datemsg[3]["tempMax"]), int(datemsg[3]["tempMin"]), forec_text[3]],
            [forec_cond[4], int(datemsg[4]["tempMax"]), int(datemsg[4]["tempMin"]), forec_text[4]],
            [forec_cond[5], int(datemsg[5]["tempMax"]), int(datemsg[5]["tempMin"]), forec_text[5]],
            [forec_cond[6], int(datemsg[6]["tempMax"]), int(datemsg[6]["tempMin"]), forec_text[6]]
        ]

        hourlymsg = forecast_hourly["hourly"]
        forecast_hourly = []
        forec_text = []
        for n in range(24):
            for i, j in CONDITION_CLASSES.items():
                if hourlymsg[n]["text"] in j:
                    forecast_hourly.append(i)
                    forec_text.append(hourlymsg[n]["text"])

        self._forecast_hourly = [
            [forecast_hourly[0], float(hourlymsg[0]["temp"]), float(hourlymsg[0]["humidity"]),
             float(hourlymsg[0]["precip"]), hourlymsg[0]["windDir"], int(hourlymsg[0]["windSpeed"]),
             float(hourlymsg[0]["pop"]), forec_text[0]],
            [forecast_hourly[1], float(hourlymsg[1]["temp"]), float(hourlymsg[1]["humidity"]),
             float(hourlymsg[1]["precip"]), hourlymsg[1]["windDir"], int(hourlymsg[1]["windSpeed"]),
             float(hourlymsg[1]["pop"]), forec_text[1]],
            [forecast_hourly[2], float(hourlymsg[2]["temp"]), float(hourlymsg[2]["humidity"]),
             float(hourlymsg[2]["precip"]), hourlymsg[2]["windDir"], int(hourlymsg[2]["windSpeed"]),
             float(hourlymsg[2]["pop"]), forec_text[2]],
            [forecast_hourly[3], float(hourlymsg[3]["temp"]), float(hourlymsg[3]["humidity"]),
             float(hourlymsg[3]["precip"]), hourlymsg[3]["windDir"], int(hourlymsg[3]["windSpeed"]),
             float(hourlymsg[3]["pop"]), forec_text[3]],
            [forecast_hourly[4], float(hourlymsg[4]["temp"]), float(hourlymsg[4]["humidity"]),
             float(hourlymsg[4]["precip"]), hourlymsg[4]["windDir"], int(hourlymsg[4]["windSpeed"]),
             float(hourlymsg[4]["pop"]), forec_text[4]],
            [forecast_hourly[5], float(hourlymsg[5]["temp"]), float(hourlymsg[5]["humidity"]),
             float(hourlymsg[5]["precip"]), hourlymsg[5]["windDir"], int(hourlymsg[5]["windSpeed"]),
             float(hourlymsg[5]["pop"]), forec_text[5]],
            [forecast_hourly[6], float(hourlymsg[6]["temp"]), float(hourlymsg[6]["humidity"]),
             float(hourlymsg[6]["precip"]), hourlymsg[6]["windDir"], int(hourlymsg[6]["windSpeed"]),
             float(hourlymsg[6]["pop"]), forec_text[6]],
            [forecast_hourly[7], float(hourlymsg[7]["temp"]), float(hourlymsg[7]["humidity"]),
             float(hourlymsg[7]["precip"]), hourlymsg[7]["windDir"], int(hourlymsg[7]["windSpeed"]),
             float(hourlymsg[7]["pop"]), forec_text[7]],
            [forecast_hourly[8], float(hourlymsg[8]["temp"]), float(hourlymsg[8]["humidity"]),
             float(hourlymsg[8]["precip"]), hourlymsg[8]["windDir"], int(hourlymsg[8]["windSpeed"]),
             float(hourlymsg[8]["pop"]), forec_text[8]],
            [forecast_hourly[9], float(hourlymsg[9]["temp"]), float(hourlymsg[9]["humidity"]),
             float(hourlymsg[9]["precip"]), hourlymsg[9]["windDir"], int(hourlymsg[9]["windSpeed"]),
             float(hourlymsg[9]["pop"]), forec_text[9]],
            [forecast_hourly[10], float(hourlymsg[10]["temp"]), float(hourlymsg[10]["humidity"]),
             float(hourlymsg[10]["precip"]), hourlymsg[10]["windDir"], int(hourlymsg[10]["windSpeed"]),
             float(hourlymsg[10]["pop"]), forec_text[10]],
            [forecast_hourly[11], float(hourlymsg[11]["temp"]), float(hourlymsg[11]["humidity"]),
             float(hourlymsg[11]["precip"]), hourlymsg[11]["windDir"], int(hourlymsg[11]["windSpeed"]),
             float(hourlymsg[11]["pop"]), forec_text[11]],
            [forecast_hourly[12], float(hourlymsg[12]["temp"]), float(hourlymsg[12]["humidity"]),
             float(hourlymsg[12]["precip"]), hourlymsg[12]["windDir"], int(hourlymsg[12]["windSpeed"]),
             float(hourlymsg[12]["pop"]), forec_text[12]],
            [forecast_hourly[13], float(hourlymsg[13]["temp"]), float(hourlymsg[13]["humidity"]),
             float(hourlymsg[13]["precip"]), hourlymsg[13]["windDir"], int(hourlymsg[13]["windSpeed"]),
             float(hourlymsg[13]["pop"]), forec_text[13]],
            [forecast_hourly[14], float(hourlymsg[14]["temp"]), float(hourlymsg[14]["humidity"]),
             float(hourlymsg[14]["precip"]), hourlymsg[14]["windDir"], int(hourlymsg[14]["windSpeed"]),
             float(hourlymsg[14]["pop"]), forec_text[14]],
            [forecast_hourly[15], float(hourlymsg[15]["temp"]), float(hourlymsg[15]["humidity"]),
             float(hourlymsg[15]["precip"]), hourlymsg[15]["windDir"], int(hourlymsg[15]["windSpeed"]),
             float(hourlymsg[15]["pop"]), forec_text[15]],
            [forecast_hourly[16], float(hourlymsg[16]["temp"]), float(hourlymsg[16]["humidity"]),
             float(hourlymsg[16]["precip"]), hourlymsg[16]["windDir"], int(hourlymsg[16]["windSpeed"]),
             float(hourlymsg[16]["pop"]), forec_text[16]],
            [forecast_hourly[17], float(hourlymsg[17]["temp"]), float(hourlymsg[17]["humidity"]),
             float(hourlymsg[17]["precip"]), hourlymsg[17]["windDir"], int(hourlymsg[17]["windSpeed"]),
             float(hourlymsg[17]["pop"]), forec_text[17]],
            [forecast_hourly[18], float(hourlymsg[18]["temp"]), float(hourlymsg[18]["humidity"]),
             float(hourlymsg[18]["precip"]), hourlymsg[18]["windDir"], int(hourlymsg[18]["windSpeed"]),
             float(hourlymsg[18]["pop"]), forec_text[18]],
            [forecast_hourly[19], float(hourlymsg[19]["temp"]), float(hourlymsg[19]["humidity"]),
             float(hourlymsg[19]["precip"]), hourlymsg[19]["windDir"], int(hourlymsg[19]["windSpeed"]),
             float(hourlymsg[19]["pop"]), forec_text[19]],
            [forecast_hourly[20], float(hourlymsg[20]["temp"]), float(hourlymsg[20]["humidity"]),
             float(hourlymsg[20]["precip"]), hourlymsg[20]["windDir"], int(hourlymsg[20]["windSpeed"]),
             float(hourlymsg[20]["pop"]), forec_text[20]],
            [forecast_hourly[21], float(hourlymsg[21]["temp"]), float(hourlymsg[21]["humidity"]),
             float(hourlymsg[21]["precip"]), hourlymsg[21]["windDir"], int(hourlymsg[21]["windSpeed"]),
             float(hourlymsg[21]["pop"]), forec_text[21]],
            [forecast_hourly[22], float(hourlymsg[22]["temp"]), float(hourlymsg[22]["humidity"]),
             float(hourlymsg[22]["precip"]), hourlymsg[22]["windDir"], int(hourlymsg[22]["windSpeed"]),
             float(hourlymsg[22]["pop"]), forec_text[22]],
            [forecast_hourly[23], float(hourlymsg[23]["temp"]), float(hourlymsg[23]["humidity"]),
             float(hourlymsg[23]["precip"]), hourlymsg[23]["windDir"], int(hourlymsg[23]["windSpeed"]),
             float(hourlymsg[23]["pop"]), forec_text[23]]
        ]
        _LOGGER.info("success to load local informations")

# class HfweatherEntity(WeatherEntity):
#     def __init__(self, name, coordinator):
#         self.coordinator = coordinator
#         _LOGGER.debug("coordinator: %s", coordinator.data["updateTime"])
#         self._name = name
#         self._attrs = {}
#         self._unit_system = "Metric" if self.coordinator.data["is_metric"] == "metric:v2" else "Imperial"
#
#     @property
#     def name(self):
#         return self._name
#
#     @property
#     def attribution(self):
#         return ATTRIBUTION
#
#     @property
#     def unique_id(self):
#         _LOGGER.debug("weather_unique_id: %s", self.coordinator.data["location_key"])
#         return self.coordinator.data["location_key"]
#
#     @property
#     def device_info(self):
#         return {
#             "identifiers": {(DOMAIN, self.coordinator.data["location_key"])},
#             "name": self._name,
#             "manufacturer": MANUFACTURER,
#             "entry_type": DeviceEntryType.SERVICE,
#         }
#
#     @property
#     def should_poll(self):
#         return False
#
#     @property
#     def available(self):
#         return self.coordinator.last_update_success
#
#     @property
#     def condition(self):
#         icon = self.coordinator.data["now"]["icon"]
#         return CONDITION_MAP.get(icon, None)
#
#     @property
#     def native_temperature(self):
#         return self.coordinator.data["now"]['temp']
#
#     @property
#     def native_temperature_unit(self):
#         return TEMP_CELSIUS if self.coordinator.data["is_metric"] == "metric:v2" else TEMP_FAHRENHEIT
#
#     @property
#     def humidity(self):
#         return float(self.coordinator.data["now"]['humidity'])
#
#     @property
#     def native_wind_speed(self):
#         """风速"""
#         return self.coordinator.data["now"]['windSpeed']
#
#     @property
#     def wind_bearing(self):
#         """风向"""
#         return self.coordinator.data["now"]['windDir']
#
#     @property
#     def native_visibility(self):
#         """能见度"""
#         return self.coordinator.data["now"]['vis']
#
#     @property
#     def native_pressure(self):
#         return self.coordinator.data["now"]['pressure']
#
#     # @property
#     # def pm25(self):
#     #     """pm25，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['pm25']
#     #
#     # @property
#     # def pm10(self):
#     #     """pm10，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['pm10']
#     #
#     # @property
#     # def o3(self):
#     #     """臭氧，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['o3']
#     #
#     # @property
#     # def no2(self):
#     #     """二氧化氮，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['no2']
#     #
#     # @property
#     # def so2(self):
#     #     """二氧化硫，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['so2']
#     #
#     # @property
#     # def co(self):
#     #     """一氧化碳，质量浓度值"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['co']
#     #
#     # @property
#     # def aqi(self):
#     #     """AQI（国标）"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['aqi']['chn']
#     #
#     # @property
#     # def aqi_description(self):
#     #     """AQI（国标）"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['description']['chn']
#     #
#     # @property
#     # def aqi_usa(self):
#     #     """AQI USA"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['aqi']['usa']
#     #
#     # @property
#     # def aqi_usa_description(self):
#     #     """AQI USA"""
#     #     return self.coordinator.data["result"]['realtime']['air_quality']['description']['usa']
#     #
#     # @property
#     # def forecast_hourly(self):
#     #     """实时天气预报描述-小时"""
#     #     return self.coordinator.data['result']['hourly']['description']
#     #
#     # @property
#     # def forecast_minutely(self):
#     #     """实时天气预报描述-分钟"""
#     #     return self.coordinator.data['result']['minutely']['description']
#     #
#     # @property
#     # def forecast_minutely_probability(self):
#     #     """分钟概率"""
#     #     return self.coordinator.data['result']['minutely']['probability']
#     #
#     # @property
#     # def forecast_alert(self):
#     #     """天气预警"""
#     #     alert = self.coordinator.data['result']['alert'] if 'alert' in self.coordinator.data['result'] else ""
#     #     return alert
#     #
#     # @property
#     # def forecast_keypoint(self):
#     #     """实时天气预报描述-注意事项"""
#     #     return self.coordinator.data['result']['forecast_keypoint']
#
#     # @property
#     # def state_attributes(self):
#     #     data = super(HfweatherEntity, self).state_attributes
#     #     data['forecast_hourly'] = self.forecast_hourly
#     #     data['forecast_minutely'] = self.forecast_minutely
#     #     data['forecast_probability'] = self.forecast_minutely_probability
#     #     data['forecast_keypoint'] = self.forecast_keypoint
#     #     data['forecast_alert'] = self.forecast_alert
#     #     data['pm25'] = self.pm25
#     #     data['pm10'] = self.pm10
#     #     data['skycon'] = self.coordinator.data['result']['realtime']['skycon']
#     #     data['o3'] = self.o3
#     #     data['no2'] = self.no2
#     #     data['so2'] = self.so2
#     #     data['co'] = self.co
#     #     data['aqi'] = self.aqi
#     #     data['aqi_description'] = self.aqi_description
#     #     data['aqi_usa'] = self.aqi_usa
#     #     data['aqi_usa_description'] = self.aqi_usa_description
#     #
#     #     data['hourly_precipitation'] = self.coordinator.data['result']['hourly']['precipitation']
#     #     data['hourly_temperature'] = self.coordinator.data['result']['hourly']['temperature']
#     #     data['hourly_cloudrate'] = self.coordinator.data['result']['hourly']['cloudrate']
#     #     data['hourly_skycon'] = self.coordinator.data['result']['hourly']['skycon']
#     #     data['hourly_wind'] = self.coordinator.data['result']['hourly']['wind']
#     #     data['hourly_visibility'] = self.coordinator.data['result']['hourly']['visibility']
#     #     data['hourly_aqi'] = self.coordinator.data['result']['hourly']['air_quality']['aqi']
#     #     data['hourly_pm25'] = self.coordinator.data['result']['hourly']['air_quality']['pm25']
#     #
#     #     return data
#
#     # @property
#     # def forecast(self):
#     #     forecast_data = []
#     #     for i in range(len(self.coordinator.data['result']['daily']['temperature'])):
#     #         time_str = self.coordinator.data['result']['daily']['temperature'][i]['date'][:10]
#     #         data_dict = {
#     #             ATTR_FORECAST_TIME: datetime.strptime(time_str, '%Y-%m-%d'),
#     #             ATTR_FORECAST_CONDITION: CONDITION_MAP[self.coordinator.data['result']['daily']['skycon'][i]['value']],
#     #             "skycon": self.coordinator.data['result']['daily']['skycon'][i]['value'],
#     #             ATTR_FORECAST_PRECIPITATION: self.coordinator.data['result']['daily']['precipitation'][i]['avg'],
#     #             ATTR_FORECAST_TEMP: self.coordinator.data['result']['daily']['temperature'][i]['max'],
#     #             ATTR_FORECAST_TEMP_LOW: self.coordinator.data['result']['daily']['temperature'][i]['min'],
#     #             ATTR_FORECAST_WIND_BEARING: self.coordinator.data['result']['daily']['wind'][i]['avg']['direction'],
#     #             ATTR_FORECAST_WIND_SPEED: self.coordinator.data['result']['daily']['wind'][i]['avg']['speed']
#     #         }
#     #         forecast_data.append(data_dict)
#     #
#     #     return forecast_data
#
#     async def async_added_to_hass(self):
#         self.async_on_remove(
#             self.coordinator.async_add_listener(self.async_write_ha_state)
#         )
#
#     async def async_update(self):
#         _LOGGER.debug("weather_update: %s", self.coordinator.data['updateTime'])
#
#         await self.coordinator.async_request_refresh()
