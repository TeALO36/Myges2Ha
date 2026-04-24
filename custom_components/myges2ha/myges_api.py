"""MyGES API Client."""

import logging
import base64
import urllib.parse
from datetime import datetime
import aiohttp

_LOGGER = logging.getLogger(__name__)


class MyGesAPI:
    """Class to communicate with MyGES API."""

    def __init__(
        self, session: aiohttp.ClientSession, username: str, password: str
    ):
        """Initialize the API and store the auth credentials."""
        self.session = session
        self.username = username
        self.password = password
        self.access_token = None
        self.token_type = None

    async def login(self) -> bool:
        """Authenticate and retrieve the access token."""
        credentials = f"{self.username}:{self.password}"
        base64_cred = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )

        headers = {"Authorization": f"Basic {base64_cred}"}

        # Kordis OAuth endpoint returns a 302 Redirect with token in the URL hash
        url = "https://authentication.kordis.fr/oauth/authorize"
        url += "?response_type=token&client_id=skolae-app"

        try:
            # allow_redirects=False is required to catch the 302 Redirect
            async with self.session.get(
                url, headers=headers, allow_redirects=False
            ) as response:
                if response.status in (301, 302, 303, 307, 308):
                    location = response.headers.get("Location")
                    if location and "#" in location:
                        hash_part = location.split("#", 1)[1]
                        params = urllib.parse.parse_qs(hash_part)

                        if "access_token" in params:
                            self.access_token = params["access_token"][0]
                            self.token_type = params.get(
                                "token_type", ["Bearer"]
                            )[0]
                            _LOGGER.debug(
                                "Successfully authenticated to MyGES."
                            )
                            return True

                _LOGGER.error(
                    "Failed to authenticate to MyGES: "
                    "Invalid response or credentials."
                )
                return False

        except Exception as e:
            _LOGGER.error(f"Error authenticating to MyGES: {e}")
            return False

    async def get_agenda(
        self, start_date: datetime, end_date: datetime
    ) -> list:
        """Retrieve the agenda between start_date and end_date."""
        if not self.access_token:
            success = await self.login()
            if not success:
                raise Exception("Authentication failed")

        headers = {
            "Authorization": f"{self.token_type} {self.access_token}",
            "Accept": "application/json",
        }

        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)

        url = f"https://api.kordis.fr/me/agenda?start={start_ts}&end={end_ts}"

        try:
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", [])
        except Exception as e:
            _LOGGER.error(f"Failed to fetch MyGES agenda: {e}")
            raise
