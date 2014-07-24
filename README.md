Photopi!
========

Photopi is a flask app, that provides a web-based interface to taking and managing photos using a raspberry pi and picamera.

Requirements
-----------

 - Raspberry Pi, this has been developed on Raspian
 - Python 2.7
 - Raspberry Pi Camera module
 - (Picamera)[http://picamera.readthedocs.org/]
 - (Flask)[http://flask.pocoo.org/]

Installation
------------

 - Always best to start by creating a new (virtualenv)[http://virtualenvwrapper.readthedocs.org/en/latest/]
 - @todo - do a run through and give the actual commands for install all this:

 - argparse (1.2.1)
 - docutils (0.11)
 - ExifRead (1.4.2)
 - Flask (0.10.1)
 - itsdangerous (0.23)
 - Jinja2 (2.7.2)
 - MarkupSafe (0.18)
 - picamera (1.5)
 - pip (1.5.2)
 - Pygments (1.6)
 - setuptools (2.1)
 - Sphinx (1.2.1)
 - Werkzeug (0.9.4)
 - wsgiref (0.1.2)

Setup
-----
 - Made a copy of the default config `cp photopi.default_settings photopi.settings`
 - Edit the config file and add a secure username and password `nano photopi.settings`
 - run photopi `python photos.py`
 - you can access photopi at http://localhost:8080
