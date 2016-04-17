
"""
Implementation of fronted for Checkin-Beacon project
Funcitons to access database
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
import config
from contextlib import closing # for mysql  cursor witch closing clasue
import MySQLdb as mdb
import logging

def add_new_user(username,password):
	"""
	Adds new user to database
	parameters:
		username - string containing login of new user
		password - string containing password to be stored for new user
	returns:
		error message
	"""
	error=None
	# check if user of specified login allready exists
	data=execute_mysql_query("SELECT COUNT(*) FROM users WHERE `login` = '"+username+"'")[0]
	if data[0] != 0:
		error = "login taken pick different"
	else:
		# all good, add new user
		update_mysql_query("INSERT INTO `frontend`.`users` (login,password,user_data) values ('"+username+"','"+password+"',0)")
	return error

def check_user_credentials(login,password):
	"""
	Retrieves basic data for for user
	Parameters: 
		login - login name of user to get information
		password - password of user to authenticate 
	Returns:
		table containing basic inforation on user
		data[0] - uesr_id	-  unique id of user
		data[1] - user_data -  0 if user is ordinary user / 1 if user is admin
	"""
	data= execute_mysql_query("SELECT id,user_data FROM users WHERE login='" + login + "' AND password='" + password + "'")
	if data:
		return data[0]

def get_user_details(user_id):
	"""
	Retrieves from database values connected to user with specified user_id
	Parameters:
		user_id - Id of user to get inforation
	Returns:
		talbe containing inforation
		data[0] - id
		data[1] - login
		data[2] - user_data - 1 if user is admin
		data[3]	- location of picture / null for default picture
	"""
	data= execute_mysql_query("SELECT id,login,user_data, picture FROM users WHERE id='" +str(user_id) + "'")
	if data:
		return data[0]

def get_list_of_users(pattern):
	"""
	gets list of users statring with specified pattern. 
	If pattern is empty string All users are returned.
	parameters: 
		pattern - String containing begining of login to filter
	returns:
		list o id's of users whose login begins with pattern
	"""
	pattern=pattern+'%' 
	return execute_mysql_query("SELECT id FROM users WHERE login like '" + pattern + "'")

def set_mac_address(user_id,mac):
	"""
	 Assigns MAC address to user with specified user_id
	 If Mac is assigned to other user operation is not successfull
	 If Mac have not been used function adds new address.
	 if MAc is already in database function re-assigns it to specified user
	Parameters:
		user_id Id of user to assign Mac address
		mac Mac-address to be assigned. Format is not evaluated
	Returns: 
		error message.
	"""
	#check if already assigned
	error=None
	data =execute_mysql_query("SELECT count(*) FROM user_has_device JOIN mac ON (user_has_device.mac_id=mac.id) WHERE end_time IS NULL and mac = '"+mac+"'")
	print data
	if data and data[0][0]!=0:
		return "Mac taken"
	
	if mac != "":
		#if mac is not empty string
		data=execute_mysql_query("SELECT id FROM `frontend`.`mac` WHERE `mac`.`mac`='" +mac+"'")
		if not data:
			# put new address into db
			update_mysql_query("INSERT INTO `frontend`.`mac`( `mac`) VALUES ('" +mac+"')")

			# get id of new address
			data=execute_mysql_query("SELECT id FROM `frontend`.`mac` WHERE `mac`.`mac`='" +mac+"'")[0]
			if not data:
				return "problem with adding mac"
		else:
			data=data[0]
		# assign addres to user
	update_mysql_query("UPDATE user_has_device SET end_time=now() WHERE end_time IS NULL AND user_id="+str(user_id))
	if mac != "":
		update_mysql_query("insert into `frontend`.`user_has_device` (mac_id,user_id,start_time) values ('"+str(data[0])+"','"+str(user_id)+"', now() )")

	return 'all ok'


def get_mac_address(user_id):
	"""
	Reads Mac address assigned to user with given user_id
	Parameters:
		user_id User whose Mac has to be retrived
	Returns: 
		string containing address of user or empty string if Mac address not assigned
	"""
	#data =execute_mysql_query("SELECT mac FROM (`frontend`.`mac` JOIN `frontend`.`users` ON (`mac`.id=`users`.`MAC_id`)) WHERE `users`.`id`='" +str(user_id)+"'")
	
	data =execute_mysql_query("SELECT mac from user_has_device JOIN `users` ON (users.id=user_id) 	JOIN mac ON (user_has_device.mac_id=mac.id) WHERE end_time IS NULL AND `users`.`id`='" +str(user_id)+"'""")	
	if data:
		#print data
		mac=data[0][0]
	else:
		mac=""
	return mac

def get_mac_list_for_user(user_id):
	"""
	Reads Mac address assigned to user with given user_id
	Parameters:
		user_id User whose Mac has to be retrived
	Returns: 
		string containing address of user or empty string if Mac address not assigned
	"""
	#data =execute_mysql_query("SELECT mac FROM (`frontend`.`mac` JOIN `frontend`.`users` ON (`mac`.id=`users`.`MAC_id`)) WHERE `users`.`id`='" +str(user_id)+"'")
	res=[]
	data =execute_mysql_query("SELECT mac, start_time , end_time from user_has_device JOIN `users` ON (users.id=user_id) 	JOIN mac ON (user_has_device.mac_id=mac.id) WHERE `users`.`id`='" +str(user_id)+"' ORDER BY user_has_device.id DESC""")	
	if data:
		#print data
		res=data
	else:
		res=[]
	return res

def update_account_avatar(user_id,filename):
	"""
	Updates picture in database for specified user
	Parameters:
		user_id - Id of user to update picture
		filename - File name of picture
	 Returns:
		none
	"""
	update_mysql_query("UPDATE `frontend`.`users` SET picture = '"+filename+"' WHERE id='"+str(user_id)+"'")


def execute_mysql_query(query):
	"""
	Executes mysql query not requireing commit - SELECT
	Parameters:
		querry String containing query to execute
	Returns:
		Response data for query
	"""
	try:
		connection=mdb.connect(config.MYSQL_DATABASE_HOST,config.MYSQL_DATABASE_USER,config.MYSQL_DATABASE_PASSWORD,config.MYSQL_DATABASE_DB);
		with closing( connection.cursor() ) as cursor:
			cursor.execute(query)
			data = cursor.fetchall()
		connection.close()
		return data
	except Exception as e:
		logging.error(e)
		raise('Error accessing database')

def update_mysql_query(query):
	"""
	Ececutes query requiring commit - INSERT, UPDATE, DELETE
	Parameters:
		querry String containing query to execute
	Returns:
		none
	"""
	try:
		connection=mdb.connect(config.MYSQL_DATABASE_HOST,config.MYSQL_DATABASE_USER,config.MYSQL_DATABASE_PASSWORD,config.MYSQL_DATABASE_DB);
		with closing( connection.cursor() ) as cursor:
			cursor.execute(query)
		connection.commit() #required to apply result of insert operation to database
		connection.close() #release conneciton
	except Exception as e:
		logging.error(e)
		raise('Error accessing database')
