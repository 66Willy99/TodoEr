import mysql.connector

import click

from flask import current_app, g #g is used to save the user of the app
from flask.cli import with_appcontext #used to enter the context of the app
from .schema import instructions

def getDb():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DATABASE_HOST'], #TO SET ON CMD WOKRS WITH set FLASK_DATABASE_HOST=localhost
            user=current_app.config['DATABASE_USER'], #TO SET ON CMD WOKRS WITH set FLASK_DATABASE_USER=%user%
            password=current_app.config['DATABASE_PASSWORD'], #TO SET ON CMD WOKRS WITH set FLASK_DATABASE_PASSWORD=%password%
            database=current_app.config['DATABASE'] #TO SET ON CMD WOKRS WITH set FLASK_DATABASE=%database%
        )
        g.c = g.db.cursor(dictionary=True)
    return g.db, g.c

def closeDb(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def initDb():
    db, c = getDb()
    for i in instructions:
        c.execute(i)
    db.commit()

@click.command('init-db') #"flask init-db" command to initialize the database
@with_appcontext #to enter the context of the app
def initDbCommand():
    initDb()
    click.echo('Base de datos inicializada')

def initApp(app):
    app.teardown_appcontext(closeDb)
    app.cli.add_command(initDbCommand) #add the command to the app
    
