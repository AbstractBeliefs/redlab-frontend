"""
file: config.py
Implementation of fronted for Checkin-Beacon project
Configuration file for frontend server
Edinburgh Napier University 3rd year group project 2015/2016
Group members: 
	Christopher Caira
	Przmeyslaw Beniamin Dorzak
	Edward Kellet
	Braian Lawes
	Gareth Pulham
	
Author - Przemyslaw Beniamin Dorzak
Design - Przmeyslaw Beniamin Dorzak / Gareth Pulham

"""

import datetime			#calculate time periods
import logging

UPLOAD_FOLDER='static/uploads'
ALLOWED_EXTENTIONS= set (['png','jpg','jpeg','gif'])

#configuration
DEBUG = True
SECRET_KEY='develompent key'
MYSQL_DATABASE_USER ='frontend'
MYSQL_DATABASE_PASSWORD = 'vC6qj39A9zPZDbdj'
MYSQL_DATABASE_DB = 'frontend'
MYSQL_DATABASE_HOST = 'localhost'
CHECK_IN_INTERVAL= datetime.timedelta(minutes=10)
API_URL='https://api.checkinbeacon.pulham.info' 
API_PORT=443

logging.basicConfig(format="RedLab Frontend: %(levelname)s: %(message)s", level=logging.INFO)
