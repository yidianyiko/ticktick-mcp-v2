"""
Authentication related MCP tools

Provides authentication functions such as login and logout
"""

import logging
from typing import Any, Dict, List
import mcp.types as types

from utils.helpers import load_credentials, save_credentials

logger = logging.getLogger(__name__)


class AuthTools:
    """Authentication tools class"""

    def get_tools(self) -> List[types.Tool]:
        """Get list of authentication related tools"""
        return [
            types.Tool(
                name="auth_login",
                description="Login to TickTick with username and password",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "TickTick username or email"},
                        "password": {"type": "string", "description": "TickTick password"},
                    },
                    "required": ["username", "password"],
                },
            ),
            types.Tool(
                name="auth_logout",
                description="Logout from TickTick and clear saved credentials",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="auth_status",
                description="Check authentication status",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any], server: Any) -> Dict[str, Any]:
        """Call authentication tool"""

        if name == "auth_login":
            return await self._login(arguments, server)
        elif name == "auth_logout":
            return await self._logout(server)
        elif name == "auth_status":
            return await self._status(server)
        else:
            raise Exception(f"Unknown auth tool: {name}")

    async def _login(self, arguments: Dict[str, Any], server: Any) -> Dict[str, Any]:
        """Login function"""
        try:
            username = arguments.get("username")
            password = arguments.get("password")

            if not username or not password:
                return {"success": False, "error": "Username and password are required"}

            # Use TickTickAuth for authentication
            from auth import TickTickAuth

            auth = TickTickAuth()

            if auth.authenticate(username, password):
                return {
                    "success": True,
                    "message": f"Successfully logged in as {username}",
                    "username": username,
                }
            else:
                return {"success": False, "error": "Authentication failed"}

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"success": False, "error": f"Login failed: {str(e)}"}

    async def _logout(self, server: Any) -> Dict[str, Any]:
        """Logout function"""
        try:
            # Use TickTickAuth for logout
            from auth import TickTickAuth

            auth = TickTickAuth()

            if auth.logout():
                return {
                    "success": True,
                    "message": "Successfully logged out and cleared credentials",
                }
            else:
                return {"success": False, "error": "Logout failed"}

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {"success": False, "error": f"Logout failed: {str(e)}"}

    async def _status(self, server: Any) -> Dict[str, Any]:
        """Check authentication status"""
        try:
            # Use TickTickAuth to check authentication status
            from auth import TickTickAuth

            auth = TickTickAuth()

            if auth.is_authenticated():
                username = auth.get_username() or "Unknown"
                return {
                    "authenticated": True,
                    "message": f"Authenticated as {username}",
                    "username": username,
                }
            else:
                return {"authenticated": False, "message": "Not authenticated"}

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {"authenticated": False, "error": f"Status check failed: {str(e)}"}
