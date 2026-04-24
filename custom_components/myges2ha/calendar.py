"""Calendar platform for MyGES."""

from datetime import datetime
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_USERNAME
from .coordinator import MyGesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyGES calendar based on a config entry."""
    coordinator: MyGesDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([MyGesCalendarEntity(coordinator, entry)])


class MyGesCalendarEntity(
    CoordinatorEntity[MyGesDataUpdateCoordinator], CalendarEntity
):
    """Representation of a MyGES Calendar."""

    def __init__(
        self, coordinator: MyGesDataUpdateCoordinator, entry: ConfigEntry
    ):
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self._attr_name = f"MyGES {entry.data[CONF_USERNAME]}"
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self.coordinator.data:
            return None

        now = dt_util.now()
        upcoming_events = []

        for evt in self.coordinator.data:
            start_ts = evt.get("start_date")
            end_ts = evt.get("end_date")
            if not start_ts or not end_ts:
                continue

            # Convert from ms to dt
            start_dt = datetime.fromtimestamp(
                start_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
            )
            end_dt = datetime.fromtimestamp(
                end_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
            )

            if end_dt > now:
                upcoming_events.append(
                    {"start": start_dt, "end": end_dt, "event": evt}
                )

        if not upcoming_events:
            return None

        # Sort by start date
        upcoming_events.sort(key=lambda x: x["start"])
        next_evt = upcoming_events[0]
        evt_data = next_evt["event"]

        summary = evt_data.get("name", "Cours")
        rooms = [room.get("name") for room in evt_data.get("rooms", [])]
        location = ", ".join(rooms) if rooms else ""
        desc = (
            f"Professeur: {evt_data.get('teacher', '')}\n"
            f"Modalité: {evt_data.get('modality', '')}"
        )

        return CalendarEvent(
            summary=summary,
            start=next_evt["start"],
            end=next_evt["end"],
            location=location,
            description=desc,
        )

    # To support older HomeAssistant core
    async def async_get_events(self, *args, **kwargs) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if len(args) == 3:
            return await self._async_get_events(args[1], args[2])
        elif len(args) == 2:
            return await self._async_get_events(args[0], args[1])
        elif "start_date" in kwargs and "end_date" in kwargs:
            return await self._async_get_events(
                kwargs["start_date"], kwargs["end_date"]
            )
        else:
            return []

    async def _async_get_events(
        self, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Internal method to return calendar events."""
        events = []
        if not self.coordinator.data:
            return events

        for evt in self.coordinator.data:
            start_ts = evt.get("start_date")
            end_ts = evt.get("end_date")
            if not start_ts or not end_ts:
                continue

            # Convert from ms to dt
            evt_start = datetime.fromtimestamp(
                start_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
            )
            evt_end = datetime.fromtimestamp(
                end_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
            )

            # Check if event overlaps with the requested range
            if evt_start < end_date and evt_end > start_date:
                summary = evt.get("name", "Cours")
                rooms = [room.get("name") for room in evt.get("rooms", [])]
                location = ", ".join(rooms) if rooms else ""
                desc = (
                    f"Professeur: {evt.get('teacher', '')}\n"
                    f"Modalité: {evt.get('modality', '')}"
                )

                events.append(
                    CalendarEvent(
                        summary=summary,
                        start=evt_start,
                        end=evt_end,
                        location=location,
                        description=desc,
                    )
                )

        return events
