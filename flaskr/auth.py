from cgi import test
import functools
from lib2to3.pgen2 import token


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.database import get_database

import pyotp

bp = Blueprint('auth', __name__, url_prefix='/auth')

# =======================

# register function


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "GET":
        # generating random secret key for authentication
        global secret
        secret = pyotp.random_base32()
        print(secret)

    if request.method == 'POST':
        username = request.form['username']
        #password = request.form['password']

        database = get_database()
        error = None

        if not username:
            error = 'Username is required.'
        # elif not password:
        #    error = 'Password is required.'

        if error is None:
            try:
                print(username)
                database.execute(
                    'INSERT INTO user (username, secret_key) VALUES (?, ?)', (username, secret,),)
                database.commit()
            except database.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    if g.user is not None:
        return redirect(url_for('index'))
    else:
        return render_template('auth/register.html', secret=secret)


# =========================
# login

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        token = request.form['token']
        db = get_database()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        # print(user['secret_key'])

        if user is None:
            error = 'Incorrect username.'
        else:
            if pyotp.TOTP(user['secret_key']).verify(token):
                # inform users if OTP is valid
                flash("The TOTP 2FA token is valid", "success")
                print("The TOTP 2FA token is valid", "success")
                # return redirect(url_for("auth.login"))
            else:
                # inform users if OTP is invalid
                flash("You have supplied an invalid 2FA token!", "danger")
                error = "You have supplied an invalid 2FA token!"
        # check_password_hash(user['password'], password):
        #error = 'Incorrect password.'
        # elif

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['logged_in'] = True
            return redirect(url_for('manage.index'))
        if error == 'Incorrect username.':
            flash(error, "danger")
    if g.user is not None:
        return redirect(url_for('index'))

    return render_template('auth/login.html')


# =================================
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_database().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# =================


@bp.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('index'))


# ======================
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
