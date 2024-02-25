import asyncio

import aiohttp
import logging

from async_timeout import timeout

from homeassistant.const import CONF_API_KEY
import async_timeout
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import (
    CONF_API_VERSION,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER, CONF_LOCATION, CONF_LONGITUDE, CONF_LATITUDE, PLATFORMS, TIME_BETWEEN_UPDATES,
    CONDITION_CLASSES, DISASTER_LEVEL, CONF_DISASTER_MSG, CONF_DISASTER_LEVEL, CONF_DAILYSTEPS, CONF_HOURLYSTEPS,
    CONF_ALERT, CONF_STARTTIME,
)

_LOGGER = logging.getLogger(__name__)


# _LOGGER.info("zxve 000")


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    try:
        api_key = config_entry.data[CONF_API_KEY]
        location = config_entry.data[CONF_LOCATION]
        location_key = config_entry.unique_id
        longitude = config_entry.data[CONF_LONGITUDE]
        latitude = config_entry.data[CONF_LATITUDE]
        api_version = config_entry.data[CONF_API_VERSION]
        disaster_msg = config_entry.options[CONF_DISASTER_MSG]
        disaster_level = config_entry.options[CONF_DISASTER_LEVEL]
        dailysteps = config_entry.options.get(CONF_DAILYSTEPS, 3)
        hourlysteps = config_entry.options.get(CONF_HOURLYSTEPS, 24)
        alert = config_entry.options.get(CONF_ALERT, True)
        starttime = config_entry.options.get(CONF_STARTTIME, 0)

        coordinator = HfCoordinator(hass, all_apis, api_key, api_version, location_key, longitude, latitude,
                                    dailysteps, hourlysteps, starttime, alert, disaster_msg, disaster_level)
        await coordinator.async_refresh()

        _LOGGER.info(f"zxve 000: {coordinator.data}")

        if not coordinator.last_update_success:
            raise ConfigEntryNotReady

        undo_listener = config_entry.add_update_listener(update_listener)

        hass.data[DOMAIN][config_entry.entry_id] = {
            COORDINATOR: coordinator,
            UNDO_UPDATE_LISTENER: undo_listener,
        }

        for component in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, component)
            )

        return True
    except Exception as e:
        raise e


async def async_unload_entry(hass, config_entry):
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    await hass.config_entries.async_reload(config_entry.entry_id)


class HfCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, my_apis, api_key, api_version, location_key, longitude, latitude, dailysteps, hourlysteps,
                 starttime, alert, disaster_msg,
                 disaster_level):
        self.hass = hass
        self.location_key = location_key
        self.longitude = longitude
        self.latitude = latitude
        self.api_version = api_version
        self.api_key = api_key
        self.dailysteps = dailysteps
        self.hourlysteps = hourlysteps
        self.starttime = starttime
        self.alert = alert
        self.disaster_msg = disaster_msg
        self.disaster_level = disaster_level
        self.is_metric = "metric:v2"
        if hass.config.units is METRIC_SYSTEM:
            self.is_metric = "metric:v2"
        else:
            self.is_metric = "imperial"

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=TIME_BETWEEN_UPDATES)
        self.my_apis = my_apis

    async def _async_update_data(self):
        try:
            async with timeout(100):
                resdata = await self.my_apis(self.hass, self.api_version, self.longitude, self.latitude, self.api_key,
                                             self.dailysteps, self.hourlysteps, self.starttime, self.alert,
                                             self.disaster_msg, self.disaster_level)
        except Exception as e:
            raise e
        return {**resdata, "location_key": self.location_key, "is_metric": self.is_metric}


async def all_apis(hass, api_version, longitude, latitude, key, dailysteps, hourlysteps, starttime, alert, disaster_msg,
                   disaster_level):
    try:
        async with timeout(50):
            wdata = await weather_data_update(api_version, longitude, latitude, key, dailysteps, hourlysteps)
            wsdata = await weather_sensor_data_update(api_version, longitude, latitude, key, disaster_msg,
                                                      disaster_level, alert)
            sdata = await suggestion_data_update(hass, api_version, longitude, latitude, key, alert)

    except Exception as e:
        raise e

    return {"wdata": wdata, "wsdata": wsdata, "sdata": sdata}


async def weather_data_update(api_version, longitude, latitude, key, dailysteps, hourlysteps):
    forecast_url = f"https://devapi.qweather.com/{api_version}/weather/{dailysteps}d?location={longitude},{latitude}&key={key}"
    weather_now_url = f"https://devapi.qweather.com/{api_version}/weather/now?location={longitude},{latitude}&key={key}"
    forecast_hourly_url = f"https://devapi.qweather.com/{api_version}/weather/{hourlysteps}h?location={longitude},{latitude}&key={key}"
    params = {"location": f"{longitude}/{latitude}", "key": key}
    data = {}
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(weather_now_url) as response:
                json_data = await response.json()
                weather = json_data["now"]
            async with session.get(forecast_url) as response:
                json_data = await response.json()
                forecast = json_data
            async with session.get(forecast_hourly_url) as response:
                json_data = await response.json()
                forecast_hourly = json_data

    except Exception as e:
        raise e

    data["temperature"] = float(weather["temp"])
    data["humidity"] = float(weather["humidity"])
    data["pressure"] = weather["pressure"]
    data["condition"] = weather["text"]
    data["wind_speed"] = weather["windSpeed"]
    data["wind_bearing"] = weather["windDir"]
    data["visibility"] = weather["vis"]
    data["precipitation"] = float(weather["precip"])

    data["feelslike"] = float(weather["feelsLike"])
    data["dew"] = float(weather["dew"])
    data["cloud"] = int(weather["cloud"])

    data["windScale"] = weather["windScale"]
    data["updatetime"] = weather["obsTime"]

    datemsg = forecast["daily"]

    # forec_cond = []
    # forec_text = []
    daily_tmp = []
    for n in range(dailysteps):
        for i, j in CONDITION_CLASSES.items():
            if datemsg[n]["textDay"] in j:
                # forec_cond.append(i)
                # forec_text.append(datemsg[n]["textDay"])

                daily_tmp.append(
                    [i, int(datemsg[n]["tempMax"]), int(datemsg[n]["tempMin"]), datemsg[n]["textDay"]]
                )
    data["forecast"] = daily_tmp
    # data["forecast"] = [
    #     [forec_cond[0], int(datemsg[0]["tempMax"]), int(datemsg[0]["tempMin"]), forec_text[0]],
    #     [forec_cond[1], int(datemsg[1]["tempMax"]), int(datemsg[1]["tempMin"]), forec_text[1]],
    #     [forec_cond[2], int(datemsg[2]["tempMax"]), int(datemsg[2]["tempMin"]), forec_text[2]],
    #     [forec_cond[3], int(datemsg[3]["tempMax"]), int(datemsg[3]["tempMin"]), forec_text[3]],
    #     [forec_cond[4], int(datemsg[4]["tempMax"]), int(datemsg[4]["tempMin"]), forec_text[4]],
    #     [forec_cond[5], int(datemsg[5]["tempMax"]), int(datemsg[5]["tempMin"]), forec_text[5]],
    #     [forec_cond[6], int(datemsg[6]["tempMax"]), int(datemsg[6]["tempMin"]), forec_text[6]]
    # ]

    hourlymsg = forecast_hourly["hourly"]
    # forecast_hourly = []
    # forec_text = []
    hourly_tmp = []
    for n in range(hourlysteps):
        for i, j in CONDITION_CLASSES.items():
            if hourlymsg[n]["text"] in j:
                # forecast_hourly.append(i)
                # forec_text.append(hourlymsg[n]["text"])

                hourly_tmp.append(
                    [i, float(hourlymsg[n]["temp"]), float(hourlymsg[n]["humidity"]),
                     float(hourlymsg[n]["precip"]), hourlymsg[n]["windDir"], int(hourlymsg[n]["windSpeed"]),
                     float(hourlymsg[n]["pop"]), hourlymsg[n]["text"]]
                )
    data["forecast_hourly"] = hourly_tmp
    # data["forecast_hourly"] = [
    #     [forecast_hourly[0], float(hourlymsg[0]["temp"]), float(hourlymsg[0]["humidity"]),
    #      float(hourlymsg[0]["precip"]), hourlymsg[0]["windDir"], int(hourlymsg[0]["windSpeed"]),
    #      float(hourlymsg[0]["pop"]), forec_text[0]],
    #     [forecast_hourly[1], float(hourlymsg[1]["temp"]), float(hourlymsg[1]["humidity"]),
    #      float(hourlymsg[1]["precip"]), hourlymsg[1]["windDir"], int(hourlymsg[1]["windSpeed"]),
    #      float(hourlymsg[1]["pop"]), forec_text[1]],
    #     [forecast_hourly[2], float(hourlymsg[2]["temp"]), float(hourlymsg[2]["humidity"]),
    #      float(hourlymsg[2]["precip"]), hourlymsg[2]["windDir"], int(hourlymsg[2]["windSpeed"]),
    #      float(hourlymsg[2]["pop"]), forec_text[2]],
    #     [forecast_hourly[3], float(hourlymsg[3]["temp"]), float(hourlymsg[3]["humidity"]),
    #      float(hourlymsg[3]["precip"]), hourlymsg[3]["windDir"], int(hourlymsg[3]["windSpeed"]),
    #      float(hourlymsg[3]["pop"]), forec_text[3]],
    #     [forecast_hourly[4], float(hourlymsg[4]["temp"]), float(hourlymsg[4]["humidity"]),
    #      float(hourlymsg[4]["precip"]), hourlymsg[4]["windDir"], int(hourlymsg[4]["windSpeed"]),
    #      float(hourlymsg[4]["pop"]), forec_text[4]],
    #     [forecast_hourly[5], float(hourlymsg[5]["temp"]), float(hourlymsg[5]["humidity"]),
    #      float(hourlymsg[5]["precip"]), hourlymsg[5]["windDir"], int(hourlymsg[5]["windSpeed"]),
    #      float(hourlymsg[5]["pop"]), forec_text[5]],
    #     [forecast_hourly[6], float(hourlymsg[6]["temp"]), float(hourlymsg[6]["humidity"]),
    #      float(hourlymsg[6]["precip"]), hourlymsg[6]["windDir"], int(hourlymsg[6]["windSpeed"]),
    #      float(hourlymsg[6]["pop"]), forec_text[6]],
    #     [forecast_hourly[7], float(hourlymsg[7]["temp"]), float(hourlymsg[7]["humidity"]),
    #      float(hourlymsg[7]["precip"]), hourlymsg[7]["windDir"], int(hourlymsg[7]["windSpeed"]),
    #      float(hourlymsg[7]["pop"]), forec_text[7]],
    #     [forecast_hourly[8], float(hourlymsg[8]["temp"]), float(hourlymsg[8]["humidity"]),
    #      float(hourlymsg[8]["precip"]), hourlymsg[8]["windDir"], int(hourlymsg[8]["windSpeed"]),
    #      float(hourlymsg[8]["pop"]), forec_text[8]],
    #     [forecast_hourly[9], float(hourlymsg[9]["temp"]), float(hourlymsg[9]["humidity"]),
    #      float(hourlymsg[9]["precip"]), hourlymsg[9]["windDir"], int(hourlymsg[9]["windSpeed"]),
    #      float(hourlymsg[9]["pop"]), forec_text[9]],
    #     [forecast_hourly[10], float(hourlymsg[10]["temp"]), float(hourlymsg[10]["humidity"]),
    #      float(hourlymsg[10]["precip"]), hourlymsg[10]["windDir"], int(hourlymsg[10]["windSpeed"]),
    #      float(hourlymsg[10]["pop"]), forec_text[10]],
    #     [forecast_hourly[11], float(hourlymsg[11]["temp"]), float(hourlymsg[11]["humidity"]),
    #      float(hourlymsg[11]["precip"]), hourlymsg[11]["windDir"], int(hourlymsg[11]["windSpeed"]),
    #      float(hourlymsg[11]["pop"]), forec_text[11]],
    #     [forecast_hourly[12], float(hourlymsg[12]["temp"]), float(hourlymsg[12]["humidity"]),
    #      float(hourlymsg[12]["precip"]), hourlymsg[12]["windDir"], int(hourlymsg[12]["windSpeed"]),
    #      float(hourlymsg[12]["pop"]), forec_text[12]],
    #     [forecast_hourly[13], float(hourlymsg[13]["temp"]), float(hourlymsg[13]["humidity"]),
    #      float(hourlymsg[13]["precip"]), hourlymsg[13]["windDir"], int(hourlymsg[13]["windSpeed"]),
    #      float(hourlymsg[13]["pop"]), forec_text[13]],
    #     [forecast_hourly[14], float(hourlymsg[14]["temp"]), float(hourlymsg[14]["humidity"]),
    #      float(hourlymsg[14]["precip"]), hourlymsg[14]["windDir"], int(hourlymsg[14]["windSpeed"]),
    #      float(hourlymsg[14]["pop"]), forec_text[14]],
    #     [forecast_hourly[15], float(hourlymsg[15]["temp"]), float(hourlymsg[15]["humidity"]),
    #      float(hourlymsg[15]["precip"]), hourlymsg[15]["windDir"], int(hourlymsg[15]["windSpeed"]),
    #      float(hourlymsg[15]["pop"]), forec_text[15]],
    #     [forecast_hourly[16], float(hourlymsg[16]["temp"]), float(hourlymsg[16]["humidity"]),
    #      float(hourlymsg[16]["precip"]), hourlymsg[16]["windDir"], int(hourlymsg[16]["windSpeed"]),
    #      float(hourlymsg[16]["pop"]), forec_text[16]],
    #     [forecast_hourly[17], float(hourlymsg[17]["temp"]), float(hourlymsg[17]["humidity"]),
    #      float(hourlymsg[17]["precip"]), hourlymsg[17]["windDir"], int(hourlymsg[17]["windSpeed"]),
    #      float(hourlymsg[17]["pop"]), forec_text[17]],
    #     [forecast_hourly[18], float(hourlymsg[18]["temp"]), float(hourlymsg[18]["humidity"]),
    #      float(hourlymsg[18]["precip"]), hourlymsg[18]["windDir"], int(hourlymsg[18]["windSpeed"]),
    #      float(hourlymsg[18]["pop"]), forec_text[18]],
    #     [forecast_hourly[19], float(hourlymsg[19]["temp"]), float(hourlymsg[19]["humidity"]),
    #      float(hourlymsg[19]["precip"]), hourlymsg[19]["windDir"], int(hourlymsg[19]["windSpeed"]),
    #      float(hourlymsg[19]["pop"]), forec_text[19]],
    #     [forecast_hourly[20], float(hourlymsg[20]["temp"]), float(hourlymsg[20]["humidity"]),
    #      float(hourlymsg[20]["precip"]), hourlymsg[20]["windDir"], int(hourlymsg[20]["windSpeed"]),
    #      float(hourlymsg[20]["pop"]), forec_text[20]],
    #     [forecast_hourly[21], float(hourlymsg[21]["temp"]), float(hourlymsg[21]["humidity"]),
    #      float(hourlymsg[21]["precip"]), hourlymsg[21]["windDir"], int(hourlymsg[21]["windSpeed"]),
    #      float(hourlymsg[21]["pop"]), forec_text[21]],
    #     [forecast_hourly[22], float(hourlymsg[22]["temp"]), float(hourlymsg[22]["humidity"]),
    #      float(hourlymsg[22]["precip"]), hourlymsg[22]["windDir"], int(hourlymsg[22]["windSpeed"]),
    #      float(hourlymsg[22]["pop"]), forec_text[22]],
    #     [forecast_hourly[23], float(hourlymsg[23]["temp"]), float(hourlymsg[23]["humidity"]),
    #      float(hourlymsg[23]["precip"]), hourlymsg[23]["windDir"], int(hourlymsg[23]["windSpeed"]),
    #      float(hourlymsg[23]["pop"]), forec_text[23]]
    # ]
    return data


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
        timeout = aiohttp.ClientTimeout(total=20)
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
            allmsg = allmsg + i["title"] + ':' + i["text"] + '||'
            titlemsg = titlemsg + i["title"] + '||'

    if len(titlemsg) < 5:
        disaster_warn = '近日无' + disaster_level + '级及以上灾害'
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
        with async_timeout.timeout(15):
            response = await session.get(url)
    except Exception as e:
        raise e
    if response.status != 200:
        _LOGGER.error("Error while accessing: %s, status=%d",
                      url,
                      response.status)
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
