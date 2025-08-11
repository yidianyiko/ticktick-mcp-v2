#!/usr/bin/env python3
"""
TickTick MCP CLI - Command Line Interface
"""

import asyncio
import logging
import sys

import click
from dotenv import load_dotenv

from auth import TickTickAuth
from server import main as server_main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@click.group()
def cli() -> None:
    """TickTick MCP Server CLI"""


@cli.command()
@click.option(
    "--username",
    prompt="TickTick Username/Email",
    help="Your TickTick username or email",
)
@click.option(
    "--password",
    prompt="TickTick Password",
    hide_input=True,
    help="Your TickTick password",
)
def auth(username: str, password: str) -> None:
    """Authenticate with TickTick using username and password"""
    try:
        auth_handler = TickTickAuth()

        # Try to authenticate
        if auth_handler.authenticate(username, password):
            click.echo("✅ Authentication successful! Credentials saved.")
            click.echo("You can now run the server with: uv run ticktick-mcp run")
        else:
            click.echo(
                "❌ Authentication failed. Please check your username and password.",
            )
            sys.exit(1)

    except Exception as e:  # noqa: BLE001 - CLI surfaces any error message to user
        click.echo(f"❌ Authentication failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--host", default="localhost", help="Host for the callback server")
@click.option("--port", default=8000, help="Port for the callback server")
def run(host: str, port: int) -> None:  # noqa: ARG001 - reserved for future use
    """Run TickTick MCP server"""
    try:
        # Check authentication status
        auth_handler = TickTickAuth()

        if not auth_handler.is_authenticated():
            click.echo(
                "❌ Not authenticated. Please run authentication command first:",
                err=True,
            )
            click.echo("uv run ticktick-mcp auth", err=True)
            sys.exit(1)

        click.echo("🚀 Starting TickTick MCP server...", err=True)
        click.echo("Press Ctrl+C to stop server", err=True)

        # Run server
        try:
            asyncio.run(server_main())
        except KeyboardInterrupt:
            click.echo("\n🛑 Server stopped", err=True)
        except Exception as e:  # noqa: BLE001 - Report any startup error to CLI
            click.echo(f"❌ Server startup failed: {e}", err=True)
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped", err=True)


@cli.command()
def test() -> None:
    """Test TickTick MCP server configuration"""
    try:
        auth_handler = TickTickAuth()

        if not auth_handler.is_authenticated():
            click.echo("❌ Not authenticated. Please run authentication command first.")
            sys.exit(1)

        # Try to get client
        try:
            auth_handler.get_client()
            username = auth_handler.get_username()
            click.echo(f"✅ Configuration correct! Authenticated as: {username}")
            click.echo("✅ Client connection successful")
        except Exception as e:  # noqa: BLE001 - present full error in CLI
            click.echo(f"❌ Client connection failed: {e}")
            sys.exit(1)

    except Exception as e:  # noqa: BLE001 - present full error in CLI
        click.echo(f"❌ Test failed: {e}")
        sys.exit(1)


@cli.command()
def logout() -> None:
    """Logout and clear saved credentials"""
    try:
        auth_handler = TickTickAuth()

        if auth_handler.logout():
            click.echo("✅ Successfully logged out and cleared credentials")
        else:
            click.echo("❌ Logout failed")
            sys.exit(1)

    except Exception as e:  # noqa: BLE001 - present full error in CLI
        click.echo(f"❌ Logout failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
