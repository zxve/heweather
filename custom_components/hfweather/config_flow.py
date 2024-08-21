'''
输入参数配置
'''
import json
import logging
from collections import OrderedDict

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
)
from homeassistant.core import callback

from .const import (
    CONF_SUGG,
    CONF_DAILYSTEPS,
    CONF_DISASTER_LEVEL,
    # CONF_DISASTER_MSG,
    CONF_HOURLYSTEPS,
    DOMAIN, NAME,
    CONF_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class HfweatherHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """初始化设置模块"""
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HfweatherOptionsFlow(config_entry)

    def __init__(self):
        self._errors = {}

    # @asyncio.coroutine
    def get_data(self, url):
        """请求url"""
        json_text = requests.get(url, timeout=100).content
        resdata = json.loads(json_text)
        return resdata

    async def async_step_user(self, user_input=None):
        “”“获取第一次数据”“”
        try:
            self._errors = {}
            if user_input is not None:
                # 若location则使用，否则使用user_input的经纬度
                if user_input["location"] != 'None':
                    # lat, lon = self.hass.states.get(user_input["location"]).state.split(",")
                    lat, lon = self.hass.states.get(user_input["location"]).attributes["location"]
                    user_input["latitude"] = lat
                    user_input["longitude"] = lon

                existing = await self._check_existing(user_input[CONF_NAME])
                if existing:
                    return self.async_abort(reason="already_configured")

                url = str.format(
                    "https://devapi.qweather.com/{}/weather/now?location={},{}&key={}",
                    user_input["api_version"],
                    user_input["longitude"],
                    user_input["latitude"],
                    user_input["api_key"])
                redata = await self.hass.async_add_executor_job(self.get_data, url)
                status = redata['code']
                if status == '200':
                    await self.async_set_unique_id(
                        f"{user_input['longitude']}-{user_input['latitude']}".replace(".", "_"))
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME], data=user_input
                    )
                else:
                    self._errors["base"] = "communication"

                return await self._show_config_form(user_input)

            return await self._show_config_form(user_input)
        except Exception as e:
            # traceback.print_exc()
            raise e

    async def _show_config_form(self, user_input):
        """第一次配置参数"""
        try:
            data_schema = OrderedDict()
            data_schema[vol.Required(CONF_API_KEY)] = str
            data_schema[vol.Optional("location", default="sensor.xxx_geocoded_location")] = str
            data_schema[vol.Optional("api_version", default="v7")] = str
            data_schema[vol.Optional(CONF_LONGITUDE,
                                     default=self.hass.config.longitude)] = cv.longitude
            data_schema[vol.Optional(CONF_LATITUDE,
                                     default=self.hass.config.latitude)] = cv.latitude

            data_schema[vol.Optional(CONF_NAME, default=NAME)] = str
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
            )
        except Exception as e:
            raise e

    async def async_step_import(self, user_input):
        """Import a config entry."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _check_existing(self, host):
        for entry in self._async_current_entries():
            if host == entry.data.get(CONF_NAME):
                return True


class HfweatherOptionsFlow(config_entries.OptionsFlow):
    """选项设置"""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """init by user"""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DAILYSTEPS,
                        default=self.config_entry.options.get(CONF_DAILYSTEPS, 7),
                    ): vol.All(vol.Coerce(int), vol.Range(min=3, max=7)),
                    vol.Optional(
                        CONF_HOURLYSTEPS,
                        default=self.config_entry.options.get(CONF_HOURLYSTEPS, 24),
                    ): vol.All(vol.Coerce(int), vol.Range(min=24, max=168)),
                    vol.Optional(
                        CONF_SUGG,
                        default=self.config_entry.options.get(CONF_SUGG, False),
                    ): bool,
                    vol.Optional(
                        CONF_INTERVAL,
                        default=self.config_entry.options.get(CONF_INTERVAL, 720),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60)),
                    vol.Optional(
                        CONF_DISASTER_LEVEL,
                        default=self.config_entry.options.get(CONF_DISASTER_LEVEL, 0),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                    # vol.Optional(
                    #     CONF_DISASTER_MSG,
                    #     default=self.config_entry.options.get(CONF_DISASTER_MSG, 24),
                    # ): vol.All(vol.Coerce(str), "title"),
                }
            ),
        )
