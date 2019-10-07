import asyncio
import logging
import time
from functools import wraps
from prometheus_client import Counter, Summary, Gauge

LOG = logging.getLogger('discord')
COMMAND_SUMMARY_VC = Summary('command_vc', 'Time spent processing request')
COMMAND_SUMMARY_ACUPDATE = Summary('command_acupdate', 'Time spent processing request')
COMMAND_COUNT = Counter('command_count', 'time command was invoked', ['guild', 'command'])
TASK_COUNT = Counter('task_count', 'time command was invoked', ['guild', 'task'])
QUEUE_COUNT = Gauge('autochan_queue_count', 'Number of events in queue')
BOT_USER_COUNT = Gauge('autochan_bot_user_count', 'bot user count stats')
BOT_GUILD_COUNT = Gauge('autochan_bot_guild_count', 'bot guild count stats')


def bot_guild_count(num_of_guilds):
    """[summary]
    
    Arguments:
        num_of_guilds {[type]} -- [description]
    """
    BOT_GUILD_COUNT.set(num_of_guilds)   

def bot_user_count(num_of_users):
    """[summary]
    
    Arguments:
        num_of_users {[type]} -- [description]
    """
    BOT_USER_COUNT.set(num_of_users)   

def queue_stats_gauge(num_of_events):
    """[summary]
    
    Arguments:
        num_of_events {[type]} -- [description]
    """
    QUEUE_COUNT.set(num_of_events)   

def command_metrics_counter(f):
    """[summary]
    
    Arguments:
        f {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        guild = args[0].guild
        COMMAND_COUNT.labels(command=f'autochan.command.{f.__name__}', guild=guild).inc()
        LOG.debug(f'STATS INCR: autochannel_bot.command.{f.__name__}.count tags=[f"guild:{guild}"]')
        return await f(self, *args, **kwargs)
    return wrapper


def task_metrics_counter(f):
    """[summary]
    
    Arguments:
        f {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        guild = args[0].guild
        TASK_COUNT.labels(task=f'autochan.task.{f.__name__}', guild=guild).inc()
        LOG.debug(f'STATS INCR: autochannel.task.command.{f.__name__}.count tags=[f"guild:{guild}"]')
        return await f(self, *args, **kwargs)
    return wrapper

