import logging
import aiohttp

import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.const import CONF_NAME, ATTR_ATTRIBUTION
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    OPTIONS,
    MANUFACTURER, DISASTER_LEVEL, OPTIONAL_SENSORS, TIME_BETWEEN_UPDATES, CONF_API_KEY, CONF_API_VERSION,
    CONF_LONGITUDE, CONF_LATITUDE, CONF_DISASTER_MSG, CONF_DISASTER_LEVEL, CONF_ALERT
)

# PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    try:
        name = config_entry.data[CONF_NAME]
        api_key = config_entry.data[CONF_API_KEY]
        api_version = config_entry.data[CONF_API_VERSION]
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        disaster_msg = config_entry.options.get(CONF_DISASTER_MSG, "title")
        disaster_level = config_entry.options.get(CONF_DISASTER_LEVEL, 1)
        alert = config_entry.options.get(CONF_ALERT, True)
        location_key = config_entry.unique_id
        is_metric = "metric:v2"
        if hass.config.units is METRIC_SYSTEM:
            is_metric = "metric:v2"
        else:
            is_metric = "imperial"

        wsdata = await weather_sensor_data_update(api_version, longitude, latitude, api_key, disaster_msg,
                                                  disaster_level, alert)
        async_track_time_interval(hass, weather_sensor_data_update, TIME_BETWEEN_UPDATES)

        sdata = await suggestion_data_update(hass, api_version, longitude, latitude, api_key, alert)
        async_track_time_interval(hass, suggestion_data_update, TIME_BETWEEN_UPDATES)

        sensors = []
        for sensor in OPTIONS.keys():
            sensors.append(HfweatherSensor(name, sensor,
                                           {"location_key": location_key, "is_metric": is_metric, "wsdata": wsdata,
                                            "sdata": sdata}))

        async_add_entities(sensors, False)
    except Exception as e:
        raise e


class HfweatherSensor(CoordinatorEntity, SensorEntity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self, name, option, coordinator):
        """初始化."""
        self.coordinator = coordinator
        self.wsdata = coordinator.data["wsdata"]
        self.sdata = coordinator.data["sdata"]
        self.alert = coordinator.data.get("alert", True)
        opobj = OPTIONS[option]
        self._device_class = opobj[0] if opobj[0] else ''
        # self._name = name
        self._name = f"{name} {opobj[1]}"
        self._icon = opobj[2]
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._unit_of_measurement = opobj[3] if self.coordinator.data["is_metric"] == "metric:v2" else opobj[4]
        self._type = option
        self._updatetime = self.wsdata["updatetime"]
        self.location_key = coordinator.data["location_key"]
        # self._attr_unique_id = f"{coordinator.data['location_key']}-{self._type}"
        self._attr_unique_id = f"{self.location_key}-{self._type}".lower()  # 最好前面和weather对象保持一致，疑似需要
        super().__init__(coordinator, context=None)

    # @property
    # def extra_state_attributes(self):
    #     """Return entity specific state attributes."""
    #     return self._attributes

    @property
    def name(self):
        return self._name

    # @property
    # def attribution(self):
    #     """Return the attribution."""
    #     return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return self._attr_unique_id

    @property
    def device_class(self):
        return self._device_class

    @property
    def device_info(self):
        """Return the device info."""
        return {
            # 踩坑。。。。HfweatherSensor要注册到Hfweather设备，这里到identifiers要和HfweatherEntity保持一致
            "identifiers": {(DOMAIN, self.location_key)},
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE
        }

    @property
    def state(self):
        if self.alert:
            if self._type in self.wsdata:
                return self.wsdata[self._type]
            elif self._type in self.sdata:
                return self.sdata[self._type]

    @property
    def icon(self):
        """返回icon属性."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回unit_of_measuremeng属性."""
        return self._unit_of_measurement

    @property
    def entity_registry_enabled_default(self):
        return bool(self._type not in OPTIONAL_SENSORS)

    # async def async_added_to_hass(self):
    #     self.async_on_remove(
    #         self.coordinator.async_add_listener(self.async_write_ha_state)
    #     )

    # async def async_update(self):
    #     """update函数变成了async_update."""
    #     self._updatetime = self.wsdata["updatetime"]
    #     if self._type == "temprature":
    #         self._state = self.wsdata["temprature"]
    #     elif self._type == "humidity":
    #         self._state = self.wsdata["humidity"]
    #     elif self._type == "feelsLike":
    #         self._state = self.wsdata["feelsLike"]
    #     elif self._type == "text":
    #         self._state = self.wsdata["text"]
    #     elif self._type == "windDir":
    #         self._state = self.wsdata["windDir"]
    #     elif self._type == "windScale":
    #         self._state = self.wsdata["windScale"]
    #     elif self._type == "windSpeed":
    #         self._state = self.wsdata["windSpeed"]
    #     elif self._type == "precip":
    #         self._state = self.wsdata["precip"]
    #     elif self._type == "pressure":
    #         self._state = self.wsdata["pressure"]
    #     elif self._type == "vis":
    #         self._state = self.wsdata["vis"]
    #     elif self._type == "dew":
    #         self._state = self.wsdata["dew"]
    #     elif self._type == "cloud":
    #         self._state = self.wsdata["cloud"]
    #     elif self._type == "category":
    #         self._state = self.wsdata["category"]
    #     elif self._type == "primary":
    #         self._state = self.wsdata["primary"]
    #     elif self._type == "level":
    #         self._state = self.wsdata["level"]
    #     elif self._type == "pm10":
    #         self._state = self.wsdata["pm10"]
    #     elif self._type == "pm25":
    #         self._state = self.wsdata["pm25"]
    #     elif self._type == "no2":
    #         self._state = self.wsdata["no2"]
    #     elif self._type == "so2":
    #         self._state = self.wsdata["so2"]
    #     elif self._type == "co":
    #         self._state = self.wsdata["co"]
    #     elif self._type == "o3":
    #         self._state = self.wsdata["o3"]
    #     elif self._type == "qlty":
    #         self._state = self.wsdata["qlty"]
    #     elif self._type == "disaster_warn":
    #         if len(self.wsdata["disaster_warn"]) > 10:
    #             self._state = 'on'
    #             self._attributes["states"] = self.wsdata["disaster_warn"]
    #         else:
    #             self._state = 'off'
    #             self._attributes["states"] = self.wsdata["disaster_warn"]
    #     # life-suggestion
    #     elif self._type == "air":
    #         self._state = self.sdata["air"][0]
    #         self._attributes["states"] = self.sdata["air"][1]
    #     elif self._type == "comf":
    #         self._state = self.sdata["comf"][0]
    #         self._attributes["states"] = self.sdata["comf"][1]
    #     elif self._type == "cw":
    #         self._state = self.sdata["cw"][0]
    #         self._attributes["states"] = self.sdata["cw"][1]
    #     elif self._type == "drsg":
    #         self._state = self.sdata["drsg"][0]
    #         self._attributes["states"] = self.sdata["drsg"][1]
    #     elif self._type == "flu":
    #         self._state = self.sdata["flu"][0]
    #         self._attributes["states"] = self.sdata["flu"][1]
    #     elif self._type == "sport":
    #         self._state = self.sdata["sport"][0]
    #         self._attributes["states"] = self.sdata["sport"][1]
    #     elif self._type == "trav":
    #         self._state = self.sdata["trav"][0]
    #         self._attributes["states"] = self.sdata["trav"][1]
    #     elif self._type == "uv":
    #         self._state = self.sdata["uv"][0]
    #         self._attributes["states"] = self.sdata["uv"][1]
    #     elif self._type == "guomin":
    #         self._state = self.sdata["guomin"][0]
    #         self._attributes["states"] = self.sdata["guomin"][1]
    #     elif self._type == "kongtiao":
    #         self._state = self.sdata["kongtiao"][0]
    #         self._attributes["states"] = self.sdata["kongtiao"][1]
    #     elif self._type == "liangshai":
    #         self._state = self.sdata["liangshai"][0]
    #         self._attributes["states"] = self.sdata["liangshai"][1]
    #     elif self._type == "fangshai":
    #         self._state = self.sdata["fangshai"][0]
    #         self._attributes["states"] = self.sdata["fangshai"][1]
    #     elif self._type == "sunglass":
    #         self._state = self.sdata["uv"][0]
    #         self._attributes["states"] = self.sdata["uv"][1]
    #     elif self._type == "jiaotong":
    #         self._state = self.sdata["jiaotong"][0]
    #         self._attributes["states"] = self.sdata["jiaotong"][1]


async def weather_sensor_data_update(api_version, longitude, latitude, key, disaster_msg, disaster_level, alert):
    if not alert:
        return {"alert": False}
    data = {}

    weather_now_url = f"https://devapi.qweather.com/{api_version}/weather/now?location={longitude},{latitude}&key={key}"
    air_now_url = f"https://devapi.qweather.com/{api_version}/air/now?location={longitude},{latitude}&key={key}"
    disaster_warn_url = f"https://devapi.qweather.com/{api_version}/warning/now?location={longitude},{latitude}&key={key}"
    params = {"location": f"{longitude}/{latitude}", "key": key, }
    place = None
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(weather_now_url) as response:
                json_data = await response.json()
                weather = json_data["now"]
                place = json_data["fxLink"].split("/")[-1].split("-")[0]
            async with session.get(air_now_url) as response:
                json_data = await response.json()
                air = json_data["now"]
            async with session.get(disaster_warn_url) as response:
                json_data = await response.json()
                disaster_warn = json_data["warning"]
    except Exception as e:
        raise e

    # 根据http返回的结果，更新数据
    data["temperature"] = weather["temp"]
    data["humidity"] = weather["humidity"]
    data["feelsLike"] = weather["feelsLike"]
    data["text"] = weather["text"]
    data["windDir"] = weather["windDir"]
    data["windScale"] = weather["windScale"]
    data["windSpeed"] = weather["windSpeed"]
    data["precip"] = weather["precip"]
    data["pressure"] = weather["pressure"]
    data["vis"] = weather["vis"]
    data["cloud"] = weather["cloud"]
    data["dew"] = weather["dew"]
    data["place"] = place
    data["updatetime"] = weather["obsTime"]
    data["category"] = air["category"]
    data["pm25"] = air["pm2p5"]
    data["pm10"] = air["pm10"]
    data["primary"] = air["primary"]
    data["level"] = air["level"]
    data["no2"] = air["no2"]
    data["so2"] = air["so2"]
    data["co"] = air["co"]
    data["o3"] = air["o3"]
    data["qlty"] = air["aqi"]

    allmsg = ''
    titlemsg = ''
    for i in disaster_warn:
        # if DISASTER_LEVEL[i["severity"]] >= 订阅等级:
        if DISASTER_LEVEL[i["severity"]] >= int(disaster_level):
            allmsg = f'{allmsg}{i["title"]}:{i["text"]}||'
            titlemsg = f'{titlemsg}{i["title"]}||'

    if len(titlemsg) < 5:
        disaster_warn = f'近日无{disaster_level}级及以上灾害'
    # if(订阅标题)
    elif disaster_msg == 'title':
        disaster_warn = titlemsg
    else:
        disaster_warn = allmsg
    data["disaster_warn"] = disaster_warn
    return data


async def suggestion_data_update(hass, api_version, longitude, latitude, key, alert):
    if not alert:
        return {"alert": False}

    url = f"https://devapi.qweather.com/{api_version}/indices/1d?location={longitude},{latitude}&key={key}&type=0"
    params = {"location": f"{longitude}/{latitude}", "key": key, "type": 0}
    updatetime = ["1", "1"]
    data = {
        "air": ["1", "1"],
        "comf": ["1", "1"],
        "cw": ["1", "1"],
        "drsg": ["1", "1"],
        "flu": ["1", "1"],
        "sport": ["1", "1"],
        "trav": ["1", "1"],
        "uv": ["1", "1"],
    }

    try:
        session = async_get_clientsession(hass)
        with async_timeout.timeout(10):
            response = await session.get(url)
    except Exception as e:
        raise e
    if response.status != 200:
        _LOGGER.error("Error while accessing: %s, status=%d", url, response.status)
        return

    result = await response.json()

    if result is None:
        _LOGGER.error("Request api Error")
        return
    elif result["code"] != "200":
        _LOGGER.error("Error API return, code=%s,url=%s",
                      result["code"], url)
        return

    # 根据http返回的结果，更新数据
    all_result = result["daily"]
    updatetime = result["updateTime"]
    for i in all_result:
        if i["type"] == "1":
            data["sport"] = [i["category"], i["text"]]

        if i["type"] == "10":
            data["air"] = [i["category"], i["text"]]

        if i["type"] == "8":
            data["comf"] = [i["category"], i["text"]]

        if i["type"] == "2":
            data["cw"] = [i["category"], i["text"]]

        if i["type"] == "3":
            data["drsg"] = [i["category"], i["text"]]

        if i["type"] == "9":
            data["flu"] = [i["category"], i["text"]]

        if i["type"] == "6":
            data["trav"] = [i["category"], i["text"]]

        if i["type"] == "5":
            data["uv"] = [i["category"], i["text"]]

        if i["type"] == "7":
            data["guomin"] = [i["category"], i["text"]]

        if i["type"] == "11":
            data["kongtiao"] = [i["category"], i["text"]]

        if i["type"] == "12":
            data["sunglass"] = [i["category"], i["text"]]

        if i["type"] == "14":
            data["liangshai"] = [i["category"], i["text"]]

        if i["type"] == "15":
            data["jiaotong"] = [i["category"], i["text"]]

        if i["type"] == "16":
            data["fangshai"] = [i["category"], i["text"]]
    return data
