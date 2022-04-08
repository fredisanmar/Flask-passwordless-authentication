import sqlite3
from . import mysql
from flask_mysqldb import MySQLdb
import sys
import click
from flask import current_app, g
from flask.cli import with_appcontext



#init config to inicialize the remote DB
init_config = {
    'host': 'writ1.cqtsozzwj3vt.eu-west-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'FeCDv7szQ4WKpG'
}

#function to generate the DB connection
def get_database():
    if 'database' not in g:
        g.database = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return g.database

#Disconect from database
def close_database(e=None):
    database = g.pop('database', None)

    if database is not None:
        database.close()


#inicialize the DB making use of schema.sql file stored in local machine
def init_db():
    conn = MySQLdb.connect(**init_config)
    database = conn.cursor()
    #g.database.row_factory = mariadb.R

    with current_app.open_resource('schema.sql') as f:
        fd = f.read().decode('utf-8')
        sqlCommands = fd.split(';')
        for commands in sqlCommands:
            try:
                database.execute(commands)
            except:
                print("Command skipped: ")

#Define the init-db command
@click.command('init-db')
@with_appcontext
def init_database_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# register functions in the app enviroment


def init_app(app):
    app.teardown_appcontext(close_database)
    app.cli.add_command(init_database_command)
