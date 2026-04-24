"""The MyGES to Home Assistant integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_TARGET_CALENDAR
from .myges_api import MyGesAPI
from .coordinator import MyGesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["calendar"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyGES from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = MyGesAPI(
        session, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )

    # Verify auth
    success = await api.login()
    if not success:
        _LOGGER.error("Failed to authenticate with MyGES during setup.")
        return False

    coordinator = MyGesDataUpdateCoordinator(
        hass, api, entry.data[CONF_TARGET_CALENDAR]
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
