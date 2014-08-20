# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from bitcharts.database import manager as database_manager
from bitcharts import app


manager = Manager(app, with_default_commands=False)

manager.add_command('database', database_manager)


if __name__ == "__main__":
    manager.run()
