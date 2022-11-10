"""Config flow for Zehnder Cloud."""
import logging
from typing import Any, Mapping

import pkce

from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, OAUTH2_CLIENT_ID
from .oauth_impl import ZehnderCloudOauth2Implementation

_LOGGER = logging.getLogger(__name__)


class ZehnderCloudControlFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Zehnder Cloud OAuth2 authentication."""

    DOMAIN = DOMAIN

    def __init__(self) -> None:
        """Initialize ZehnderCloudControlFlowHandler."""
        super().__init__()

        # Generate a code_verifier and code_challenge pair to use during OAuth2 flow
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        await self.async_set_unique_id(DOMAIN)

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        self.async_register_implementation(
            self.hass,
            ZehnderCloudOauth2Implementation(self.hass, self.code_verifier),
        )

        return await super().async_step_user(user_input)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> dict:
        """Create an oauth config entry or update existing entry for reauth."""
        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        return await super().async_oauth_create_entry(data)

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @property
    def extra_authorize_data(self) -> dict:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": OAUTH2_CLIENT_ID + " offline_access",
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
