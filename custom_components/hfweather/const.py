from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    UnitOfLength,
    UnitOfTemperature,
    DEGREE, UnitOfSpeed
)

# 方便直接使用Home Assistant Brands上面的和风天气图标
DOMAIN = "heweather"

PLATFORMS = ["sensor"]
REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "weather.py",
    "config_flow.py",
    "services.yaml",
    "translations/en.json",
]
VERSION = "0.1.0"
ISSUE_URL = ""

STARTUP = """

"""

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
