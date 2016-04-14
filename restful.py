"""
Module for restful service requests

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

import config
from requests import put,get,post,delete	# restful requests
import datetime			#calculate time periods

import logging




API_URL=config.API_URL +':'+str(config.API_PORT)

def get_visibility_for_mac(mac,starting_date=None,ending_date=None,limit=None):
	"""
	Gets all visibility events for specified mac within specified time period
	parameters:
		mac - string containing mac address to check
		limit - number of evets of interest
		starting_date - datetime containing begining of interval
		ending_date - datetime containing end of interval
	Returns:
		List of [date,beacon] tuples when check-in event occured sorted in descending order
	"""
	res=[]
	if mac:
		#k=(execute_mysql_query('select now() from dual'))[0][0]
		#starting_date=k-datetime.timedelta(hours=10) 
		#ending_date=k
		#limit=1
		request_string = API_URL+'/mac/'+mac	
		if starting_date:
			request_string+='/'+starting_date.strftime('%s')
			if ending_date:
				request_string+='/'+ending_date.strftime('%s')
		if limit:
			request_string+='?limit='+str(limit)
		try:
			contents= get(request_string).json()
			#print contents
			if 'status' in contents and contents['status']=='ok':
				for event in contents['eventlist']:
					#if event['mac']==mac:
						#d=datetime(datetime.strptime(event['event_time'][5:-4],'%d %b %Y %H:%M:%S'))
						d=datetime.datetime.fromtimestamp(event['event_time'])
						#res.append( d)
						res.append((d,event['beacon']) )
		except Exception as e:
			logging.error(e)
			raise Exception('Error sending data to API-server')
	return res
def get_beacon_devices():
	"""
	Request for devices using restful request
	parameters:
		none
	returns 
		list of all active devices in form of dict values containing device_serial and device_comment
	"""
	res=[]
	request_string = API_URL+'/beacon'
	#logging.info('logging: '+ request_string)
	try:
		contents= get(request_string).json()
		if 'status' in contents and contents['status']=='ok':
			res=contents['beacons']
	except Exception as e:
		logging.error(e)
		raise Exception ('Error sending data to API-server')
	return res
def set_beacon_device(device_id,comment):
	"""
	Request to set comment in device with specifed serial 
	parameters:
		device_id 	- serial of beacon device to update
		comment 	- new comment to be stored for device
	returns 
		status of operation 'ok' if successfull
	"""
	request_string = API_URL+'/beacon/'+str(device_id)
	try:
		contents= put(request_string, data={'comment':comment}).json()
	except Exception as e:
		logging.error(e)
		raise Exception('Error sending data to API-server')
	return contents['status']

def add_beacon_device(device_id,comment):
	"""
	Request to add new device with specifed serial 
	parameters:
		device_id 	- serial of beacon device be added
		comment 	- comment to be stored for device
	returns 
		status of operation 'ok' if successfull
	"""
	request_string = API_URL+'/beacon/'+str(device_id)
	try:
		contents= post(request_string, data={'comment':comment}).json()
	except Exception as e:
		logging.error(e)
		raise Exception('Error sending data to API-server')
	return contents['status']
def remove_beacon_device(device_id):
	"""
	Request remove device with specifed serial 
	parameters:
		device_id 	- serial of beacon device to remove
	returns 
		status of operation 'ok' if successfull
	"""
	request_string = API_URL+'/beacon/'+str(device_id)
	try:
		contents= delete(request_string).json()
	except Exception as e:
		logging.error(e)
		raise('Error sending data to API-server')
	return contents['status']

