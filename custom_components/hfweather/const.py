from datetime import timedelta
import homeassistant.util.dt as dt_util

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    UnitOfLength,
    UnitOfTemperature,
    DEGREE, UnitOfSpeed,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    PRECIPITATION_MILLIMETERS_PER_HOUR,
    DEVICE_CLASS_PM25, DEVICE_CLASS_PM10, DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE, WIND_SPEED, UnitOfPressure, CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT,
)

# 方便直接使用Home Assistant Brands上面的和风天气图标, 在这里和manifest.json中修改domain为heweather
DOMAIN = "heweather"

PLATFORMS = ["sensor", "weather"]

REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "weather.py",
    "config_flow.py",
    "services.yaml",
    "translations/zh-Hans.json",
]
VERSION = "0.1.0"
ISSUE_URL = ""

STARTUP = """

"""
ATTR_UPDATE_TIME = "更新时间"
ATTR_SUGGESTION = "建议"
ATTRIBUTION = "Data provided by 和风天气"
ATTR_ICON = "icon"
ATTR_FORECAST = "forecast"
ATTR_LABEL = "label"
ATTR_UNIT_IMPERIAL = "Imperial"
ATTR_UNIT_METRIC = "Metric"
MANUFACTURER = "Hfweather, Inc."
NAME = "Hfweather"

CONF_API_KEY = "api_key"
CONF_API_VERSION = "api_version"
CONF_LOCATION = "location"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
COORDINATOR = "coordinator"
CONF_ALERT = "alert"
CONF_HOURLYSTEPS = "hourlysteps"
CONF_DAILYSTEPS = "dailysteps"
CONF_STARTTIME = "starttime"

UNDO_UPDATE_LISTENER = "undo_update_listener"

OPTIONAL_SENSORS = (
    "windDir",
)

# new
DISASTER_LEVEL = {
    "Cancel": 0,
    "None": 0,
    "Unknown": 0,
    "Standard": 1,
    "Minor": 2,
    "Moderate": 3,
    "Major": 4,
    "Severe": 5,
    "Extreme": 6
}

TIME_BETWEEN_UPDATES = timedelta(minutes=120)

DEFAULT_TIME = dt_util.now()
CONF_OPTIONS = "options"
CONF_LOCATION = "location"
CONF_DISASTER_LEVEL = "disaster_level"
CONF_DISASTER_MSG = "disaster_msg"

OPTIONS = {
    "temperature": [SensorDeviceClass.TEMPERATURE, "室外温度", "mdi:thermometer", UnitOfTemperature.CELSIUS,
                    UnitOfTemperature.FAHRENHEIT],
    "humidity": [SensorDeviceClass.HUMIDITY, "室外湿度", "mdi:water-percent", PERCENTAGE, PERCENTAGE],
    "feelsLike": [SensorDeviceClass.TEMPERATURE, "体感温度", "mdi:thermometer", UnitOfTemperature.CELSIUS,
                  UnitOfTemperature.FAHRENHEIT],
    "text": [None, "天气描述", "mdi:thermometer", '', ''],
    "precip": [None, "小时降水量", "mdi:weather-rainy", PRECIPITATION_MILLIMETERS_PER_HOUR,
               UnitOfLength.INCHES],
    "windDir": [None, "风向", "mdi:windsock", DEGREE, DEGREE],
    "windScale": [None, "风力等级", "mdi:weather-windy", '', ''],
    "windSpeed": [WIND_SPEED, "风速", "mdi:weather-windy", UnitOfSpeed.KILOMETERS_PER_HOUR,
                  UnitOfSpeed.MILES_PER_HOUR],
    "dew": [SensorDeviceClass.TEMPERATURE, "露点温度", "mdi:thermometer-water", SensorDeviceClass.TEMPERATURE,
            UnitOfTemperature.FAHRENHEIT],
    "pressure": [SensorDeviceClass.PRESSURE, "大气压强", "mdi:thermometer", UnitOfPressure.HPA, UnitOfPressure.HPA],
    "vis": [None, "能见度", "mdi:thermometer", UnitOfLength.KILOMETERS, UnitOfLength.KILOMETERS],
    "place": [None, "气候位置", "mdi:thermometer", '', ''],
    "cloud": [None, "云量", "mdi:cloud-percent", PERCENTAGE, PERCENTAGE],
    "primary": [None, "空气质量的主要污染物", "mdi:weather-dust", '', ''],
    "category": [None, "空气质量指数级别", "mdi:walk", '', ''],
    "level": [None, "空气质量指数等级", "mdi:walk", '', ''],
    "pm25": [SensorDeviceClass.PM25, "PM2.5", "mdi:walk", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
             CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "pm10": [SensorDeviceClass.PM10, "PM10", "mdi:walk", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
             CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "no2": [SensorDeviceClass.NITROGEN_DIOXIDE, "二氧化氮", "mdi:emoticon-dead", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "so2": [SensorDeviceClass.SULPHUR_DIOXIDE, "二氧化硫", "mdi:emoticon-dead", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "co": [SensorDeviceClass.CO, "一氧化碳", "mdi:molecule-co", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
           CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "o3": [SensorDeviceClass.OZONE, "臭氧", "mdi:weather-cloudy", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
           CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT],
    "qlty": [None, "综合空气质量", "mdi:quality-high", '', ''],
    "disaster_warn": [None, "灾害预警", "mdi:alert", '', ''],
    "air": [None, "空气污染扩散条件指数", "mdi:air-conditioner", '', ''],
    "comfortable": [None, "舒适度指数", "mdi:human-greeting", '', ''],
    "cw": [None, "洗车指数", "mdi:car", '', ''],
    "drsg": [None, "穿衣指数", "mdi:hanger", '', ''],
    "flu": [None, "感冒指数", "mdi:biohazard", '', ''],
    "sport": [None, "运动指数", "mdi:badminton", '', ''],
    "trav": [None, "旅行指数", "mdi:wallet-travel", '', ''],
    "uv": [None, "紫外线指数", "mdi:weather-sun-wireless", '', ''],
    "guomin": [None, "过敏指数", "mdi:sunglasses", '', ''],
    "kongtiao": [None, "空调开启指数", "mdi:air-conditioner", '', ''],
    "sunglass": [None, "太阳镜指数", "mdi:sunglasses", '', ''],
    "fangshai": [None, "防晒指数", "mdi:sun-protection-outline", '', ''],
    "liangshai": [None, "晾晒指数", "mdi:tshirt-crew-outline", '', ''],
    "jiaotong": [None, "交通指数", "mdi:train-car", '', ''],
}

CONDITION_CLASSES = {
    'sunny': ["晴"],
    'cloudy': ["多云"],
    'partlycloudy': ["少云", "晴间多云", "阴"],
    'windy': ["有风", "微风", "和风", "清风"],
    'windy-variant': ["强风", "劲风", "疾风", "大风", "烈风"],
    'hurricane': ["飓风", "龙卷风", "热带风暴", "狂暴风", "风暴"],
    'rainy': ["雨", "毛毛雨", "细雨", "小雨", "小到中雨", "中雨", "中到大雨", "大雨", "大到暴雨", "阵雨", "极端降雨", "冻雨"],
    'pouring': ["暴雨", "暴雨到大暴雨", "大暴雨", "大暴雨到特大暴雨", "特大暴雨", "强阵雨"],
    'lightning-rainy': ["雷阵雨", "强雷阵雨"],
    'fog': ["雾", "薄雾", "霾", "浓雾", "强浓雾", "中度霾", "重度霾", "严重霾", "大雾", "特强浓雾"],
    'hail': ["雷阵雨伴有冰雹"],
    'snowy': ["小雪", "小到中雪", "中雪", "中到大雪", "大雪", "大到暴雪", "暴雪", "阵雪"],
    'snowy-rainy': ["雨夹雪", "雨雪天气", "阵雨夹雪"],
    'exceptional': ["扬沙", "浮尘", "沙尘暴", "强沙尘暴", "未知"],
}
