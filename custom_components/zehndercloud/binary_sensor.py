"""Support for Zehnder Cloud binary sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import ZehnderCloudEntity, ZehnderCloudUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class ZehnderCloudBinarySensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[dict, datetime | StateType]


@dataclass
class ZehnderCloudBinarySensorEntityDescription(
    BinarySensorEntityDescription, ZehnderCloudBinarySensorEntityDescriptionMixin
):
    """Describes Zehnder Cloud binary sensor entity."""


SENSORS: tuple[ZehnderCloudBinarySensorEntityDescription, ...] = (
    ZehnderCloudBinarySensorEntityDescription(
        key="awayEnabled",
        name="Away mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: bool(coordinator.state.value("awayEnabled")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="manualMode",
        name="Manual Mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: bool(coordinator.state.value("manualMode")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="boostTimerEnabled",
        name="Boost Timer Enabled",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: bool(coordinator.state.value("boostTimerEnabled")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="coolingSeason",
        name="coolingSeason",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda coordinator: bool(coordinator.state.value("coolingSeason")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="heatingSeason",
        name="heatingSeason",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda coordinator: bool(coordinator.state.value("heatingSeason")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="hoodIsOn",
        name="hoodIsOn",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda coordinator: bool(coordinator.state.value("hoodIsOn")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="hoodPresence",
        name="hoodPresence",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda coordinator: bool(coordinator.state.value("hoodPresence")),
    ),
    ZehnderCloudBinarySensorEntityDescription(
        key="postHeaterPresence",
        name="postHeaterPresence",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda coordinator: bool(
            coordinator.state.value("postHeaterPresence")
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zehnder Cloud binary sensor based on a config entry."""
    coordinators: list[ZehnderCloudUpdateCoordinator] = hass.data[DOMAIN][
        entry.entry_id
    ]

    entities = [
        ZehnderCloudBinarySensor(coordinator, description)
        for description in SENSORS
        for coordinator in coordinators
    ]

    async_add_entities(entities)


class ZehnderCloudBinarySensor(ZehnderCloudEntity, BinarySensorEntity):
    """Defines a Zehnder Cloud binary sensor entity."""

    entity_description: ZehnderCloudBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: ZehnderCloudUpdateCoordinator,
        description: ZehnderCloudBinarySensorEntityDescription,
    ) -> None:
        """Initialize a Zehnder Cloud binary sensor entity."""
        super().__init__(coordinator=coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator)
