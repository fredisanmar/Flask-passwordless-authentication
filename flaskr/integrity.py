
from flask import flash
from flaskr.database import get_database
from . import mysql



#check the integrity
def chk_integrity(Nin):
    database = get_database()
    database.execute(
                    'SELECT md5(CONCAT(Name,Surname, Birth)) FROM students WHERE NIN = %s', (Nin,))
    temp_hash = database.fetchone()
    mysql.connection.commit()

    database = get_database()
    #print(Nin)
    try:
        database.execute(
                    'SELECT * FROM integrity WHERE NIN = %s', (Nin,))
        stored_hash = database.fetchone()
        print(stored_hash)
        mysql.connection.commit()
    except:
        error = "record for integrity not available"
        flash(error, 'danger')

    if stored_hash is None:
        return False
    elif temp_hash['md5(CONCAT(Name,Surname, Birth))'] != stored_hash['checksum']:
        return False 
    elif temp_hash['md5(CONCAT(Name,Surname, Birth))'] == stored_hash['checksum']:
        return True
    else:
        return False


# set integrity point
def set_integrity(Nin):
    database = get_database()
    database.execute(
                    'SELECT md5(CONCAT(Name,Surname, Birth)) FROM students WHERE NIN = %s', (Nin,))
                #database.execute(
                #    'INSERT INTO checks (NIN, chipher) VALUES (%s, %s, %s, %s, %s)', ciphered_tuple,)
    mysql.connection.commit()
    hash = database.fetchone()
    print(hash)
    database.execute(
                    'INSERT INTO integrity (NIN, checksum) VALUES (%s, %s)', (Nin, hash['md5(CONCAT(Name,Surname, Birth))'],),)
    mysql.connection.commit()
