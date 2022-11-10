"""Support for Zehner Cloud fan."""
from __future__ import annotations

import logging
import math
from typing import Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from . import ZehnderCloudEntity, ZehnderCloudUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (1, 3)  # away is not included in speeds and instead mapped to off


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zehnder Cloud fan based on a config entry."""
    coordinators: list[ZehnderCloudUpdateCoordinator] = hass.data[DOMAIN][
        entry.entry_id
    ]

    entities = [ZehnderCloudFan(coordinator) for coordinator in coordinators]

    async_add_entities(entities)


class ZehnderCloudFan(ZehnderCloudEntity, FanEntity):
    """Defines a Zehnder Cloud fan entity."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    current_speed = None

    def __init__(
        self,
        coordinator: ZehnderCloudUpdateCoordinator,
    ) -> None:
        """Initialize a Zehnder Cloud fan entity."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_fan"

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ranged_value_to_percentage(
            SPEED_RANGE, self.coordinator.state.value("ventilationPreset")
        )

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None:
        """Turn the entity on."""
        if percentage is None:
            await self.async_set_percentage(1)  # Set fan speed to low
        else:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        await self.async_set_percentage(0)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed percentage."""
        speed = math.ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))

        _LOGGER.debug("Changing fan speed percentage to %s -> %d", percentage, speed)

        await self.coordinator.client.set_device_settings(
            self.coordinator.device_id, {"setVentilationPreset": {"value": speed}}
        )
        await self.coordinator.async_request_refresh()
