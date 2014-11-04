#!/usr/bin/env python

# all the imports
from __future__ import unicode_literals
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

#check that picamera is available. if not, we'll fail new photos greacefully
import imp
try:
    imp.find_module('picamera')
    picamera_available = True
    import picamera
except ImportError:
    picamera_available = False

import datetime
import os
import sys
import datetime
import exifread
from PIL import Image
import glob

# create our little application :)
app = Flask(__name__)

# config
app.config.from_pyfile('photopi.default_config')
app.config.from_pyfile('photopi.config')
# app.config.from_object(__name__)

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
    return render_template('show_photos_icons.html', photos=photos)

@app.route('/list_view')
def show_photos_list():
    cur = g.db.execute('select date, title, text, id, filename from photos order by id desc')
    photos = [dict(date=row[0], title=row[1], text=row[2], id=row[3], filename=row[4]) for row in cur.fetchall()]
    return render_template('show_photos_list.html', photos=photos)

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
    
# if picamera modules is not available, fail gracefully
    if not (picamera_available):
        flash('Picamera module is not available - not possible to take photo', 'error')
        return redirect(url_for('show_photos'))
        
    photo_filename = datetime.datetime.now().strftime("photo_%d-%m-%Y-%H-%M-%S.jpg")
    photo_location = app.config['PHOTO_DIRECTORY'] + photo_filename
    g.db.execute('insert into photos (date, title, text, filename) values (?, ?, ?, ?)',
                 [datetime.datetime.now(), request.form['photo-title'], request.form['photo-desc'], photo_filename])
    g.db.commit()

    brightness = "camera.brightness = " + (request.form['brightness'])
    iso = "camera.ISO = " + (request.form['ISO'])
    awb = "camera.awb_mode = " + (request.form['awb_mode'])
    contrast = "camera.contrast = " + (request.form['contrast'])
    sharpness = "camera.sharpness = " + (request.form['sharpness'])
    exposure_compensation = "camera.exposure_compensation = " + (request.form['exposure_compensation'])
    exposure_mode = "camera.exposure_mode = " + (request.form['exposure_mode'])
    vflip = "camera.vflip = " + (request.form['vflip'])
    hflip = "camera.hflip = " + (request.form['hflip'])
    image_effect = "camera.image_effect = " + (request.form['image_effect'])
    meter_mode = "camera.meter_mode = " + (request.form['meter_mode'])
    shutter_speed = "camera.shutter_speed = " + (request.form['shutter_speed'])

    with picamera.PiCamera() as camera:
  	camera.brightness = (int(request.form['brightness']))
        camera.ISO = (int(request.form['ISO']))
	camera.awb_mode = (request.form['awb_mode'])
	camera.contrast = (int(request.form['contrast']))
        camera.sharpness = (int(request.form['sharpness']))
	camera.exposure_compensation = (int(request.form['exposure_compensation']))
	camera.exposure_mode = (request.form['exposure_mode'])
        camera.vflip = (request.form['vflip'])
        camera.hflip = (request.form['hflip'])
	camera.image_effect = (request.form['image_effect'])
	camera.meter_mode = (request.form['meter_mode'])
	camera.shutter_speed = (int(request.form['shutter_speed']))
	camera.capture(photo_location, format = 'jpeg', quality = int(request.form['jpg-quality']), thumbnail = (64, 48, 35))

    file, ext = os.path.splitext(photo_location)
    im = Image.open(photo_location)
    size = 253, 189
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(file + "_thumb.jpg", "JPEG")

    flash('New photo was successfully posted', 'success')
    flash (brightness + ' | ' +
	iso + ' | ' +
	awb + ' | ' +
	contrast +  ' | ' +
        sharpness +  ' | ' +
        exposure_compensation + ' | ' +
        exposure_mode + ' | ' +
        vflip + ' | ' +
        hflip + ' | ' +
        image_effect + ' | ' +
        meter_mode + ' | ' +
        shutter_speed,
	 'info')
    return redirect(url_for('show_photos'))

@app.route('/show_exif/<photo_id>')
def show_exif(photo_id):
    # filename = request.form['filename']
    query = 'select filename from photos WHERE id=%s' % str(photo_id)
    cur = g.db.execute(query)
    result = cur.fetchone()
    filename = str(result[0])
    photo_location = app.config['PHOTO_DIRECTORY'] + filename
    if filename[-4:] == '.jpg':
        f = open(photo_location, 'rb')
	exif = exifread.process_file(f)
	return render_template('show_exif.html', exif=exif, photo_id = photo_id)
    else:
	txt = filename
	flash(txt, 'error')
	return redirect(url_for('show_photos'))

@app.route('/regen_thumbnails')
def regen_thumbs():
    size = 253, 189

    for filePath in glob.glob("static/photos/*thumb*"):
    if os.path.isfile(filePath):
        os.remove(filePath)

    for infile in glob.glob("static/photos/*.jpg"):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(file + "_thumb.jpg", "JPEG")
#    except:
#        flash('Something went wrong with thumbnail generation', 'danger')
#    else:
#        flash('thumbnail generation looks to have worked', 'info')

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

@app.route('/edit', methods=['POST'])
def edit_photo():
    if not session.get('logged_in'):
        abort(401)
    try:
        #g.db.execute('UPDATE PHOTOS SET TITLE=' + request.form['value'] + 'WHERE ID=' + request.form['pk'])
        g.db.execute('UPDATE photos SET title=? WHERE id=?', (str(request.form['value']), str(request.form['pk'])))
	g.db.commit()
    except:
        flash('Something went wrong with editing the photo title', 'danger')
    else:
        flash('Photo title succesfully updated', 'success')
    return redirect(url_for('show_photos'))

#Run this on the little dev server
if __name__ == '__main__':
#    app.debug = True
    app.run(host='0.0.0.0', port=8080)
