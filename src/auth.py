#!/usr/bin/env python3
"""
TickTick Authentication Module
Username/password authentication based on ticktick.py library
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)


class TickTickAuth:
    """Authentication manager based on ticktick.py library"""

    def __init__(self):
        """Initialize authentication manager"""
        self.env_file = Path(".env")
        self.config_dir = Path.home() / ".ticktick-mcp"
        self.credentials_file = self.config_dir / "credentials.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate using username and password"""
        try:
            # Import ticktick.py library
            import sys
            import os

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "submodule", "ticktick-py"))

            from ticktick.api import TickTickClient

            # Try to login
            client = TickTickClient(username, password)

            # Test connection
            client.sync()

            # Save credentials
            self._save_credentials(username, password)

            logger.info(f"Successfully authenticated as {username}")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _save_credentials(self, username: str, password: str) -> None:
        """Save credentials to local file"""
        credentials = {"username": username, "password": password, "authenticated": True}

        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)

        # Also save to .env file for compatibility
        set_key(self.env_file, "TICKTICK_USERNAME", username)
        set_key(self.env_file, "TICKTICK_PASSWORD", password)
        set_key(self.env_file, "TICKTICK_AUTHENTICATED", "true")

    def get_client(self):
        """Get authenticated TickTick client"""
        try:
            # Check if there are saved credentials
            if not self.is_authenticated():
                raise Exception("Not authenticated. Please login first.")

            # Import ticktick.py library
            import sys
            import os

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "submodule", "ticktick-py"))

            from ticktick.api import TickTickClient

            # Get saved credentials
            credentials = self._load_credentials()
            if not credentials:
                raise Exception("No saved credentials found.")

            # Create client
            client = TickTickClient(credentials["username"], credentials["password"])

            # Sync data
            client.sync()

            return client

        except Exception as e:
            logger.error(f"Failed to get client: {e}")
            raise

    def _load_credentials(self) -> Optional[Dict[str, str]]:
        """Load saved credentials"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")

        return None

    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        try:
            credentials = self._load_credentials()
            return credentials is not None and credentials.get("authenticated", False)
        except Exception:
            return False

    def logout(self) -> bool:
        """Logout and clear credentials"""
        try:
            # Delete credentials file
            if self.credentials_file.exists():
                self.credentials_file.unlink()

            # Clear authentication info in .env file
            set_key(self.env_file, "TICKTICK_USERNAME", "")
            set_key(self.env_file, "TICKTICK_PASSWORD", "")
            set_key(self.env_file, "TICKTICK_AUTHENTICATED", "false")

            logger.info("Successfully logged out")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False

    def get_username(self) -> Optional[str]:
        """Get current username"""
        try:
            credentials = self._load_credentials()
            return credentials.get("username") if credentials else None
        except Exception:
            return None
