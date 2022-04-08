from importlib.resources import path
from ntpath import join
import os
from flask import *
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
#import MySQLdb.cursors

#create app setting up config
def create_app(test_config=None):
    # create an configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='test',
    )
    #mysql/mariadb config
    app.config['MYSQL_HOST'] = 'writ1.cqtsozzwj3vt.eu-west-2.rds.amazonaws.com'
    app.config['MYSQL_PORT'] = 3306
    app.config['MYSQL_USER'] = 'admin'
    app.config['MYSQL_PASSWORD'] = 'Secret_password'
    app.config['MYSQL_DB'] = 'APK_Uni'
    #set gobal mysql to be accesible from everywhere
    global mysql
    #inicialize MYSQL
    mysql = MySQL(app)
    #inicialize bootstrap
    Bootstrap(app)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Index page
    @app.route('/')
    def index():
        return render_template('index.html')
    #add al the modules created to the app enviroment
    from . import database
    database.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import management
    app.register_blueprint(management.bp)

    return app

