import discord
import logging
import importlib
import sys

LOG = logging.getLogger(__name__)

async def load(extension, client):

    try:
        #lib = importlib.import_module(extension, package="tamago")
        lib = importlib.import_module(extension)
        if not hasattr(lib, 'setup'):
            del lib
            del sys.modules["autochannel%s" % extension]

            raise discord.ClientException('extension does not have a setup function')

        await lib.setup(client)
        LOG.info('Loaded extension: {}'.format(extension))
    except Exception as e:
        LOG.error('{} extension can not be loaded. [{}]'.format(extension, e))
