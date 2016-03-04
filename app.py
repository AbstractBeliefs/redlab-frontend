from flask import Flask
from flaskext.mysql import MySQL
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash


import MySQLdb 			#escape_string()
import re				#re.match()
import datetime			#calculate time periods

#upload file
import os
#from werkzeug import secure_filename #file is stored in changed name.
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

app=Flask(__name__)
app.config.from_object(__name__)

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

# TODO
# To load from separate file use. FRONTENT_SETINGS should be then env-setting 
# with assigned filename of settings.
# Settins are stored in sectet.txt.
#app.config.from_envvar('FRONTENT_SETINGS',silent=true)

# TODO 
# Validation of data to make sure that sql injecton can't be done.
# Need to be consulted with Brian
mysql=MySQL()
mysql.init_app(app)

def allowed_file(filename):
	#check if filename has allowed extension
	return '.'in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENTIONS




session = dict()

@app.route('/')
@app.route('/index')
def index():
	session['active_nav']='Home'
	# main entry for webpage.
	return render_template('index.html',session=session)

 

@app.route('/emulator', methods=['GET', 'POST'])
def api_emul():
	# emulation of ap-server behaviour 
	# displays form to select registered beacon device and Mac in ordet to emulate
	# VisibilityEvent. Only for test purpse. Should be removed from final solution
	if request.method=='POST':
		#if button pressed insert into database selected VisibilityEvent
		beacon=MySQLdb.escape_string(request.form['beacon'])
		mac=MySQLdb.escape_string(request.form['mac'])
		ev_type=MySQLdb.escape_string(request.form['event'])
		con=mysql.connect()
		cursor1=con.cursor()	
		cursor1.execute(" INSERT INTO `Api-server`.`VisibilityEvent` (event_time,beacon,mac,event_type) VALUES (now(),'"+beacon+"','"+mac+"','"+ev_type+"')")
		con.commit()
	macs=[]
	beacons=[]
	#read all macs registered in db
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT id,MAC FROM `Api-server`.`MAC`")
	data = cursor.fetchall()
	for row in data:
		macs.append([row[0],row[1]])
	# read all beacons registered in db
	cursor.execute("SELECT serial,comment FROM `Api-server`.`Beacons`")
	data = cursor.fetchall()
	for row in data:
		beacons.append([row[0],row[1]])
	cursor.close()
	# display form
	return render_template('api_emul.html',beacons=beacons,macs=macs)


@app.route('/wip',methods=['GET', 'POST'])
def wip():
	session['active_nav']='Home'
	#displays work in proggres page 
	return render_template('wip.html',session=session)
	
@app.route('/register',methods=['GET', 'POST'])
def register():
	session['active_nav']='Register'
	# displays form to capture user input for registration
	# validates user input 
	# register new user using data accuired from form
	# logis in user if registration successfull
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
			#valid userename and password
			con=mysql.connect()
			cursor = con.cursor() 
			# check if user of specified login allready exists
			cursor.execute("SELECT COUNT(*) FROM users WHERE `login` = '"+username+"'")
			data = cursor.fetchone()
			if data[0] != 0:
				# 
				error = "login taken pick different"
			else:
				# all good, add new user
				cursor.execute("INSERT INTO `frontend`.`users` (login,password,user_data) values ('"+username+"','"+password+"',0)")
				con.commit() #required to apply result of insert operation to database
				cursor.close() #release conneciton
				if login_user(username,password):
					return redirect(url_for('index',session=session))
			cursor.close()
	return render_template('register.html',error=error)

##################################################
@app.route('/userdetails',methods=['GET'])
def userdetails():
	user_id=MySQLdb.escape_string(request.args['user_id'])
	return redirect(url_for('profile',user_id=user_id,))
	

@app.route('/users',methods=['GET', 'POST'])
def users():
	session['active_nav']='Users'
	# shows list of all users 
	# shoudl display last login time
	# clicking on users avatar shoudl open window with user details
	# should add nav tab with user's login 
	# optioon ony for admins
	if not is_admin():
		return render_template('index.html')
	if 'picture' in request.form:
		selected_user= request.form['picture']
		content=show_content(selected_user,True)
		session['active_nav']=content['user_login']
		if not content['user_login'] in session['nav']:
			session['nav'][content['user_login']]=url_for('userdetails',user_id=content['user_id'])
		return redirect(url_for('userdetails',user_id=content['user_id'],))
	
	#get list of users
	pattern="" #empty pattern
	if request.method=='POST':#get pattern from user input if set
		if request.form['username']:
			pattern=MySQLdb.escape_string(request.form['username'])
		
	#append wildcard to pattern in order to find users starting with pattern
	pattern=pattern+'%' 
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT id FROM users WHERE login like '" + pattern + "'")
	data= cursor.fetchall()
	user_list=[]
	for row in data:
		#get basic infrmation about each user from lsit of results
		content=show_content(row[0],False)
		user_list.append(content)
	return render_template('users.html',session=session,user_list=user_list)

@app.route('/profile',methods=['GET' ,'POST'])
def profile():
	#session['active_nav']='Profile'
	#shows profile for user with specified id passed as get data
	#if user_id is different than stored in session, only admin can profile
	#user sees only basic information - last seen event
	#admin sees list of visibility events
	#when device not set for this user message should be displayed.
	pass
	user_id=MySQLdb.escape_string(request.args['user_id'])
	if user_id != str(session['logged_in']):
		if not is_admin():
			# access denied
			return render_template('wip.html',error="Sorry??")
		#profile=False
	else:
		profile=True
		#if user is on "me"page can change his avatar picture
		if request.method == 'POST':
			if 'mac' in request.form:
				mac = request.form['mac']
				if not mac == get_mac_address(user_id):
					if(re.match("^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$",mac)):
						print set_mac_address(user_id,mac)
			if 'file' in request.files:
				file = request.files['file']
				if file and allowed_file(file.filename):
					#	save file as 'avatar(user_id)_.ext' so every user has 1 profile foto
					#	no check on size is done!!
					#	No check on pic dimensions is done!!
					#	file can be uploaded only once. can not be deleted

					#filename = secure_filename(file.filename)
					filename='avatar'+str(user_id)+'_.'+file.filename.rsplit('.',1)[1]
					#if os.path.isfile((os.path.join(app.config['UPLOAD_FOLDER'],filename))):
					#	 print os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
					#else:
					#	print("Sorry, I can not remove %s file." % (os.path.join(app.config['UPLOAD_FOLDER']+filename)))
						
					file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
					update_account_avatar(user_id,filename)
					return redirect(url_for('profile',user_id=user_id))
	content=show_content(user_id,is_admin())
	return render_template('profile.html',session=session,content=content,profile=True)
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	# Displays form to capture user input for username and password
	# validates user input 
	# if entered data is valid logs in by setting session values
	session['active_nav']='Log in'
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
			session['active_nav']='Profile'
			if login_user(username, pasword):

				return redirect(url_for('profile',user_id=session['logged_in']))
			
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	# logs out user by clearing session values.
	session.clear()
	flash('You were logged out')
	session['active_nav']='Home'
	return redirect(url_for('index'))


def login_user(login, password):
	# checks if user with login and password is in database 
	# sets session values with data from database
	# returs true if login sucessfull, false otherwise
	result=False # login result
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT id,user_data FROM users WHERE login='" + login + "' AND password='" + password + "'")
	data = cursor.fetchone()
	if data is None:
		#login uncucessfull
		pass
	else:
		session_start()
		session['logged_in']=data[0]
		session['is_admin']=data[1]
		result=True
	cursor.close() #release database conneciton 
	return result

def is_admin():
	# checks if logged user is admin
	# possible need for revoking rights while logged in  
	if session:
		return session['is_admin']==1
	else: 
		return False

def show_content(user_id,full):
	#create content to fill profile 
	#parameters:
	#	user_id - subject of profile check
	#	full	- level of detail. =false for basic information and last check-in
	#return 
	#	dict with content to be displayed
	content=dict()
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT id,login,user_data, picture FROM users WHERE id='" +str(user_id) + "'")
	data = cursor.fetchone()
	#print user_id
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
			
			
		cursor.execute("SELECT register_time FROM check_in_events WHERE user_id='" +str(user_id) + "' ORDER BY register_time DESC")
		data = cursor.fetchall()
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
	cursor.close()
	return content

def session_start():
	#stard new session
	session['nav']=dict()
	
def merge_sequence(seq,interval):
	# Function finds subsets of coherent values in sequence,
	# which are distant no more than specified interval.
	# Sequence must be sorted in decending order
	#parametres:
	#	seq List containing Sequence of numbers
	#	interval Maximal distance betweeen values to be considered as coherent
	#return:
	#	list of value compartments merged according to interval value
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

def set_mac_address(user_id,mac):
	# Assigns MAC address to user with specified user_id
	# If Mac is assigned to other user operation is not successfull
	# If Mac have not been used function adds new address.
	# if MAc is already in database function re-assigns it to specified user
	# parameters:
	#	user_id Id of user to assign Mac address
	#	mac Mac-address to be assigned. Format is not evaluated
	# return: 
	#	error message.
	con=mysql.connect()
	cursor = con.cursor() 
	#check if already assigned
	cursor.execute("SELECT MAC FROM (`Api-server`.`MAC` JOIN `frontend`.`users` ON (`MAC`.id=`users`.`MAC_id`)) WHERE `MAC`.`MAC`='" +mac+"'")
	data=cursor.fetchone()
	if data:
		return "Mac taken"
	cursor.execute("SELECT id FROM `Api-server`.`MAC` WHERE `MAC`.`MAC`='" +mac+"'")
	data=cursor.fetchone()
	if not data:
		# put new address into db
		cursor.execute("INSERT INTO `Api-server`.`MAC`( `MAC`) VALUES ('" +mac+"')")
		con.commit()
		# get id of new address
		cursor.execute("SELECT id FROM `Api-server`.`MAC` WHERE `MAC`.`MAC`='" +mac+"'")
		data=cursor.fetchone()
		if not data:
			return "problem with adding mac"
	# assign addres to user
	cursor.execute ("UPDATE `frontend`.`users` SET `MAC_id`='"+str(data[0])+"' WHERE `id`='"+str(user_id)+"'")
	con.commit()
	return 'all ok'


def get_mac_address(user_id):
	# reads Mac address assigned to user with given user_id
	# parameters:
	#	user_id User whose Mac has to be retrived
	# returns: 
	#	string containg address of user or empty string if Mac address not assigned
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT MAC FROM (`Api-server`.`MAC` JOIN `frontend`.`users` ON (`MAC`.id=`users`.`MAC_id`)) WHERE `users`.`id`='" +str(user_id)+"'")
	data=cursor.fetchone()
	cursor.close()
	if data:
		mac=data[0]
	else:
		mac=""
	return mac


def update_account_avatar(user_id,filename):
	#updates picture in database for specified user
	con=mysql.connect()
	cursor = con.cursor() 
	cursor.execute("UPDATE `frontend`.`users` SET picture = '"+filename+"' WHERE id='"+str(user_id)+"'")
	con.commit() #required to apply result of insert operation to database
	cursor.close() #release conneciton

if __name__=="__main__":
	app.run()
