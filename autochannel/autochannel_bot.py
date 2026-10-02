#!/usr/bin/env python3
"""AutoChannel Bot - Main entrypoint for the Discord bot application."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

import coloredlogs
import discord
from prometheus_client import start_http_server

from autochannel import VERSION
from autochannel.autochannel import AutoChannel

EXTENSIONS: list[str] = [
    "autochannel.lib.plugins.autochannels",
    "autochannel.lib.plugins.join",
    "autochannel.lib.plugins.server",
]

LOG = logging.getLogger(__name__)

APP_ID: str = os.getenv("APP_ID") or "fakeid"
BOT_PREFIX: tuple[str, ...] = ("?", "!")
DBL_TOKEN: str | None = os.getenv("DBL_TOKEN")
SHARD: str = os.getenv("SHARD") or "0"
SHARD_COUNT: str = os.getenv("SHARD_COUNT") or "1"
TOKEN: str | None = os.getenv("TOKEN")
VOICE_CHANNEL_PREFIX: str = os.getenv("VOICE_CHANNEL_PREFIX") or "!VC "
AUTO_CHANNEL_PREFIX: str = os.getenv("AUTO_CHANNEL_PREFIX") or "!AC "
AUTO_CATEGORIES: list[str] = (os.getenv("AUTO_CATEGORIES") or "auto-voice").lower().split(",")
TESTING_GUILD_ID: str | None = os.getenv("TESTING_GUILD_ID")
ENV: str | None = os.getenv("ENV")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the bot.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="AutoChannel Discord Bot",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Show version and exit",
    )
    return parser.parse_args()


def setup_logging(args: argparse.Namespace) -> None:
    """Configure logging for the application.

    Args:
        args: Command line arguments.
    """
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_fmt = "[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s"

    logging.basicConfig(level=log_level, format=log_fmt)
    coloredlogs.install(
        level=0,
        fmt=log_fmt,
        isatty=True,
    )

    logging.getLogger(f"{__package__}").setLevel(log_level)
    logging.getLogger("discord").setLevel(log_level)
    logging.getLogger("websockets.protocol").setLevel(log_level)
    logging.getLogger("urllib3").setLevel(log_level)


async def run_autochannel() -> None:
    """Main entrypoint for running the AutoChannel bot.

    This function sets up the bot with proper intents and configuration,
    starts the metrics server, and runs the bot.
    """
    args = parse_arguments()
    setup_logging(args)

    LOG.info("LONG LIVE AutoChannel bot")

    intents = discord.Intents.default()
    LOG.info(f"Intents: {intents}")

    autochannel = AutoChannel(
        shard_id=int(SHARD),
        shard_count=int(SHARD_COUNT),
        command_prefix=BOT_PREFIX,
        app_id=APP_ID,
        voice_channel_prefix=VOICE_CHANNEL_PREFIX,
        auto_channel_prefix=AUTO_CHANNEL_PREFIX,
        auto_categories=AUTO_CATEGORIES,
        env=ENV,
        dbl_token=DBL_TOKEN,
        intents=intents,
        initial_extensions=EXTENSIONS,
        testing_guild_id=TESTING_GUILD_ID,
    )

    start_http_server(8000)
    await autochannel.start(TOKEN)


def main() -> None:
    """Synchronous entrypoint that runs the async bot."""
    asyncio.run(run_autochannel())


if __name__ == "__main__":
    main()
