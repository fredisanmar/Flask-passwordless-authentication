from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr import database

from flaskr.auth import login_required
from flaskr.database import get_database

bp = Blueprint('manage', __name__, url_prefix='/manage')

# ===========================


@bp.route('/')
@login_required
def index():
    #db = get_database()
    #posts = db.execute().fetchall()
    # return render_template('index.html', posts=posts)
    return redirect(url_for('index'))


@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        Name = request.form['Name']
        Surname = request.form['Surname']
        Birth = request.form['Birth']

        database = get_database()
        error = None

        if not Name:
            error = 'Name is required.', 'Danger'
        elif not Surname:
            error = 'Surname is required.', 'Danger'
        elif not Birth:
            error = 'Birth is required.', 'Danger'

        if error is None:
            try:
                database.execute(
                    'INSERT INTO students (Name, Surname, Birth) VALUES (?, ?, ?)', (Name, Surname, Birth),)
                database.commit()
            except database.IntegrityError:
                error = f"Student {Name} {Surname} is already registered."
            else:
                return redirect(url_for("index"))

        flash(error)
        if g.user is not None:
            return redirect(url_for('index'))
        else:
            return render_template('manage.add')

    return render_template('manage/add.html')


@bp.route('/view')
@login_required
def view():
    return render_template('manage/add.html')
