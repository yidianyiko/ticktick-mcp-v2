"""
Authentication related MCP tools

Provides authentication functions such as login and logout
"""

import logging
from typing import Any

from mcp import types

from auth import TickTickAuth

logger = logging.getLogger(__name__)


class AuthTools:
    """Authentication tools class"""

    def get_tools(self) -> list[types.Tool]:
        """Get list of authentication related tools"""
        return [
            types.Tool(
                name="auth_login",
                description="Login to TickTick with username and password",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "TickTick username or email",
                        },
                        "password": {
                            "type": "string",
                            "description": "TickTick password",
                        },
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

    async def call_tool(
        self, name: str, arguments: dict[str, Any], server: Any,
    ) -> dict[str, Any]:
        """Call authentication tool"""

        if name == "auth_login":
            return await self._login(arguments, server)
        if name == "auth_logout":
            return await self._logout(server)
        if name == "auth_status":
            return await self._status(server)
        msg = f"Unknown auth tool: {name}"
        raise ValueError(msg)

    async def _login(self, arguments: dict[str, Any], _server: Any) -> dict[str, Any]:
        """Login function"""
        try:
            username = arguments.get("username")
            password = arguments.get("password")

            if not username or not password:
                return {"success": False, "error": "Username and password are required"}

            # Use TickTickAuth for authentication
            auth = TickTickAuth()

            success = auth.authenticate(username, password)
        except Exception as e:
            logger.exception("Login failed")
            return {"success": False, "error": f"Login failed: {e!s}"}
        else:
            if success:
                return {
                    "success": True,
                    "message": f"Successfully logged in as {username}",
                    "username": username,
                }
            return {"success": False, "error": "Authentication failed"}

    async def _logout(self, _server: Any) -> dict[str, Any]:
        """Logout function"""
        try:
            # Use TickTickAuth for logout
            auth = TickTickAuth()
            did_logout = auth.logout()
        except Exception as e:
            logger.exception("Logout failed")
            return {"success": False, "error": f"Logout failed: {e!s}"}
        else:
            if did_logout:
                return {
                    "success": True,
                    "message": "Successfully logged out and cleared credentials",
                }
            return {"success": False, "error": "Logout failed"}

    async def _status(self, _server: Any) -> dict[str, Any]:
        """Check authentication status"""
        try:
            # Use TickTickAuth to check authentication status
            auth = TickTickAuth()
            is_auth = auth.is_authenticated()
        except Exception as e:
            logger.exception("Status check failed")
            return {"authenticated": False, "error": f"Status check failed: {e!s}"}
        else:
            if is_auth:
                username = auth.get_username() or "Unknown"
                return {
                    "authenticated": True,
                    "message": f"Authenticated as {username}",
                    "username": username,
                }
            return {"authenticated": False, "message": "Not authenticated"}
