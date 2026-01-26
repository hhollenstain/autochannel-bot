import os
import logging
import coloredlogs
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
""" AC Imports"""
from autochannel.ui.lib import utils
from autochannel.ui import create_app
from autochannel.data import db
from autochannel.data.models import Guild, Category


def main():
    # args = utils.parse_arguments()
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install(level=0,
                        fmt="[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        isatty=True)
    # if args.debug:
    #     l_level = logging.DEBUG
    #     app.debug = True
    # else:
    #     l_level = logging.INFO
    l_level = logging.INFO
    logging.getLogger(__package__).setLevel(l_level)
    logging.getLogger('websockets.protocol').setLevel(l_level)
    logging.getLogger('urllib3').setLevel(l_level)

    app = create_app()
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    manager.run()


if __name__ == '__main__':
    main()