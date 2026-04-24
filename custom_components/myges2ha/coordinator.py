"""Data update coordinator for MyGES to Home Assistant."""

import logging
from datetime import datetime, timedelta
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.util import dt as dt_util

from .const import DOMAIN, UPDATE_INTERVAL, SYNC_DAYS
from .myges_api import MyGesAPI

_LOGGER = logging.getLogger(__name__)


class MyGesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MyGES data and syncing to Google Calendar."""

    def __init__(
        self, hass: HomeAssistant, api: MyGesAPI, target_calendar: str
    ):
        """Initialize the coordinator."""
        self.api = api
        self.target_calendar = target_calendar
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from MyGES and sync to target calendar."""
        try:
            # 1. Fetch MyGES events
            start_date = datetime.now()
            end_date = start_date + timedelta(days=SYNC_DAYS)

            myges_events = await self.api.get_agenda(start_date, end_date)
            _LOGGER.debug(f"Fetched {len(myges_events)} events from MyGES")

            # Store the events for the local calendar entity
            self.data = myges_events

            # 2. Sync to target calendar in the background
            self.hass.async_create_task(
                self._sync_to_target_calendar(
                    myges_events, start_date, end_date
                )
            )

            return myges_events
        except Exception as err:
            raise UpdateFailed(f"Error fetching MyGES data: {err}")

    async def _sync_to_target_calendar(
        self, myges_events, start_date, end_date
    ):
        """Sync MyGES events to the target Google Calendar."""
        try:
            # Get existing events from target calendar
            # We call the `get_events` service which returns a dictionary of events
            response = await self.hass.services.async_call(
                CALENDAR_DOMAIN,
                "get_events",
                {
                    "entity_id": self.target_calendar,
                    "start_date_time": start_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "end_date_time": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                },
                blocking=True,
                return_response=True,
            )

            existing_events = []
            if response and self.target_calendar in response:
                existing_events = response[self.target_calendar].get(
                    "events", []
                )

            new_events_count = 0

            # Map MyGES event to HA event fields
            for ges_evt in myges_events:
                summary = ges_evt.get("name", "Cours MyGES")

                # Convert timestamps from milliseconds
                start_ts = ges_evt.get("start_date")
                end_ts = ges_evt.get("end_date")

                if not start_ts or not end_ts:
                    continue

                start_dt = datetime.fromtimestamp(
                    start_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
                )
                end_dt = datetime.fromtimestamp(
                    end_ts / 1000.0, dt_util.DEFAULT_TIME_ZONE
                )

                # Prepare description and location
                rooms = [room.get("name") for room in ges_evt.get("rooms", [])]
                location = ", ".join(rooms) if rooms else ""

                teacher = ges_evt.get("teacher", "")
                modality = ges_evt.get("modality", "")
                description = f"Professeur: {teacher}\nModalité: {modality}"

                # A safer approach is to check if any existing event starts at
                # exactly the same time with same title
                already_exists = False
                for ex_evt in existing_events:
                    ex_start = ex_evt.get("start", "")
                    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
                    if ex_start and start_str in ex_start:
                        if ex_evt.get("summary", "") == summary:
                            already_exists = True
                            break

                if not already_exists:
                    # Create the event
                    service_data = {
                        "entity_id": self.target_calendar,
                        "summary": summary,
                        "description": description,
                        "start_date_time": start_dt.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "end_date_time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    if location:
                        service_data["location"] = location

                    await self.hass.services.async_call(
                        CALENDAR_DOMAIN,
                        "create_event",
                        service_data,
                        blocking=True,
                    )
                    new_events_count += 1

                    # Be nice to the API
                    await asyncio.sleep(0.5)

            _LOGGER.info(
                f"Synced {new_events_count} new MyGES events to {self.target_calendar}"
            )

        except Exception as err:
            _LOGGER.error(f"Error syncing to target calendar: {err}")
