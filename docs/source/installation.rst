Photopi Installation
====================

Pre-requisites
--------------

 - Enable camera on raspberry pi and restart: ``sudo raspi-config``
 - Intstall picamera ``pip install picamera`` - http://picamera.readthedocs.org/
 - Install Flask ``pip install flask`` - http://flask.pocoo.org/

Configuration
-------------

 - Open a firewall port on the raspberry pi
	- sudo nano /etc/iptables.firewall.rules
	- sudo iptables-restore < /etc/iptables.firewall.rules
 - Set the port in the flask app ``app.run(host='0.0.0.0', port=8080)``

Initialise the database
-----------------------

From the python interpreter::

    from photos import init_db
    init_db()
