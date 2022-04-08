from tokenize import Name
from fastapi import Query
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from numpy import record
from werkzeug.exceptions import abort
from flaskr import database

from flaskr.auth import login_required
from flaskr.database import get_database
from . import mysql

bp = Blueprint('manage', __name__, url_prefix='/manage')
import traceback
import sys

from . import cipher
from . import integrity

# ===========================


@bp.route('/')
@login_required
def index():
    return redirect(url_for('index'))

#=================================
#add student record
@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == "GET":
        if g.user is not None:
            global cred
            cred = cipher.AESCipher.generate_pwd(8)
            print(cred)
            return render_template('manage/add.html', cred=cred)
        else:
            return redirect(url_for('index'))
            

    if request.method == 'POST':
        Name = request.form['Name']
        Surname = request.form['Surname']
        Nin = request.form['NIN']
        Birth = request.form['Birth']
        #cred = request.form['cred']
        print(cred)


        database = get_database()
        error = None

        if not Name:
            error = 'Name is required.', 'Danger'
        elif not Surname:
            error = 'Surname is required.', 'Danger'
        elif not Nin:
            error = 'National Identification Number is required.', 'Danger'
        elif not Birth:
            error = 'Birth is required.', 'Danger'
        

        #cipher the values of name surname and birth
        if error is None:
            try:
                ciphered_tuple =  []
                for i in [Name, Surname, Birth]:
                    crypt = cipher.AESCipher(cred).encrypt(i).decode('utf-8')
            
                    ciphered_tuple.append(crypt)
                print(ciphered_tuple)
                ciphered_tuple.append(Nin)
                ciphered_tuple.append(cred)

                
                database.execute(
                    'INSERT INTO students (Name, Surname, Birth, NIN, Credential) VALUES (%s, %s, %s, %s, %s)', ciphered_tuple,)
                
                mysql.connection.commit()
                integrity.set_integrity(Nin)
                
                
            except database.IntegrityError:
                error = "Student "+Name+" "+Surname+" is already registered."
                
        if error is None:
            return redirect(url_for("index"))
        else:
            flash(error, "danger")
            return redirect(url_for("manage.add"))
            


    return render_template('manage/add.html')

#==============================
#Retrieve student data
@bp.route('/view', methods=('GET', 'POST'))
@login_required
def view():
    if request.method == 'POST':
        Nin = request.form['NIN']
        Credential = request.form['Credential']

        database = get_database()
        error = None

        if not Nin:
            error = 'National Identification Number is required.', 'Danger'
        elif not Credential:
            error = 'Credential is required.', 'Danger'

        global record 
        database.execute(
            'SELECT * FROM students  WHERE NIN = %s ', (Nin, )
        )
        record = database.fetchone()

        
        if Nin is None:
            error = 'Incorrect NIN.'
            flash(error, 'danger')
        elif not record:
            error = 'No record available.'
            flash(error, 'danger')
            return redirect(url_for('manage.view'))
        elif not record['Credential'] == Credential:
            error = 'Incorrect password.'
            flash(error, 'danger')
            return render_template('manage/view.html')
        else:
            if integrity.chk_integrity(Nin) is not True:
                error = 'Integrity check failed'
                print(integrity.chk_integrity(Nin))
                flash(error, 'danger')
            else:
                flash("Integrity Check correct", "success")
                print(integrity.chk_integrity(Nin))
                record['Name'] = cipher.AESCipher(Credential).decrypt(record['Name']).decode('utf-8')
                record['Surname'] = cipher.AESCipher(Credential).decrypt(record['Surname']).decode('utf-8')
                record['Birth'] = cipher.AESCipher(Credential).decrypt(record['Birth']).decode('utf-8')
                print(record['Name'])
                return render_template('manage/view.html', record=record)
            
        
    return render_template('manage/view.html')
