from cgi import test
import functools
from lib2to3.pgen2 import token

from flaskr import database
from . import mysql

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.database import get_database

import pyotp

#blueprint to define a prefix to the endpoints

bp = Blueprint('auth', __name__, url_prefix='/auth')

# =======================

# register function


@bp.route('/register', methods=('GET', 'POST'))
def register():
    #render the index if the you are logged in
    if request.method == "GET":
        if g.user is not None:
            return redirect(url_for('index'))
        else:
            # generating random secret key for authentication
            global secret
            secret = pyotp.random_base32()
            print(secret)
            return render_template('auth/register.html', secret=secret)

    if request.method == 'POST':
        username = request.form['username']

        #call DB to interact
        database = get_database()
        error = None

        #check if in the request exist the username parameter
        if not username:
            error = 'Username is required.'

        #if no errors rised the data entered is inserted into the database (Username and secret generated)
        if error is None:
            try:
                print(username)
                database.execute(
                    'INSERT INTO user (username, secret_key) VALUES (%s, %s)', (username, secret,),)
                mysql.connection.commit()
            except database.IntegrityError:
                error = f"User {username} is already registered."
                
                flash(error, 'danger')
                return redirect(url_for("auth.register"))
            else:
                return redirect(url_for("auth.login"))
                
# =========================
# login function

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        token = request.form['token']
        database = get_database()
        error = None
        #check the username entered to get the data
        database.execute(
            'SELECT * FROM user WHERE username = %s', [username,]
        )
        user = database.fetchone()
        # print(user['secret_key'])

        #if the user doesn't exist raise error
        if user is None:
            error = 'Incorrect username.'
        else:
            #cast the results to select the secret key and verifythe token entered
            if pyotp.TOTP(user['secret_key']).verify(token):
                # rise error none to flash at the end the correct login message
                error = None
            else:
                # inform users if OTP is invalid
                error = "You have supplied an invalid TOTP token!"

        #if no error generates the user session, flash the correct login message and redirect to index. if error exist flash the error message.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['logged_in'] = True
            flash("The TOTP token is valid", "success")
            return redirect(url_for('index'))
        else:
            flash(error, "danger")
    #if correct login happens return to index
    if g.user is not None:
        return redirect(url_for('index'))

    return render_template('auth/login.html')


# =================================
#if session cookie exist check if its correct before the app load
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        database = get_database()
        database.execute(
            'SELECT * FROM user WHERE id = %s', [user_id,]
        )
        g.user = database.fetchone()
        print(g.user)

# =================
#logout


#clear the session

@bp.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('index'))


# ======================
#define a function to make some endpoint not accesible if not loged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
