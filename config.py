"""
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

UPLOAD_FOLDER='static/uploads'
ALLOWED_EXTENTIONS= set (['png','jpg','jpeg','gif'])

#configuration
DEBUG = True
SECRET_KEY='develompent key'
MYSQL_DATABASE_USER ='root'
MYSQL_DATABASE_PASSWORD = 'root'
MYSQL_DATABASE_DB = 'frontend'
MYSQL_DATABASE_HOST = 'localhost'
CHECK_IN_INTERVAL= datetime.timedelta(minutes=10)
API_URL='http://localhost' 
API_PORT=8080
