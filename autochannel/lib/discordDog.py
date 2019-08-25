import asyncio
import datadog
import logging
from functools import wraps
from time import time

LOG = logging.getLogger('discord')

# def dd_timed(inner_dec):
#     def ddmain(outer_dec):
#         def decwrapper(f):
#             wrapped = inner_dec(outer_dec(f))
#             LOG.info(f'{args}, {kwargs}')
#             def fwrapper(*args, **kwargs):
#                return wrapped(f'autochannel_bot.{f.__name__}.time')
#                LOG.info(f'timed wrapper: autochannel_bot.{f.__name__}.time')
#             return fwrapper
#         return decwrapper
#     return ddmain

def dd_command_timed(f):
    """
    """
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        self.stats.agent.timed(f'autochannel_bot.command.{f.__name__}.time')
        LOG.info(f'Timed command for : autochannel_bot.command.{f.__name__}.time')
        return await f(self, *args, **kwargs)
    return wrapper

def dd_task_timed(f):
    """
    """
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        self.stats.agent.timed(f'autochannel_bot.task.{f.__name__}.time')
        self.stats.agent.flush()
        LOG.debug(f'Timed command for : autochannel_bot.task.{f.__name__}.time')
        return await f(self, *args, **kwargs)
    return wrapper

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

    @dd_agent_check
    def incr(self, *args, **kwargs):
        pass
    
    @dd_agent_check
    def timed(self, *args, **kwargs):
        pass

    @dd_agent_check
    def timer(self, *args, **kwargs):
        pass

    @dd_agent_check
    def timing(self, *args, **kwargs):
        # self.agent.timed(*args)
        pass
