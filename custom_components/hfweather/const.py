from datetime import timedelta
import homeassistant.util.dt as dt_util

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    UnitOfLength,
    UnitOfTemperature,
    DEGREE, UnitOfSpeed,
    TEMP_CELSIUS,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    PRECIPITATION_MILLIMETERS_PER_HOUR,
    SPEED_KILOMETERS_PER_HOUR,
    PRESSURE_HPA,
    LENGTH_KILOMETERS,
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
ATTR_FORECAST = CONF_DAILYSTEPS = "forecast"
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

UNDO_UPDATE_LISTENER = "undo_update_listener"

OPTIONAL_SENSORS = (
    "WindDirection",
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

WEATHER_TIME_BETWEEN_UPDATES = timedelta(seconds=600)
LIFE_SUGGESTION_TIME_BETWEEN_UPDATES = timedelta(seconds=7200)

TIME_BETWEEN_UPDATES = timedelta(seconds=1800)
HOURLY_TIME_BETWEEN_UPDATES = timedelta(seconds=1800)

DEFAULT_TIME = dt_util.now()
CONF_OPTIONS = "options"
CONF_LOCATION = "location"
CONF_KEY = "key"
CONF_DISASTER_LEVEL = "disaster_level"
CONF_DISASTER_MSG = "disaster_msg"

OPTIONS = {
    "temperature": ["Heweather_temperature", "室外温度", "mdi:thermometer", TEMP_CELSIUS],
    "humidity": ["Heweather_humidity", "室外湿度", "mdi:water-percent", PERCENTAGE],
    "feelsLike": ["Heweather_feelsLike", "体感温度", "mdi:thermometer", TEMP_CELSIUS],
    "text": ["Heweather_text", "天气描述", "mdi:thermometer", ' '],
    "precip": ["Heweather_precip", "小时降水量", "mdi:weather-rainy", PRECIPITATION_MILLIMETERS_PER_HOUR],
    "windDir": ["Heweather_windDir", "风向", "mdi:windsock", ' '],
    "windScale": ["Heweather_windScale", "风力等级", "mdi:weather-windy", ' '],
    "windSpeed": ["Heweather_windSpeed", "风速", "mdi:weather-windy", SPEED_KILOMETERS_PER_HOUR],
    "dew": ["Heweather_dew", "露点温度", "mdi:thermometer-water", ' '],
    "pressure": ["Heweather_pressure", "大气压强", "mdi:thermometer", PRESSURE_HPA],
    "vis": ["Heweather_vis", "能见度", "mdi:thermometer", LENGTH_KILOMETERS],
    "cloud": ["Heweather_cloud", "云量", "mdi:cloud-percent", PERCENTAGE],
    "primary": ["Heweather_primary", "空气质量的主要污染物", "mdi:weather-dust", " "],
    "category": ["Heweather_category", "空气质量指数级别", "mdi:walk", " "],
    "level": ["Heweather_level", "空气质量指数等级", "mdi:walk", " "],
    "pm25": ["Heweather_pm25", "PM2.5", "mdi:walk", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "pm10": ["Heweather_pm10", "PM10", "mdi:walk", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "no2": ["Heweather_no2", "二氧化氮", "mdi:emoticon-dead", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "so2": ["Heweather_so2", "二氧化硫", "mdi:emoticon-dead", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "co": ["Heweather_co", "一氧化碳", "mdi:molecule-co", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "o3": ["Heweather_o3", "臭氧", "mdi:weather-cloudy", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER],
    "qlty": ["Heweather_qlty", "综合空气质量", "mdi:quality-high", " "],
    "disaster_warn": ["Heweather_disaster_warn", "灾害预警", "mdi:alert", " "],
    "air": ["suggestion_air", "空气污染扩散条件指数", "mdi:air-conditioner", " "],
    "comfortable": ["suggestion_comf", "舒适度指数", "mdi:human-greeting", " "],
    "cw": ["suggestion_cw", "洗车指数", "mdi:car", " "],
    "drsg": ["suggestion_drsg", "穿衣指数", "mdi:hanger", " "],
    "flu": ["suggestion_flu", "感冒指数", "mdi:biohazard", " "],
    "sport": ["suggestion_sport", "运动指数", "mdi:badminton", " "],
    "trav": ["suggestion_trav", "旅行指数", "mdi:wallet-travel", " "],
    "uv": ["suggestion_uv", "紫外线指数", "mdi:weather-sun-wireless", " "],
    "guomin": ["suggestion_guomin", "过敏指数", "mdi:sunglasses", " "],
    "kongtiao": ["suggestion_kongtiao", "空调开启指数", "mdi:air-conditioner", " "],
    "sunglass": ["suggestion_sunglass", "太阳镜指数", "mdi:sunglasses", " "],
    "fangshai": ["suggestion_fangshai", "防晒指数", "mdi:sun-protection-outline", " "],
    "liangshai": ["suggestion_liangshai", "晾晒指数", "mdi:tshirt-crew-outline", " "],
    "jiaotong": ["suggestion_jiaotong", "交通指数", "mdi:train-car", " "],
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
SENSOR_TYPES = {
    "temperature": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "温度",
        ATTR_UNIT_METRIC: UnitOfTemperature.CELSIUS,
        ATTR_UNIT_IMPERIAL: UnitOfTemperature.FAHRENHEIT,
    },
    "felt_temperature": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "体感温度",
        ATTR_UNIT_METRIC: UnitOfTemperature.CELSIUS,
        ATTR_UNIT_IMPERIAL: UnitOfTemperature.FAHRENHEIT,
    },
    "icon": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: None,
        ATTR_LABEL: "图标",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "text": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-cloudy",
        ATTR_LABEL: "天气描述",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "WindDir360": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_LABEL: "风向360",
        ATTR_UNIT_METRIC: DEGREE,
        ATTR_UNIT_IMPERIAL: DEGREE,
    },
    "WindDirection": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_LABEL: "风向",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "WindScale": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_LABEL: "风力等级",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    },
    "WindSpeed": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_LABEL: "风速",
        ATTR_UNIT_METRIC: UnitOfSpeed.KILOMETERS_PER_HOUR,
        ATTR_UNIT_IMPERIAL: UnitOfSpeed.MILES_PER_HOUR,
    },
    "humidity": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:water-percent",
        ATTR_LABEL: "湿度",
        ATTR_UNIT_METRIC: "%",
        ATTR_UNIT_IMPERIAL: "%",
    },
    "precipitation": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_LABEL: "当前小时累计雨量",
        ATTR_UNIT_METRIC: "mm",
        ATTR_UNIT_IMPERIAL: UnitOfLength.INCHES,
    },
    "pressure": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:gauge",
        ATTR_LABEL: "气压",
        ATTR_UNIT_METRIC: "Pa",
        ATTR_UNIT_IMPERIAL: "Pa",
    },
    "visibility": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-fog",
        ATTR_LABEL: "能见度",
        ATTR_UNIT_METRIC: UnitOfLength.KILOMETERS,
        ATTR_UNIT_IMPERIAL: UnitOfLength.MILES,
    },
    "cloudrate": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-cloudy",
        ATTR_LABEL: "云量",
        ATTR_UNIT_METRIC: "%",
        ATTR_UNIT_IMPERIAL: "%",
    },
    "dew": {
        ATTR_DEVICE_CLASS: SensorDeviceClass.TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: "露点温度",
        ATTR_UNIT_METRIC: UnitOfTemperature.CELSIUS,
        ATTR_UNIT_IMPERIAL: UnitOfTemperature.FAHRENHEIT,
    },
    "place": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:home-city",
        ATTR_LABEL: "地点",
        ATTR_UNIT_METRIC: None,
        ATTR_UNIT_IMPERIAL: None,
    }
}
