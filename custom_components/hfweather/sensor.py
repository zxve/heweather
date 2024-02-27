import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.const import CONF_NAME, ATTR_ATTRIBUTION
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    OPTIONS,
    MANUFACTURER, ATTR_LABEL, OPTIONAL_SENSORS,
)

# PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    try:
        name = config_entry.data[CONF_NAME]

        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        sensors = []
        for sensor in OPTIONS.keys():
            sensors.append(HfweatherSensor(name, sensor, coordinator))

        async_add_entities(sensors, False)
    except Exception as e:
        raise e


class HfweatherSensor(CoordinatorEntity, SensorEntity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self, name, option, coordinator, forecast_day=None):
        """初始化."""
        _LOGGER.info("zxve 010")

        self.coordinator = coordinator
        self.wsdata = coordinator.data["wsdata"]
        self.sdata = coordinator.data["sdata"]
        _LOGGER.info(self.wsdata)
        _LOGGER.info("zxve 011")
        _LOGGER.info(self.sdata)

        self.alert = coordinator.data.get("alert", True)
        opobj = OPTIONS[option]
        self._device_class = opobj[0] if opobj[0] else ''
        # self._name = name
        self._name = f"{name} {opobj[1]}"
        self._icon = opobj[2]
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._unit_of_measurement = opobj[3] if self.coordinator.data["is_metric"] == "metric:v2" else opobj[4]
        self.forecast_day = forecast_day
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
        """返回实体的名字."""
        """Return the name."""
        if self.forecast_day is not None:
            return f"{self._name} {FORECAST_SENSOR_TYPES[self.kind][ATTR_LABEL]} {self.forecast_day}d"
        # return f"{self._name} {OPTIONS[self._type][1]}"
        return f"{self._name}"

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
