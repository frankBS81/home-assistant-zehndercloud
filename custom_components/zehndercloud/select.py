"""Support for Zehnder Cloud selects."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Awaitable

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import ZehnderCloudEntity, ZehnderCloudUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class ZehnderCloudSelectEntityDescriptionMixin:
    """Mixin for required keys."""

    options: list[str]  # TODO: remove for 2022.11
    command: Callable[str, dict]


@dataclass
class ZehnderCloudSelectEntityDescription(
    SelectEntityDescription, ZehnderCloudSelectEntityDescriptionMixin
):
    """Describes Zehnder Cloud select entity."""


DESCRIPTORS: tuple[ZehnderCloudSelectEntityDescription, ...] = (
    ZehnderCloudSelectEntityDescription(
        key="bypassMode",
        name="Bypass mode",
        entity_category=EntityCategory.CONFIG,
        options=["auto", "on", "off"],
        command=lambda option: {"forceBypass": {"seconds": 60}},
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zehnder Cloud select based on a config entry."""
    coordinators: list[ZehnderCloudUpdateCoordinator] = hass.data[DOMAIN][
        entry.entry_id
    ]

    entities = [
        ZehnderCloudSelect(coordinator, description)
        for description in DESCRIPTORS
        for coordinator in coordinators
    ]

    async_add_entities(entities)


class ZehnderCloudSelect(ZehnderCloudEntity, SelectEntity):
    """Defines a Zehnder Cloud select entity."""

    entity_description: ZehnderCloudSelectEntityDescription

    def __init__(
            self,
            coordinator: ZehnderCloudUpdateCoordinator,
            description: ZehnderCloudSelectEntityDescription,
    ) -> None:
        """Initialize a Zehnder Cloud select entity."""
        super().__init__(coordinator=coordinator)

        self.entity_description = description
        self._attr_options = description.options
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def current_option(self) -> str:
        """Return current lamp mode."""
        return "auto"
        #     return self.entity_description.value_fn(self.coordinator)
        # return self.coordinator.data.settings.lamp_mode.name.lower()

    async def async_select_option(self, option: str) -> None:
        """Select lamp mode."""
        await self.coordinator.client.set_device_settings(
            self.coordinator.device_id, {"forceBypass": {"seconds": 60}}
        )
        await self.coordinator.async_request_refresh()
