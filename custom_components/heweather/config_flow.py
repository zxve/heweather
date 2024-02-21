import logging

import requests
import json
from homeassistant.const import CONF_API_KEY, CONF_NAME, CONF_SENSORS
from collections import OrderedDict
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
)
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class HeweatherHandler(config_entries.ConfigFlow, domain=DOMAIN):
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HeweatherOptionsFlow(config_entry)

    def __init__(self):
        self._errors = {}

    # @asyncio.coroutine
    def get_data(self, url):
        json_text = requests.get(url).content
        resdata = json.loads(json_text)
        return resdata

    async def async_step_user(self, user_input=None):
        try:
            self._errors = {}
            if user_input is not None:
                existing = await self._check_existing(user_input[CONF_NAME])
                if existing:
                    return self.async_abort(reason="already_configured")

                url = str.format("https://devapi.qweather.com/{}/weather/now?location={},{}&key={}",
                                 user_input["api_version"],
                                 user_input["longitude"], user_input["latitude"], user_input["api_key"])
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
        try:
            api_version = "v7"
            data_schema = OrderedDict()
            data_schema[vol.Required(CONF_API_KEY)] = str
            data_schema[vol.Required(CONF_SENSORS)] = str
            data_schema[vol.Optional("api_version", default=api_version)] = str
            # data_schema[vol.Optional(CONF_LONGITUDE, default=self.hass.config.longitude)] = cv.longitude
            # data_schema[vol.Optional(CONF_LATITUDE, default=self.hass.config.latitude)] = cv.latitude
            data_schema[vol.Optional(CONF_NAME, default=self.hass.config.location_name)] = str
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
            )
        except Exception as e:
            raise e

    async def async_step_import(self, user_input):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _check_existing(self, host):
        for entry in self._async_current_entries():
            if host == entry.data.get(CONF_NAME):
                return True


class HeweatherOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_user()

    # async def async_step_user(self, user_input=None):
    #     if user_input is not None:
    #         return self.async_create_entry(title="", data=user_input)
    #
    #     return self.async_show_form(
    #         step_id="user",
    #         data_schema=vol.Schema(
    #             {
    #                 vol.Optional(
    #                     CONF_DAILYSTEPS,
    #                     default=self.config_entry.options.get(CONF_DAILYSTEPS, 5),
    #                 ): vol.All(vol.Coerce(int), vol.Range(min=5, max=15)),
    #                 vol.Optional(
    #                     CONF_HOURLYSTEPS,
    #                     default=self.config_entry.options.get(CONF_HOURLYSTEPS, 24),
    #                 ): vol.All(vol.Coerce(int), vol.Range(min=24, max=360)),
    #                 vol.Optional(
    #                     CONF_STARTTIME,
    #                     default=self.config_entry.options.get(CONF_STARTTIME, 0),
    #                 ): vol.All(vol.Coerce(int), vol.Range(min=-5, max=0)),
    #                 vol.Optional(
    #                     CONF_ALERT,
    #                     default=self.config_entry.options.get(CONF_ALERT, True),
    #                 ): bool
    #             }
    #         ),
    #     )
