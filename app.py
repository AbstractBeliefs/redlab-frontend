"""
Implementation of fronted for Checkin-Beacon project
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
from flask import Flask

from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask import session
#from flask.ext.session import Session


from restful import get_visibility_for_mac
from restful import get_beacon_devices,add_beacon_device,remove_beacon_device,set_beacon_device
from db_functions import check_user_credentials,get_user_details
from db_functions import get_mac_address,set_mac_address,get_mac_list_for_user
from db_functions import get_list_of_users,add_new_user
from db_functions import update_account_avatar





import MySQLdb 			#escape_string()


import re				#re.match()
import datetime			#calculate time periods

#upload file
import os				#disk operations for saving avatar file
#from werkzeug import secure_filename #file is stored in changed name.
import config

app=Flask(__name__)
app.config.from_object(config)

CHECK_IN_INTERVAL= datetime.timedelta(minutes=10)

# TODO
# To load from separate file use. FRONTENT_SETINGS should be then env-setting 
# with assigned filename of settings.
# Settins are stored in sectet.txt.
#app.config.from_envvar('FRONTENT_SETINGS',silent=true)

# TODO 
# Validation of data to make sure that sql injecton can't be done.
# Need to be consulted with Brian



def allowed_file(filename):
	"""
	check if filename has allowed extension
	parameters:
		filename - string containing name of file to check
	returns: 
	 	True if filename is allowed, False otherwise
	"""
	return '.'in filename and filename.rsplit('.',1)[1] in config.ALLOWED_EXTENTIONS





@app.route('/')
@app.route('/index')
def index():
	# main entry for webpage.
	return render_template('index.html',session=session)




@app.route('/emulator', methods=['GET', 'POST'])
def api_emul():
	from db_functions import execute_mysql_query,update_mysql_query
	# emulation of ap-server behaviour 
	# displays form to select registered beacon device and Mac in ordet to emulate
	# VisibilityEvent. Only for test purpse. Should be removed from final solution
	if request.method=='POST':
		#if button pressed insert into database selected VisibilityEvent
		beacon=MySQLdb.escape_string(request.form['beacon'])
		mac=MySQLdb.escape_string(request.form['mac'])
		update_mysql_query(" INSERT INTO `checkinapi`.`visibilityevents` (event_time,beacon,mac) VALUES (now(),'"+beacon+"','"+mac+"')")
	macs=[]
	beacons=[]
	#read all macs registered in db
	data=execute_mysql_query("SELECT id,mac FROM `frontend`.`mac`")
	for row in data:
		macs.append([row[1],row[1]])
	# read all beacons registered in db
	data=execute_mysql_query("SELECT serial,comment FROM `checkinapi`.`beacons`")
	for row in data:
		beacons.append([row[0],row[1]])
	# display form
	return render_template('api_emul.html',beacons=beacons,macs=macs)


@app.route('/wip',methods=['GET', 'POST'])
def wip():
	#displays work in proggres page 
	return render_template('wip.html',session=session)
	
@app.route('/register',methods=['GET', 'POST'])
def register():
	"""
	displays form to capture user input for registration
	validates user input 
	register new user using data accuired from form
	logis in user if registration successfull
	"""
	error = None
	if request.method == 'POST':
		# escape username and password user input, to use with database
		username=MySQLdb.escape_string(request.form['username'])
		password=MySQLdb.escape_string(request.form['password']) 
		password1=MySQLdb.escape_string(request.form['password1']) 
		#define regex pattern for login and password
		req_user='^[a-zA-Z][a-zA-Z0-9_]{1,20}$'
		req_pass='(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{5,}'# minimal 5 chars and 1 digit
		if not re.match(req_user,username): # check if username conforms to specified pattern
			error = 'Login should start with letter and be followed by letters digits or _ sign'
		elif not re.match(req_pass,password): # check if password matches regex pattern
			error = 'Password should be at least 5 characters long and must contain 1 digit and 1 letter'
		elif password1 != password:
			error = "Passwords do not match"
		else:
			error=add_new_user(username,password)
			if login_user(username,password):
				return redirect(url_for('index',session=session))
	return render_template('register.html',error=error)



##################################################
@app.route("/edit",methods=['GET','POST'])
def edit():
	try:
		if 'logged_in' not in session:
		# if not logged in go to login screen		
			flash('You are not logged in')
			return redirect(url_for('login'))
		#get user_id from get 
		user_id=MySQLdb.escape_string(request.args['user_id'])
		if user_id != str(session['logged_in']):
			if not is_admin():
				# access denied
				return render_template('wip.html',error="Sorry??")
			# to set active class in nav to #uer_login
			navpil=show_content(user_id,False)['user_login']
		else:
			navpil=None
			profile=True
			error=None
			#if user is on "me"page can change his avatar picture
			if request.method == 'POST':
				if 'mac' in request.form:
					#check if mac address has been changed
					mac = request.form['mac'].upper()
					#check if new mac address proper mac address or empty string
					if(re.match("^$|^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$",mac)):
						#check if new mac is the same as in database
						if not mac == get_mac_address(user_id):
							#change mac address.
							error = set_mac_address(user_id,mac)
					else:
						error ="New mac address is not valid"
				if 'file' in request.files:
					file = request.files['file']
					if file and allowed_file(file.filename):
						#	save file as 'avatar(user_id)_.ext' so every user has 1 profile foto
						#	no check on size is done!!
						#	No check on pic dimensions is done!!
						#filename = secure_filename(file.filename)
						filename='avatar'+str(user_id)+'_.'+file.filename.rsplit('.',1)[1]
						file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
						update_account_avatar(user_id,filename)
						return redirect(url_for('edit',user_id=user_id))
				if error: 
					flash(error)
			content=show_content(user_id,True)
		return render_template('profile.html',session=session,content=content,profile=True)
	except Exception as e:
		return render_template('wip.html', error=e)

@app.route('/userdetails',methods=['GET'])
def userdetails():
	#redirect to profile for specified user
	user_id=MySQLdb.escape_string(request.args['user_id'])
	return redirect(url_for('profile',user_id=user_id))
	
@app.route('/options',methods=['GET','POST'])	
def options():
	"""
	Display list of active beacons and generate buttons to add, edit, delete 
	"""
	try:
		if(is_admin()):
			# this is only avaliable for admin
			if request.method=='POST':
				if 'Update' in request.form:
					device_id=MySQLdb.escape_string(request.form['Update'])
					if unicode(device_id).isnumeric():
						comment=MySQLdb.escape_string(request.form['comment'])
						error = set_beacon_device(device_id,comment)
					else :
						error= '<Update> Error processing beacon serial'
					
				if "Add" in request.form:
					device_id=(MySQLdb.escape_string(request.form['serial']))
					
					if unicode(device_id).isnumeric():
						comment=comment=MySQLdb.escape_string(request.form['comment'])
						error=add_beacon_device(device_id,comment)
					else:
						error='<Add> Beacon serial has to be greater than 0'
				if 'Delete' in request.form:
					device_id=MySQLdb.escape_string(request.form['Delete'])
					if unicode(device_id).isnumeric():	
						error=remove_beacon_device(device_id)
					else:
						error= '<Delete> Error processing beacon serial'
				if error!= 'ok':
					flash(error)
			beacons=get_beacon_devices() # restful request for devices
			return render_template('device_options.html',session=session,beacons=beacons)
		else:
			return render_template('wip.html',error="Unauthorised.")
	except Exception as e:
		return render_template('wip.html', error=e)
	
@app.route('/users',methods=['GET', 'POST'])
def users():
	"""
	shows list of all users 
	shoudl display last login time
	clicking on users avatar shoudl open window with user details
	should add nav tab with user's login 
	optioon ony for admins
	"""
	try:
		if not is_admin():
			return render_template('index.html')
		if 'picture' in request.form:
			# pressed on button with user picture
			selected_user= request.form['picture']
			#get information on selected user from database
			content=show_content(selected_user,True)
			if not content['user_login'] in session['nav']:
				#if nav for this user does not exist, add it to nav list
				session['nav'][content['user_login']]=url_for('userdetails',user_id=content['user_id'])
			return redirect(url_for('userdetails',user_id=content['user_id'],))
		
		#get list of users
		pattern="" #empty pattern
		if request.method=='POST':#get pattern from user input if set
			if request.form['username']:
				pattern=MySQLdb.escape_string(request.form['username'])
			
		#append wildcard to pattern in order to find users starting with pattern
		user_list=[]
		data=get_list_of_users(pattern)
		for row in data:
			#get basic infrmation about each user from lsit of results
			content=show_content(row[0],False)
			user_list.append(content)
		return render_template('users.html',session=session,user_list=user_list)
	except Exception as e:
		return render_template('wip.html', error=e)
@app.route('/profile',methods=['GET' ])
def profile():
	"""
	shows profile for user with specified id passed as get data
	if user_id is different than stored in session, only admin can profile
	user sees only basic information - last seen event
	admin sees list of visibility events
	when device not set for this user message should be displayed.
	"""
	try:
		if 'logged_in' not in session:
		# if not logged in go to login screen		
			flash('You are not logged in')
			return redirect(url_for('login'))
		#get user_id from get 
		user_id=MySQLdb.escape_string(request.args['user_id'])
		if user_id != str(session['logged_in']):
			if not is_admin():
				# access denied
				return render_template('wip.html',error="Sorry??")
			# to set active class in nav to #uer_login
			navpil=show_content(user_id,False)['user_login']
		else:
			navpil=None
			profile=True
		content=show_content(user_id,True)
		return render_template('profile.html',session=session,content=content,profile=True,navpil=navpil)
	except Exception as e:
			return render_template('wip.html', error=e)

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	Displays form to capture user input for username and password
	validates user input 
	if entered data is valid logs in by setting session values
	"""
	try:
		error = None
		if request.method == 'POST':		
			if request.form['username']=="":
				error = 'Invalid username'
			elif request.form['password'] == "":
				error = 'Invalid password'
			else:
				#TODO validation of data to make sure that sql injecton can't be done
				#need to be consulted with Brian
				username=MySQLdb.escape_string(request.form['username'])
				pasword=MySQLdb.escape_string(request.form['password'])
				if login_user(username, pasword):

					return redirect(url_for('profile',user_id=session['logged_in']))
				
		return render_template('login.html', error=error)
	except Exception as e:
		return render_template('wip.html', error=e)

@app.route('/logout')
def logout():
	# logs out user by clearing session values.
	session.clear()
	flash('You were logged out')
	return redirect(url_for('index'))


def session_start():
	"""
		starts new session
		resets global variable session.
		clears additional nav tabs.
	"""
	session.clear()
	session['nav']=dict()
	

def login_user(login, password):
	"""
	TODO change plain text password to MD5 hash
	checks if user with login and password is in database 
	sets session values with data from database
	parameters:
		login - Login to check
		password - password of user
	returs 
		true if login sucessfull, false otherwise
	"""
	result=False # login result
	data=check_user_credentials(login,password)
	if data is None:
		#login uncucessfull
		pass
	else:
		session_start()
		session['logged_in']=data[0]
		session['is_admin']=data[1]
		result=True
	return result

def is_admin():
	"""
	checks if logged user is admin
	possible need for revoking rights while logged in  
	returns: 
		true if user is admin, false otherwise
	"""
	if session:
		return session['is_admin']==1
	else: 
		return False

def show_content(user_id,full):
	"""
	create content to fill profile 
	parameters:
		user_id - subject of profile check
		full	- level of detail. =false for basic information and last check-in
	return 
		dict with content to be displayed
	"""
	content=dict()
	data = get_user_details(user_id)
	if data:
		content['user_id']=data[0]
		content['user_login']=data[1]
		content['mac']=get_mac_address(user_id)
		if data[3]:
			content['profil_pic']=url_for('static',filename='uploads/'+data[3])
		else:
			content['profil_pic']= url_for('static',filename='img/default_user.jpg')
		if full:
			content['is_admin']=data[2]
	
		data=get_check_in_events(user_id)
		if len(data)>0:
			content['last_seen']=data[0][0] #last check-in
			#check if user is on line now
			if content['last_seen']+CHECK_IN_INTERVAL>datetime.datetime.now():
				content['last_seen']="On-Line now."	
			if full:
				#calculate login time periods
				seq=[]
				for row in data:
					seq.append(row[0])
				#merge coherent events as login time intervals
				history=merge_sequence(seq,CHECK_IN_INTERVAL)
				content['history']=history
		else:
			content['last_seen']="Not seen."
	return content


def merge_sequence(seq,interval):
	"""
	Function finds subsets of coherent values in sequence,
	which are distant no more than specified interval.
	Sequence must be sorted in decending order
	parametres:
		seq List containing Sequence of numbers
		interval Maximal distance betweeen values to be considered as coherent
	Returns:
		list of value compartments merged according to interval value
	"""
	result=[]
	if len(seq):
		prev=seq[0]
		hi=0
		lo=0
		for p in seq:
			if p+interval<prev:
				prev=p
				result.append([seq[lo-1],seq[hi]])
				hi=lo
			else:
				prev=p
			lo+=1
		result.append([seq[lo-1],seq[hi]])
	return result

def get_check_in_events(user_id,limit=None):
	"""
	Retrieves data for checking events for specified user
	Parameters: 
		user_id - Id of user to get inforation
		limit	- number of check_in events to register
	Returns:
		table containing checking events ordeterd desending by time of occurence
	"""
	#data =execute_mysql_query("SELECT register_time FROM check_in_events WHERE user_id='" +str(user_id) + "' ORDER BY register_time DESC")
	maclist=[]
	data=[]
	maclist=get_mac_list_for_user(user_id)
	#maclist.append(get_mac_address(user_id))
	for mac,start_time,end_time in maclist:
		data+=(get_visibility_for_mac(mac,start_time,end_time))
	return data





if __name__=="__main__":
	app.run()
	
