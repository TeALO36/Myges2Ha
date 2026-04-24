"""Config flow for MyGES to Home Assistant."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_TARGET_CALENDAR
from .myges_api import MyGesAPI

_LOGGER = logging.getLogger(__name__)


def get_calendars(hass: HomeAssistant) -> list[str]:
    """Return a list of available calendar entities."""
    return hass.states.async_entity_ids("calendar")


class MyGesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyGES to Home Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            self._abort_if_unique_id_configured()

            # Validate the credentials
            session = async_get_clientsession(self.hass)
            api = MyGesAPI(
                session, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            success = await api.login()

            if success:
                return self.async_create_entry(
                    title=f"MyGES ({user_input[CONF_USERNAME]})",
                    data=user_input,
                )

            errors["base"] = "invalid_auth"

        # Dynamically list target calendars. Fallback to free text if none
        calendars = get_calendars(self.hass)
        if calendars:
            calendar_selector = vol.In(calendars)
        else:
            calendar_selector = str

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_TARGET_CALENDAR): calendar_selector,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
