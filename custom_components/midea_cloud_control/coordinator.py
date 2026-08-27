"""Polling coordinator for Midea cloud-controlled appliances."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from msmart.device.AC.command import StateResponse

from .client import CloudError, MideaCloudClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MideaCloudCoordinator(DataUpdateCoordinator[StateResponse]):
    """Poll appliance state through the vendor cloud."""

    def __init__(self, hass: HomeAssistant, client: MideaCloudClient,
                 appliance_id: int, name: str) -> None:
        super().__init__(
            hass, _LOGGER, name=f"{DOMAIN} {name}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        self.appliance_id = appliance_id
        self.appliance_name = name

    async def _async_update_data(self) -> StateResponse:
        try:
            return await self.client.query(self.appliance_id)
        except CloudError as err:
            raise UpdateFailed(f"Cloud query failed: {err}") from err

    async def async_set_state(self, **changes: object) -> None:
        """Push a state change, then refresh so the UI reflects the device."""
        try:
            await self.client.set_state(self.appliance_id, **changes)
        except CloudError as err:
            raise UpdateFailed(f"Cloud command failed: {err}") from err
        await self.async_request_refresh()
