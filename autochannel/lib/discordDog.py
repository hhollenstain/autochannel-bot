import asyncio
import datadog
import logging
from functools import wraps
from time import time

LOG = logging.getLogger('discord')

def dd_command_count(f):
    """
    """
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        self.stats.increment(f'autochannel_bot.command.{f.__name__}.count')
        LOG.debug(f'STATS INCR: autochannel_bot.command.{f.__name__}.count')
        return await f(self, *args, **kwargs)
    return wrapper

def dd_task_count(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        self.stats.increment(f'autochannel_bot.task.{f.__name__}.count')
        LOG.debug(f'STATS INCR: autochannel_bot.task.{f.__name__}.count')
        return await f(self, *args, **kwargs)
    return wrapper

def dd_agent_check(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.agent:
            func = getattr(self.agent, f.__name__)
            return func(*args, **kwargs)
        else:
            LOG.info('No Datadog agent found...')
    return wrapper

class DDAgent:

    def __init__(self, dd_api_key=None, dd_app_key=None, **kwargs): 
        self.dd_api_key = dd_api_key
        self.dd_app_key = dd_app_key
        self.env = kwargs.get('env')
        self.constant_tags = kwargs.get('constant_tags')
        self.agent = None

        if dd_api_key and dd_app_key:
            datadog.initialize(api_key=dd_api_key, app_key=dd_app_key)
            self.agent = datadog.ThreadStats(constant_tags=self.constant_tags)
            self.agent.start()
        if self.agent:
            LOG.info('Datadog agent found: Will report metrics successfully')
        else:
            LOG.info ('Datadog agent not found: Will not report metrics')

    @dd_agent_check
    def send(self, *args, **kwargs):
        pass

    @dd_agent_check
    def set(self, *args, **kwargs):
        pass

    @dd_agent_check
    def event(self, *args, **kwargs):
        pass

    @dd_agent_check
    def increment(self, *args, **kwargs):
        pass
