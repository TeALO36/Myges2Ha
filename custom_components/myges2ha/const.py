"""Constants for the MyGES to Home Assistant integration."""

from datetime import timedelta

DOMAIN = "myges2ha"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TARGET_CALENDAR = "target_calendar"

UPDATE_INTERVAL = timedelta(hours=1)
SYNC_DAYS = 30
