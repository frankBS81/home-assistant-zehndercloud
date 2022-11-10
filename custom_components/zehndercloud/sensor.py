"""Support for Zehner Cloud sensors."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
    TIME_DAYS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from . import ZehnderCloudEntity, ZehnderCloudUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class ZehnderCloudSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[dict, datetime | StateType]


@dataclass
class ZehnderCloudSensorEntityDescription(
    SensorEntityDescription, ZehnderCloudSensorEntityDescriptionMixin
):
    """Describes Zehnder Cloud sensor entity."""


SENSORS: tuple[ZehnderCloudSensorEntityDescription, ...] = (
    # Temperature and Humidity
    ZehnderCloudSensorEntityDescription(
        key="exhaustAirTemp",
        name="Exhaust air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda coordinator: int(coordinator.state.value("exhaustAirTemp")) / 10,
    ),
    ZehnderCloudSensorEntityDescription(
        key="exhaustAirHumidity",
        name="Exhaust air humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(coordinator.state.value("exhaustAirHumidity")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="extractAirTemp",
        name="Extract air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda coordinator: int(coordinator.state.value("extractAirTemp"))
                                     / 10,
    ),
    ZehnderCloudSensorEntityDescription(
        key="extractAirHumidity",
        name="Extract air humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(coordinator.state.value("extractAirHumidity")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemOutdoorTemp",
        name="Outdoor air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda coordinator: int(coordinator.state.value("systemOutdoorTemp"))
                                     / 10,
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemOutdoorHumidity",
        name="Outdoor air humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(
            coordinator.state.value("systemOutdoorHumidity")
        ),
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemSupplyTemp",
        name="Supply air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        value_fn=lambda coordinator: int(coordinator.state.value("systemSupplyTemp"))
                                     / 10,
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemSupplyHumidity",
        name="Supply air humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(
            coordinator.state.value("systemSupplyHumidity")
        ),
    ),
    # Fans
    ZehnderCloudSensorEntityDescription(
        key="exhaustSpeed",
        name="Exhaust fan speed",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="rpm",
        value_fn=lambda coordinator: int(coordinator.state.value("exhaustSpeed")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemSupplySpeed",
        name="Supply fan speed",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="rpm",
        value_fn=lambda coordinator: int(coordinator.state.value("systemSupplySpeed")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="exhaustDuty",
        name="Exhaust fan duty",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(coordinator.state.value("exhaustDuty")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="systemSupplyDuty",
        name="Supply fan duty",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: int(coordinator.state.value("systemSupplyDuty")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="exhaustFanAirFlow",
        name="Exhaust fan airflow",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        value_fn=lambda coordinator: int(coordinator.state.value("exhaustFanAirFlow")),
    ),
    ZehnderCloudSensorEntityDescription(
        key="supplyFanAirFlow",
        name="Supply fan airflow",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        value_fn=lambda coordinator: int(coordinator.state.value("supplyFanAirFlow")),
    ),
    # Power Consumption
    ZehnderCloudSensorEntityDescription(
        key="currentVentilationPower",
        name="Power usage",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=POWER_WATT,
        value_fn=lambda coordinator: int(
            coordinator.state.value("currentVentilationPower")
        ),
    ),
    # Analog Input
    ZehnderCloudSensorEntityDescription(
        key="analogInput1",
        name="Analog Input 1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("analogInput1"),
    ),
    ZehnderCloudSensorEntityDescription(
        key="analogInput2",
        name="Analog Input 2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("analogInput2"),
    ),
    ZehnderCloudSensorEntityDescription(
        key="analogInput3",
        name="Analog Input 3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("analogInput3"),
    ),
    ZehnderCloudSensorEntityDescription(
        key="analogInput4",
        name="Analog Input 4",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("analogInput4"),
    ),
    # Bypass
    ZehnderCloudSensorEntityDescription(
        # The actual duty of the bypass. Shows the percentage of bypassed air is shown.
        key="bypassDuty",
        name="Bypass State",
        # device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda coordinator: coordinator.state.value("bypassDuty"),
        icon="mdi:camera-iris",
    ),
    ZehnderCloudSensorEntityDescription(
        # The different modes of the bypass such as closed, open or auto. This is used to regulate whether outside air is fed into the building without heat recovery control.
        key="bypassMode",
        name="Bypass Mode",
        # device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        # native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("bypassMode"),
    ),
    # ventilationMode
    ZehnderCloudSensorEntityDescription(
        # View of the current ventilation mode. AUTO = the airflow is set by the scheduler. MANUAL = the airflow is set by the user.
        key="ventilationMode",
        name="Ventilation Mode",
        # device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        # native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("ventilationMode"),
    ),
    ZehnderCloudSensorEntityDescription(
        # The ventilation pre-set the unit is currently running at.
        key="ventilationPreset",
        name="Ventilation Preset",
        # device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        # native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        value_fn=lambda coordinator: coordinator.state.value("ventilationPreset"),
    ),
    # Other
    ZehnderCloudSensorEntityDescription(
        key="remainingFilterDuration",
        name="Days to replace filter",
        # device_class=None,
        # state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TIME_DAYS,
        value_fn=lambda coordinator: int(
            coordinator.state.value("remainingFilterDuration")
        ),
        icon="mdi:calendar",
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zehnder Cloud sensor based on a config entry."""
    coordinators: list[ZehnderCloudUpdateCoordinator] = hass.data[DOMAIN][
        entry.entry_id
    ]

    entities = [
        ZehnderCloudSensor(coordinator, description)
        for description in SENSORS
        for coordinator in coordinators
    ]

    async_add_entities(entities)


class ZehnderCloudSensor(ZehnderCloudEntity, SensorEntity):
    """Defines a Zehnder Cloud sensor entity."""

    entity_description: ZehnderCloudSensorEntityDescription

    def __init__(
            self,
            coordinator: ZehnderCloudUpdateCoordinator,
            description: ZehnderCloudSensorEntityDescription,
    ) -> None:
        """Initialize a Zehnder Cloud sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator)
