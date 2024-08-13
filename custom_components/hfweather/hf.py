"""
coordinator 组件
"""
import datetime
import logging
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.unit_system import METRIC_SYSTEM
from .const import (
    DOMAIN,
    CONDITION_CLASSES,
    DISASTER_LEVEL,
    DataSourceUrl
)


_LOGGER = logging.getLogger(__name__)


class HfCoordinator(DataUpdateCoordinator):
    """Class to manage fetching hf weather data API."""

    def __init__(
        self,
        hass,
        websession,
        api_key,
        api_version,
        location_key,
        longitude,
        latitude,
        dailysteps: int,
        hourlysteps: int,
        disaster_msg,
        disaster_level,
        alert: bool,
        starttime: int,
        interval: int,
    ):
        """Initialize."""
        self.hass = hass
        self.api_key = api_key
        self.api_version = api_version
        self.location_key = location_key
        self.longitude = longitude
        self.latitude = latitude
        self.dailysteps = dailysteps
        self.hourlysteps = hourlysteps
        self.disaster_msg = disaster_msg
        self.disaster_level = disaster_level
        self.alert = alert
        self.interval = interval
        self.starttime = starttime
        self.is_metric = "metric:v2"
        if hass.config.units is METRIC_SYSTEM:
            self.is_metric = "metric:v2"
        else:
            self.is_metric = "imperial"

        update_interval = datetime.timedelta(minutes=self.interval)
        _LOGGER.info("hew- update data every %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data_source = DataSourceUrl(api_version=self.api_version, longitude=self.longitude,
                                        latitude=self.latitude, api_key=self.api_key,
                                        dailysteps=self.dailysteps, hourlysteps=self.hourlysteps)

            wsdata = await weather_sensor_data_update(data_source, self.disaster_msg,
                                                      self.disaster_level)
            sgdata = await suggestion_data_update(self.hass, data_source, self.alert)
            wdata = await weather_data_update(data_source)
        except ClientConnectorError as error:
            _LOGGER.info("hew- HfCoordinator update: %s", error)
            raise UpdateFailed(error)
        return {
            "wsdata": wsdata,
            "sgdata": sgdata,
            "wdata": wdata,
            "location_key": self.location_key,
            "is_metric": self.is_metric,
        }


async def weather_sensor_data_update(data_source, disaster_msg, disaster_level):
    """xxx"""
    # if not alert:
    #     return {"alert": False}
    data = {}

    weather_now_url = data_source.weather_now_url
    air_now_url = data_source.air_now_url
    disaster_warn_url = data_source.disaster_warn_url
    # params = {"location": f"{longitude}/{latitude}", "key": key, }
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
        _LOGGER.info("hew- weather sensor update: %s", e)
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


async def suggestion_data_update(hass, data_source, alert):
    """xxx"""
    if not alert:
        return {"alert": False}

    url = data_source.suggestion_url
    # updatetime = ["1", "1"]
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
        with timeout(10):
            response = await session.get(url)
    except Exception as e:
        raise e
    if response.status != 200:
        _LOGGER.info("hew- Error while accessing: %s, status=%d", url, response.status)
        return

    result = await response.json()

    if result is None:
        _LOGGER.error("Request api Error")
        return
    elif result["code"] != "200":
        _LOGGER.info("hew- Error API return, code=%s,url=%s",
                      result["code"], url)
        return

    # 根据http返回的结果，更新数据
    all_result = result["daily"]
    # updatetime = result["updateTime"]
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

async def weather_data_update(data_source):
    """xxx"""
    forecast_url = data_source.forecast_url
    weather_now_url = data_source.weather_now_url
    forecast_hourly_url = data_source.forecast_hourly_url

    # params = {"location": f"{longitude}/{latitude}", "key": key}
    data = {}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
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
        _LOGGER.info("hew- weather data update: %s", e)
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
    for n in range(data_source.dailysteps):
        for i, j in CONDITION_CLASSES.items():
            if datemsg[n]["textDay"] in j:
                # forec_cond.append(i)
                # forec_text.append(datemsg[n]["textDay"])

                daily_tmp.append(
                    [i, int(datemsg[n]["tempMax"]), int(datemsg[n]["tempMin"]),
                      datemsg[n]["textDay"]
                      ]
                )
    data["forecast"] = daily_tmp

    hourlymsg = forecast_hourly["hourly"]
    # forecast_hourly = []
    # forec_text = []
    hourly_tmp = []
    for n in range(data_source.hourlysteps):
        for i, j in CONDITION_CLASSES.items():
            if hourlymsg[n]["text"] in j:
                # forecast_hourly.append(i)
                # forec_text.append(hourlymsg[n]["text"])

                hourly_tmp.append(
                    [i, float(hourlymsg[n]["temp"]), float(hourlymsg[n]["humidity"]),
                     float(hourlymsg[n]["precip"]), hourlymsg[n]["windDir"],
                     int(hourlymsg[n]["windSpeed"]), float(hourlymsg[n]["pop"]),
                     hourlymsg[n]["text"]
                     ]
                )
    data["forecast_hourly"] = hourly_tmp
    return data
