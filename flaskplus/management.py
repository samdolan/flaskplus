from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager

def get_manager(app, db):
    manager = Manager(app)

    manager.add_command('db', MigrateCommand)

    @manager.command
    def createdb():
        db.create_all()

    @manager.command
    def dropdb():
        db.drop_all()

    return manager
