'''
sensor platform配置
'''
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.const import CONF_NAME, ATTR_ATTRIBUTION


from .const import (
    ATTRIBUTION, DOMAIN, OPTIONS, MANUFACTURER, OPTIONAL_SENSORS, SUG_OPTIONS,
    CONF_ALERT, COORDINATOR
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """xxx"""
    try:
        name = config_entry.data[CONF_NAME]
        alert = config_entry.options.get(CONF_ALERT, True)

        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        sensors = []
        options = OPTIONS.update(SUG_OPTIONS) if alert else OPTIONS

        for sensor in options:
            sensors.append(HfweatherSensor(name, sensor, alert, coordinator))

        async_add_entities(sensors, update_before_add=False)
    except Exception as e:
        _LOGGER.info("hew- sensor setup entry: %s", e)
        raise e


class HfweatherSensor(SensorEntity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self, name, sensor, alert, coordinator):
        """初始化."""
        self.wsdata = coordinator.data["wsdata"]
        self.sgdata = coordinator.data["sgdata"]
        self.coordinator = coordinator
        self.alert = alert
        opobj = OPTIONS[sensor]
        self._device_class = opobj[0] if opobj[0] else ''
        self._name = f"{name} {opobj[1]}"
        self._icon = opobj[2]
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._unit_of_measurement = opobj[3] if coordinator.data["is_metric"] == "metric:v2" else opobj[4]
        self._type = sensor
        self._updatetime = self.wsdata["updatetime"]
        self.location_key = coordinator.data["location_key"]
        # 最好前面和weather对象保持一致，疑似需要
        self._attr_unique_id = f"{self.location_key}-{self._type}".lower()

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return True

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

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
        """xxx"""
        if self._type in self.wsdata:
            return self.wsdata[self._type]
        elif self._type in self.sgdata:
            if self.alert:
                return self.sgdata[self._type]

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

    # @property
    # def entity_registry_enabled_default(self):
    #     """Return if the entity should be enabled when first added to the entity registry."""
    #     return bool(self._type not in OPTIONAL_SENSORS)

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update Colorfulclouds entity."""
        await self.coordinator.async_request_refresh()
