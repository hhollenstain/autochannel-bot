"""Utility functions for AutoChannel bot."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from datetime import datetime
from itertools import cycle, islice

import discord
from discord.ext import commands

from autochannel import VERSION
from autochannel.lib.metrics import bot_guild_count, bot_user_count

LOG = logging.getLogger(__name__)
BLOCKED_USERS = os.getenv("BLOCKED_USERS") or "123456"


def timediff(channelTime: datetime, currentTime: datetime) -> int:
    """Calculate time difference in seconds.

    Args:
        channelTime: The starting datetime.
        currentTime: The current datetime.

    Returns:
        Difference in seconds.
    """
    tdiff = int((currentTime - channelTime).total_seconds())
    return tdiff


def to_int(value: str) -> int:
    """Convert string to int, removing commas.

    Args:
        value: String value possibly containing commas.

    Returns:
        Int value without commas.
    """
    if isinstance(value, str):
        return int(value.replace(",", ""))
    return int(value)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

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
        help="enable debug",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=VERSION,
        help="show the version number and exit",
    )
    return parser.parse_args()


def take(n: int, iterable) -> list:
    """Return first n items of the iterable as a list.

    Args:
        n: Number of items to take.
        iterable: Iterable to take items from.

    Returns:
        List of first n items.
    """
    return list(islice(iterable, n))


def friendly_time(seconds: int) -> str:
    """Format seconds as a human-readable time string.

    Args:
        seconds: Number of seconds.

    Returns:
        Human-readable time string.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    periods = [("hours", hours), ("minutes", minutes), ("seconds", seconds)]
    time_string = ", ".join(f"{value} {name}" for name, value in periods if value)

    return time_string


def message_check(message: discord.Message, mentions: set[int]) -> bool:
    """Check if message author is in mentions.

    Args:
        message: Discord message.
        mentions: Set of user IDs.

    Returns:
        True if author is in mentions.
    """
    return message.author.id in mentions


def missing_numbers(L: list[int]) -> list[int]:
    """Find missing numbers in a sorted sequence.

    Args:
        L: List of integers.

    Returns:
        List of missing numbers.
    """
    start, end = 1, len(L) + 1
    return sorted(set(range(start, end + 1)).difference(L))


def block_check():
    """Create a check that blocks certain users.

    Returns:
        A discord.py check function.
    """

    return commands.check(lambda ctx: str(ctx.author.id) not in BLOCKED_USERS)


async def change_status(client: commands.Bot) -> None:
    """Change bot status periodically based on environment settings.

    Args:
        client: The bot instance.
    """
    await client.wait_until_ready()

    games = os.environ.get("GAMES")
    if games:
        activities = cycle(games.split(","))

        while not client.is_closed():
            current_activity = next(activities)
            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(name=current_activity, type=discord.ActivityType.playing),
            )
            await asyncio.sleep(300)
    else:
        while not client.is_closed():
            guild_count = len(client.guilds)
            current_activity: str = f"Serving {guild_count} Discord servers!"
            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(name=current_activity, type=discord.ActivityType.playing),
            )
            await asyncio.sleep(300)


async def list_servers(client: commands.Bot) -> None:
    """Log and track server count metrics.

    Args:
        client: The bot instance.
    """
    await client.wait_until_ready()
    while not client.is_closed():
        server_list = [server.name for server in client.guilds]
        bot_guild_count(len(server_list))
        LOG.debug(f"Current servers: {server_list}")
        await asyncio.sleep(600)


async def list_users(client: commands.Bot) -> None:
    """Track user count metrics.

    Args:
        client: The bot instance.
    """
    await client.wait_until_ready()
    while not client.is_closed():
        numb_of_clients: int = len(client.users)
        bot_user_count(numb_of_clients)
        LOG.debug(f"Number Of clients: {numb_of_clients}")
        await asyncio.sleep(600)
