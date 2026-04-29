"""Constants for the MyGES to Home Assistant integration."""

from datetime import timedelta

DOMAIN = "myges2ha"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TARGET_CALENDAR = "target_calendar"
CONF_EVENT_PREFIX = "event_prefix"

UPDATE_INTERVAL = timedelta(hours=1)
SYNC_DAYS = 30
