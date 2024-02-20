import logging
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    CONF_NAME,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import (
    ATTR_ICON,
    ATTR_LABEL,
    ATTRIBUTION,
    COORDINATOR,
    DOMAIN,
    MANUFACTURER,
    OPTIONAL_SENSORS,
    SENSOR_TYPES,
)

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data[CONF_NAME]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(HeweatherSensor(name, sensor, coordinator))

    async_add_entities(sensors, False)


class HeweatherSensor(Entity):
    def __init__(self, name, kind, coordinator, forecast_day=None):
        self._name = name
        self.kind = kind
        self.coordinator = coordinator
        self._device_class = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._unit_system = "Metric" if self.coordinator.data["is_metric"] == "metric:v2" else "Imperial"
        self.forecast_day = forecast_day

    @property
    def name(self):
        if self.forecast_day is not None:
            return f"{self._name} {FORECAST_SENSOR_TYPES[self.kind][ATTR_LABEL]} {self.forecast_day}d"
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def unique_id(self):
        _LOGGER.info("sensor_unique_id: %s", self.coordinator.data["location_key"])
        return f"{self.coordinator.data['location_key']}-{self.kind}".lower()

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
    def state(self):
        if self.kind == "temperature":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "felt_temperature":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "text":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "WindDir":
            return self.coordinator.data["result"]["realtime"]["wind"]["direction"]
        if self.kind == "WindDir360":
            return self.coordinator.data["result"]["realtime"]["wind"]["direction360"]
        if self.kind == "WindScale":
            return self.coordinator.data["result"]["realtime"]["wind"]["scale"]
        if self.kind == "WindSpeed":
            return self.coordinator.data["result"]["realtime"]["wind"]["speed"]
        if self.kind == "humidity":
            return round(float(self.coordinator.data["result"]["realtime"][self.kind]) * 100)
        if self.kind == "precipitation":
            return self.coordinator.data["result"]["realtime"]["precipitation"]["local"]["intensity"]
        if self.kind == "pressure":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "visibility":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "cloudrate":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "dew":
            return self.coordinator.data["result"]["realtime"][self.kind]
        if self.kind == "place":
            return self.coordinator.data["place"]

    @property
    def icon(self):
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def device_class(self):
        return SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]

    @property
    def unit_of_measurement(self):
        return SENSOR_TYPES[self.kind][self._unit_system]

    # @property
    # def extra_state_attributes(self):
    #     if self.kind == "ultraviolet":
    #         self._attrs["desc"] = self.coordinator.data["result"]["realtime"]["life_index"]["ultraviolet"]["desc"]
    #     elif self.kind == "comfort":
    #         self._attrs["desc"] = self.coordinator.data["result"]["realtime"]["life_index"]["comfort"]["desc"]
    #     elif self.kind == "place":
    #         self._attrs["desc"] = self.coordinator.data["place"]
    #     elif self.kind == "precipitation":
    #         self._attrs["datasource"] = self.coordinator.data["result"]["realtime"]["precipitation"]["local"][
    #             "datasource"]
    #         self._attrs["nearest_intensity"] = self.coordinator.data["result"]["realtime"]["precipitation"]["nearest"][
    #             "intensity"]
    #         self._attrs["nearest_distance"] = self.coordinator.data["result"]["realtime"]["precipitation"]["nearest"][
    #             "distance"]
    #     return self._attrs

    @property
    def entity_registry_enabled_default(self):
        return bool(self.kind not in OPTIONAL_SENSORS)

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()
