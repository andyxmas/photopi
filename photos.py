# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import picamera
import datetime

DEBUG = True
# configuration
DATABASE = 'photos.db'
SECRET_KEY = 'with random words will it be secure development key?'
USERNAME = 'admin'
PASSWORD = 'default'

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

@app.route('/')
def show_photos():
    cur = g.db.execute('select date, title, text, id, filename from photos order by id desc')
    photos = [dict(date=row[0], title=row[1], text=row[2], id=row[3], filename=row[4]) for row in cur.fetchall()]
    return render_template('show_photos.html', photos=photos)

@app.route('/add', methods=['POST'])
def add_photo():
    if not session.get('logged_in'):
        abort(401)
    photo_filename = 'photo_' + str(datetime.datetime.now()) + '.png'
    g.db.execute('insert into photos (date, title, text, filename) values (?, ?, ?, ?)',
                 [datetime.datetime.now(), request.form['photo-title'], request.form['photo-desc'], photo_filename])
    g.db.commit()
    with picamera.PiCamera() as camera:
        camera.capture(photo_filename)
    flash('New photo was successfully posted')
    return redirect(url_for('show_photos'))

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

@app.route('/shoot')
def shoot():
    with picamera.PiCamera() as camera:
        camera.capture('photo_test123.png', thumbnail)
    return redirect(url_for('show_photos'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
