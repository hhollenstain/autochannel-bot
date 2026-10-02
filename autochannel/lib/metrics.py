import logging
from functools import wraps
from typing import TYPE_CHECKING

from discord.ext import commands
from prometheus_client import Counter, Gauge, Summary

if TYPE_CHECKING:
    from discord import Guild

LOG = logging.getLogger("discord")
COMMAND_SUMMARY_VC = Summary("command_vc", "Time spent processing request")
COMMAND_SUMMARY_ACUPDATE = Summary("command_acupdate", "Time spent processing request")
COMMAND_COUNT = Counter("command_count", "time command was invoked", ["guild", "command"])
TASK_COUNT = Counter("task_count", "time command was invoked", ["guild", "task"])
QUEUE_COUNT = Gauge("autochan_queue_count", "Number of events in queue")
BOT_USER_COUNT = Gauge("autochan_bot_user_count", "bot user count stats")
BOT_GUILD_COUNT = Gauge("autochan_bot_guild_count", "bot guild count stats")


def bot_guild_count(num_of_guilds: int) -> None:
    """Update the bot guild count metric.

    Args:
        num_of_guilds: Number of guilds the bot is in.
    """
    BOT_GUILD_COUNT.set(num_of_guilds)


def bot_user_count(num_of_users: int) -> None:
    """Update the bot user count metric.

    Args:
        num_of_users: Number of users the bot knows about.
    """
    BOT_USER_COUNT.set(num_of_users)


def queue_stats_gauge(num_of_events: int) -> None:
    """Update the queue stats metric.

    Args:
        num_of_events: Number of events in the queue.
    """
    QUEUE_COUNT.set(num_of_events)


def command_metrics_counter(f):
    """Decorator to add command metrics to a cog method.

    Args:
        f: The command method to decorate.

    Returns:
        Wrapped async function with metrics tracking.
    """

    @wraps(f)
    async def wrapper(self: "commands.Cog", *args, **kwargs) -> None:
        guild: Guild = args[0].guild
        COMMAND_COUNT.labels(command=f"autochan.command.{f.__name__}", guild=guild).inc()
        LOG.debug(f'STATS INCR: autochannel_bot.command.{f.__name__}.count tags=[f"guild:{guild}"]')
        return await f(self, *args, **kwargs)

    return wrapper


def task_metrics_counter(f):
    """Decorator to add task metrics to a cog method.

    Args:
        f: The task method to decorate.

    Returns:
        Wrapped async function with metrics tracking.
    """

    @wraps(f)
    async def wrapper(self: "commands.Cog", *args, **kwargs) -> None:
        guild: Guild = args[0].guild
        TASK_COUNT.labels(task=f"autochan.task.{f.__name__}", guild=guild).inc()
        LOG.debug(
            f'STATS INCR: autochannel.task.command.{f.__name__}.count tags=[f"guild:{guild}"]'
        )
        return await f(self, *args, **kwargs)

    return wrapper
