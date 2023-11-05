"""Database migrations manager"""


import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.models import User, UserType
from app import db, create_app


app = create_app(config_name=os.getenv('APP_MODE'))
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def seed():
    """Create the default administrator of the application"""
    user = User(
        username=os.getenv('DEFAULT_ADMIN_USERNAME'),
        email=os.getenv('DEFAULT_ADMIN_EMAIL'),
        password=os.getenv('DEFAULT_ADMIN_PASSWORD'),
        role=UserType.SUPER_ADMIN,
        token=''
    )
    user.save()
    print('manager: seed complete')


if __name__ == '__main__':
    manager.run()
