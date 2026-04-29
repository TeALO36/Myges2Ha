"""The MyGES to Home Assistant integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_TARGET_CALENDAR, CONF_EVENT_PREFIX
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
        hass, api, entry.data[CONF_TARGET_CALENDAR], entry.data.get(CONF_EVENT_PREFIX, "")
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


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    target_calendar = entry.data.get(CONF_TARGET_CALENDAR)
    if not target_calendar:
        return

    _LOGGER.info(
        "L'intégration MyGES a été désinstallée. Veuillez noter qu'en raison des limitations "
        "actuelles des API de Home Assistant, il n'est pas possible de supprimer automatiquement "
        "les événements du calendrier cible (%s) depuis cette intégration. "
        "Cependant, tous les événements créés par l'intégration contiennent la mention "
        "'--- Créé par MyGES ---' dans leur description. Vous pouvez rechercher cette mention "
        "dans votre agenda (ex: Google Agenda) pour les identifier et les supprimer manuellement.",
        target_calendar
    )
