from importlib.resources import path
from ntpath import join
import os
from flask import *
from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    # create an configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='test',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
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

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')

    from . import database
    database.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import management
    app.register_blueprint(management.bp)
    #app.add_url_rule('/', endpoint='index')
    return app

