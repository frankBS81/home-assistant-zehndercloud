"""Local implementation of OAuth2 specific to Ondilo to hard code client id and secret and return a proper name."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation

from .const import (
    DOMAIN,
    OAUTH2_AUTHORIZE,
    OAUTH2_CLIENT_ID,
    OAUTH2_SECRET,
    OAUTH2_TOKEN,
)

_LOGGER = logging.getLogger(__name__)


class ZehnderCloudOauth2Implementation(LocalOAuth2Implementation):
    """Local implementation of OAuth2 specific to Zehnder Cloud to hard code client id and secret and return a proper name."""

    def __init__(self, hass: HomeAssistant, auth_code_verifier: str = None) -> None:
        """Just init default class with default values."""
        super().__init__(
            hass,
            DOMAIN,
            OAUTH2_CLIENT_ID,
            OAUTH2_SECRET,
            OAUTH2_AUTHORIZE,
            OAUTH2_TOKEN,
        )
        self.auth_code_verifier = auth_code_verifier

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return "Zehnder Cloud"

    async def _token_request(self, data: dict) -> dict:
        """Make a token request, but include the code_verifier."""
        # data['scope'] = 'openid profile offline_access'
        # data["scope"] = OAUTH_CLIENT_ID + " offline_access",

        if self.auth_code_verifier:
            data["code_verifier"] = self.auth_code_verifier

        result = await super()._token_request(data)

        # result['expires_in'] = result.get('id_token_expires_in')
        return result
