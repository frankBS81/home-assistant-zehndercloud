"""The Zehnder Cloud integration."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
from pyzehndercloud import AuthError, DeviceDetails, DeviceState, ZehnderCloud

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import api, config_flow
from .const import DOMAIN
from .oauth_impl import ZehnderCloudOauth2Implementation

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.FAN]
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zehnder Cloud from a config entry."""
    config_flow.ZehnderCloudControlFlowHandler.async_register_implementation(
        hass,
        ZehnderCloudOauth2Implementation(hass),
    )

    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    web_session = aiohttp_client.async_get_clientsession(hass)
    oauth_session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    auth = api.AsyncConfigEntryAuth(web_session, oauth_session)

    try:
        client = ZehnderCloud(web_session, auth)
        devices = await client.get_devices()
    except AuthError as ex:
        raise ConfigEntryAuthFailed(f"Credentials expired for Zehnder Cloud") from ex

    # Create a coordinator for every device we poll.
    coordinators = []
    for device_id in devices:
        coordinator = ZehnderCloudUpdateCoordinator(
            hass=hass, client=client, device_id=device_id
        )
        await coordinator.async_config_entry_first_refresh()
        coordinators.append(coordinator)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ZehnderCloudUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Zehnder Cloud Device data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ZehnderCloud,
        device_id: int,
    ) -> None:
        """Initialize."""
        self._client = client
        self._device_id = device_id

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            async with async_timeout.timeout(10):
                state = await self._client.get_device_state(self._device_id)
                _LOGGER.debug("State for device %s: %s", self._device_id, state)

            async with async_timeout.timeout(10):
                details = await self._client.get_device_details(self._device_id)
                _LOGGER.debug("Details for device %s: %s", self._device_id, details)

        except AuthError as ex:
            raise ConfigEntryAuthFailed(
                f"Credentials expired for Zehnder Cloud"
            ) from ex

        except Exception as ex:
            raise UpdateFailed(f"Error communicating with API: {ex}") from ex

        if state.data.get("timestamp") is None:
            raise UpdateFailed("Update from Zehnder Cloud did not contain data")

        return {"state": state, "details": details}

    @property
    def client(self) -> ZehnderCloud:
        """Return the client."""
        return self._client

    @property
    def device_id(self) -> int:
        """Return the device id."""
        return self._device_id

    @property
    def state(self) -> DeviceState:
        """Return the state of the device."""
        return self.data.get("state")

    @property
    def details(self) -> DeviceDetails:
        """Return the details of the device."""
        return self.data.get("details")


class ZehnderCloudEntity(CoordinatorEntity[ZehnderCloudUpdateCoordinator]):
    """Base class for a Zehnder Cloud entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.details.value("serialNumber"))},
            name=self.coordinator.details.value("deviceType").get("name"),
            manufacturer="Zehnder",
            model=self.coordinator.details.value("deviceType").get("name"),
            sw_version=self.coordinator.details.property("swVersion"),
            hw_version=self.coordinator.details.property("hwVersion"),
            configuration_url=f"https://my.zehnder-systems.com/customer/devices/{self.coordinator.device_id}",
        )

# TODO: create sensors for this
example = {
    # "analogInput1": 0,
    # "analogInput2": 0,
    # "analogInput3": 0,
    # "analogInput4": 0,
    "avoidedCooling": 28,
    "avoidedHeating": 0,
    # "awayEnabled": False,
    # "boostTimerEnabled": False,
    # "bypassDuty": 0,
    # "bypassMode": 2,
    "comfoCoolCompressorState": 1,
    "comfortTemperatureMode": 0,
    "coolProfileTemp": 190,
    # "coolingSeason": True,
    # "currentVentilationPower": 9,
    # "exhaustAirHumidity": 57,
    # "exhaustAirTemp": 264,
    "exhaustAirTempAfterComfoCool": 0,
    # "exhaustDuty": 21,
    # "exhaustFanAirFlow": 73,
    "exhaustFanOff": 0,
    # "exhaustSpeed": 889,
    # "extractAirHumidity": 53,
    # "extractAirTemp": 259,
    "frostDuty": 0,
    # "heatingSeason": False,
    # "hoodIsOn": False,
    # "hoodPresence": False,
    "limitRMOTCooling": 200,
    "limitRMOTHeating": 130,
    # "manualMode": False,
    "normalProfileTemp": 210,
    "passiveTemperatureMode": 0,
    # "postHeaterPresence": False,
    "postSupplyAirTempAfterComfoCool": 0,
    # "remainingFilterDuration": 140,
    "requiredTemperature": 224,
    "runningMeanOutdoorTemparature": 216,
    # "supplyFanAirFlow": 72,
    "supplyFanOff": 0,
    # "systemOutdoorHumidity": 48,
    # "systemOutdoorTemp": 264,
    # "systemSupplyDuty": 23,
    # "systemSupplyHumidity": 48,
    # "systemSupplySpeed": 907,
    # "systemSupplyTemp": 260,
    "temperatureProfile": 0,
    # "ventilationMode": 0,
    # "ventilationPreset": 0,
    "warmProfileTemp": 230,
}


example2 = {
  'properties': [
    {
      'name': 'assistantName',
      'value': 'ComfoAirQ'
    },
    {
      'name': 'deviceSerial',
      'value': 'BEA004185031910'
    },
    {
      'name': 'swVersion',
      'value': 'R1.4.0'
    },
    {
      'name': 'articleNr',
      'value': '471502004'
    },
    {
      'name': 'productSerial',
      'value': 'SENR20600361'
    },
    # {
    #   'name': 'remainingFilterDuration',
    #   'value': '129'
    # },
    {
      'name': 'variant',
      'value': '2'
    },
    {
      'name': 'hwVersion',
      'value': '2'
    },
    {
      'name': 'productId',
      'value': '0'
    },
    {
      'name': 'hasComfoSense',
      'value': 'False'
    },
    {
      'name': 'hasComfoSwitch',
      'value': 'False'
    },
    {
      'name': 'hasOptionBox',
      'value': 'False'
    },
    {
      'name': 'hasComfoConnect',
      'value': 'True'
    },
    {
      'name': 'hasComfoCool',
      'value': 'False'
    },
    {
      'name': 'hasKNXGateway',
      'value': 'False'
    },
    {
      'name': 'hasServiceTool',
      'value': 'False'
    },
    {
      'name': 'hasProductionTestTool',
      'value': 'False'
    },
    {
      'name': 'hasDesignVerificationTestTool',
      'value': 'False'
    },
    {
      'name': 'temperatureProfile',
      'value': '0'
    },
    {
      'name': 'ventilationPreset',
      'value': '1'
    },
    {
      'name': 'manualMode',
      'value': 'True'
    },
    {
      'name': 'exhaustFanOff',
      'value': '0'
    },
    {
      'name': 'supplyFanOff',
      'value': '0'
    },
    {
      'name': 'bypassMode',
      'value': '2'
    },
    {
      'name': 'warmProfileTemp',
      'value': '230'
    },
    {
      'name': 'normalProfileTemp',
      'value': '210'
    },
    {
      'name': 'coolProfileTemp',
      'value': '190'
    },
    {
      'name': 'comfortTemperatureMode',
      'value': '0'
    },
    {
      'name': 'boostTimerEnabled',
      'value': 'False'
    },
    {
      'name': 'awayEnabled',
      'value': 'False'
    },
    {
      'name': 'passiveTemperatureMode',
      'value': '0'
    },
    {
      'name': 'limitRMOTCooling',
      'value': '200'
    },
    {
      'name': 'limitRMOTHeating',
      'value': '130'
    }
  ],
}