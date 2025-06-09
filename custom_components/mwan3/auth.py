"""Authentication module for MWAN3 integration."""
from __future__ import annotations

import logging
import re
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

_LOGGER = logging.getLogger(__name__)

class MWAN3Auth:
    """MWAN3 Authentication handler."""

    def __init__(self, host: str, username: str, password: str):
        """Initialize the auth handler."""
        self.host = host
        self.username = username
        self.password = password
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _get_token(self) -> str:
        """Get authentication token, reusing existing token if valid."""
        # Check if we have a valid token
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token

        session = await self._get_session()
        
        # Try to login and get the token
        login_url = f"http://{self.host}/cgi-bin/luci"
        login_data = {
            "luci_username": self.username,
            "luci_password": self.password,
        }

        try:
            async with session.post(login_url, data=login_data, allow_redirects=False) as response:
                if response.status != 302:
                    raise ValueError("Invalid credentials or connection failed")

                # Extract token from the Set-Cookie header
                cookies = response.headers.getall('Set-Cookie', [])
                for cookie in cookies:
                    if 'sysauth=' in cookie:
                        match = re.search(r'sysauth=([^;]+)', cookie)
                        if match:
                            self._token = match.group(1)
                            # Set token expiry to 1 hour from now
                            self._token_expiry = datetime.now() + timedelta(hours=1)
                            return self._token

                raise ValueError("Failed to get authentication token")

        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to MWAN3: %s", err)
            raise ValueError("Failed to connect to MWAN3") from err

    async def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        token = await self._get_token()
        return {"Cookie": f"sysauth={token}"}

    async def validate_connection(self) -> Tuple[bool, str]:
        """Validate the connection and return (success, message)."""
        try:
            session = await self._get_session()
            headers = await self.get_headers()
            
            # Verify we can access the MWAN3 status page
            status_url = f"http://{self.host}/cgi-bin/luci/admin/status/mwan"
            
            async with session.get(status_url, headers=headers) as response:
                if response.status == 200:
                    return True, "Connection successful"
                elif response.status in (401, 403):
                    # Clear token on auth failure
                    self._token = None
                    self._token_expiry = None
                    return False, "Authentication failed"
                else:
                    return False, f"Failed to access MWAN3 status page (HTTP {response.status})"

        except Exception as err:
            _LOGGER.error("Error validating connection: %s", err)
            return False, f"Connection error: {str(err)}"

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None 