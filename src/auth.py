#!/usr/bin/env python3
"""
TickTick Authentication Module
Username/password authentication based on ticktick.py library
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

import keyring
from keyring.backends.chainer import ChainerBackend

# Add ticktick.py submodule to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "submodule" / "ticktick-py"))

try:
    from ticktick.api import TickTickClient
except ImportError:
    TickTickClient = None

logger = logging.getLogger(__name__)


class TickTickAuth:
    """Authentication manager based on ticktick.py library"""

    @staticmethod
    def _keyring() -> Any:
        """Use only OS credential stores; reject plaintext and third-party fallbacks."""
        backend = keyring.get_keyring()
        backends = backend.backends if isinstance(backend, ChainerBackend) else [backend]
        for candidate in backends:
            if type(candidate).__module__ in {
                "keyring.backends.SecretService",
                "keyring.backends.kwallet",
                "keyring.backends.macOS",
                "keyring.backends.Windows",
            }:
                return candidate
        msg = "No secure OS keyring available. Configure a system credential store first."
        raise RuntimeError(msg)

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate using username and password"""
        if TickTickClient is None:
            msg = "ticktick.py library not available"
            raise ImportError(msg)

        try:
            # Try to login
            client = TickTickClient(username, password)

            # Test connection
            client.sync()

            # Save credentials
            self._save_credentials(username, password)
        except Exception:  # noqa: BLE001 - SDK and vault errors must fail closed
            logger.error(  # noqa: TRY400 - exceptions may contain credentials
                "Authentication failed; check login details and system keyring availability",
            )
            return False
        else:
            logger.info("Successfully authenticated as %s", username)
            return True

    def _save_credentials(self, username: str, password: str) -> None:
        """Save credentials exclusively in the system keyring"""
        self._keyring().set_password(
            "ticktick-mcp-v2", "credentials",
            json.dumps({"username": username, "password": password, "authenticated": True}),
        )

    def get_client(self) -> Any:
        """Get authenticated TickTick client"""
        # Validate prerequisites outside of try to avoid catching intentional errors
        if not self.is_authenticated():
            msg = "Not authenticated. Please login first."
            raise PermissionError(msg)

        if TickTickClient is None:
            msg = "ticktick.py library not available"
            raise ImportError(msg)

        # Get saved credentials
        credentials = self._load_credentials()
        if not credentials:
            msg = "No saved credentials found."
            raise FileNotFoundError(msg)

        try:
            # Create client
            client = TickTickClient(credentials["username"], credentials["password"])

            # Sync data
            client.sync()
        except Exception:
            logger.exception("Failed to get client")
            raise
        else:
            return client

    def _load_credentials(self) -> dict[str, str] | None:
        """Load credentials exclusively from the system keyring"""
        try:
            value = self._keyring().get_password("ticktick-mcp-v2", "credentials")
            if value:
                credentials = json.loads(value)
                if (
                    isinstance(credentials, dict)
                    and isinstance(credentials.get("username"), str)
                    and isinstance(credentials.get("password"), str)
                    and credentials["username"] and credentials["password"]
                ):
                    return credentials
        except Exception:  # noqa: BLE001 - unavailable vault means unauthenticated
            logger.error(  # noqa: TRY400 - do not log secret-bearing exceptions
                "Unable to read credentials from the system keyring",
            )
        return None

    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        try:
            credentials = self._load_credentials()
            return credentials is not None and credentials.get("authenticated", False)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    def logout(self) -> bool:
        """Logout and clear credentials"""
        try:
            vault = self._keyring()
            if vault.get_password("ticktick-mcp-v2", "credentials") is not None:
                vault.delete_password("ticktick-mcp-v2", "credentials")
        except Exception:
            logger.exception("Logout failed")
            return False
        else:
            logger.info("Successfully logged out")
            return True

    def get_username(self) -> str | None:
        """Get current username"""
        try:
            credentials = self._load_credentials()
            return credentials.get("username") if credentials else None
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None
