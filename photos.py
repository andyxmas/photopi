# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import picamera
import datetime
import os
import sys
import datetime

DEBUG = True
# configuration
DATABASE = 'photos.db'
SECRET_KEY = 'with random words will it be secure development key?'
USERNAME = 'marco'
PASSWORD = 'lionel-christmas'
PHOTO_DIRECTORY = 'static/photos/'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#Visible Webpages
@app.route('/')
def show_photos():
    cur = g.db.execute('select date, title, text, id, filename from photos order by id desc')
    photos = [dict(date=row[0], title=row[1], text=row[2], id=row[3], filename=row[4]) for row in cur.fetchall()]
    return render_template('show_photos.html', photos=photos)

@app.route('/take-photo')
def take_photo():
    return render_template('take_photo.html') 

#Functional URLs

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_photos'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_photos'))

@app.route('/add', methods=['POST'])
def add_photo():
    if not session.get('logged_in'):
        abort(401)
    photo_filename = datetime.datetime.now().strftime("photo_%d-%m-%Y-%H-%M-%S.jpg")
    photo_location = app.config['PHOTO_DIRECTORY'] + photo_filename
    g.db.execute('insert into photos (date, title, text, filename) values (?, ?, ?, ?)',
                 [datetime.datetime.now(), request.form['photo-title'], request.form['photo-desc'], photo_filename])
    g.db.commit()
    with picamera.PiCamera() as camera:
        camera.brightness = (int(request.form['brightness']))
        camera.ISO = (int(request.form['ISO']))
	camera.awb_mode = (request.form['awb_mode'])
	camera.contrast = (int(request.form['contrast']))
	camera.exposure_compensation = (int(request.form['exposure_compensation']))
	camera.exporsure_mode = (request.form['exposure_mode'])
        camera.capture(photo_location, format = 'jpeg', quality = int(request.form['jpg-quality']))
    flash('New photo was successfully posted', 'success')
    return redirect(url_for('show_photos'))

@app.route('/delete', methods=['POST'])
def delete_photo():
    if not session.get('logged_in'):
        abort(401)
    try:
        g.db.execute('DELETE FROM photos WHERE id=' + request.form['id'])
        g.db.commit()
    except:
        flash('Something went wrong with deleting the db record', 'danger')
    else:
        flash('Photo entry was succesfully deleted from db', 'success')
    
    try:
        os.remove(app.config['PHOTO_DIRECTORY'] + request.form['filename'])
    except:
        flash('Something went wrong with deleting the photo file:', 'danger')
        flash(str(sys.exc_info()), 'warning')
    else:
        flash('The photo file was succesfully deleted', 'success')
    return redirect(url_for('show_photos'))

#Run this on the little dev server
if __name__ == '__main__':
#    app.debug = True
    app.run(host='0.0.0.0', port=8080)
