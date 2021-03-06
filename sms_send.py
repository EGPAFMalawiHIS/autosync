#!/usr/bin/python3

import requests
import datetime
import sys
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import json
import logging
import socket
import time

import emr_api.exceptions as emr_exceptions
import emr_api.reports as emr_reports
import settings # enviroment variabless

#set timezone
os.environ['TZ'] = 'Africa/Blantyre'
time.tzset()

REPORTING_API_PROTOCOL = settings.REPORTING_API['protocol']
REPORTING_API_HOST = settings.REPORTING_API['host']
REPORTING_API_PORT = settings.REPORTING_API['port']

EMASTERCARD_URL = f"{REPORTING_API_PROTOCOL}://{REPORTING_API_HOST}:{REPORTING_API_PORT}/api/v1/reports/age-disaggregates"
SERVER = os.getenv("SERVER")
PORT = os.getenv("PORT")
ENCRYPTION_KEY = bytes(os.getenv("ENCRYPTION_KEY"), 'utf-8')

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

def getSite(filename):
	site = {'SITECODE':None,'SITENAME':None,'DISTRICT':None}
	with open(filename) as fp:
		line = fp.readline()
		cnt = 1
		while line:
			newline = line.split(':')
			if newline[0] == 'SITECODE':
				site['SITECODE'] = newline[1]
			elif newline[0] == 'SITENAME':
				site['SITENAME'] = newline[1]
			elif newline[0] == 'DISTRICT':
				site['DISTRICT'] = newline[1]
				break		
			
			line = fp.readline()
			cnt += 1
	return site

#Cummulative corhot aggregated report
def getQouta(code, start_date, end_date, report_name, site):
	
	'''
	PARAMS = [
	{'code':1,'type':'TXCurrent','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'defaulted1Month','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'defaulted2Months','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'defaulted3MonthsPlus','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'stopped','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'transferredOut','reportStartDate':None,'reportEndDate':str(year) + quota },
	{'code':1,'type':'totalRegistered','reportStartDate':None,'reportEndDate':str(year) + quota }

	]
	'''

	PARAMS = [
	{'code': code,'reportStartDate': start_date,'reportEndDate': end_date }
	]

	print(PARAMS)
	#sys.exit()
	data = [] 
	for param in PARAMS:
		try:  
			print(EMASTERCARD_URL)
			r = requests.get(url = EMASTERCARD_URL, params = param) 
			print('recieved data', r.text)
			data.append({'sitecode':site['SITECODE'],'sitename':site['SITENAME'],
						 'report_source': 'emastercard', 'report_name': report_name, 
						 'report_generated_time': datetime.datetime.now().strftime("%Y-%m:%d, %H:%M:%S"),
						 'reportdata':r.json()})
		except requests.exceptions.ConnectionError as e: 
			logging.exception(f'Failed to retrieve eMastercard report: {e}')

	print('report generated')
	return data


def sendData(data,server,port,site):
	
	EMASTERCARD_URL = 'http://'+ server + ':' + str(port) + '/sms'
	response = requests.post(EMASTERCARD_URL, data={'Body':data,'sitename':site['SITENAME'],'sitecode':site['SITECODE'],'district':site['DISTRICT']})
	if response.status_code == 200:
		return True
	else:
		return False

def getTrigger(site,server,port):
	EMASTERCARD_URL = 'http://'+server+':'+port+'/trigger_per_site'
	PARAMS = {'site':site}
	data = []
	try:  
		r = requests.get(url = EMASTERCARD_URL, params = PARAMS) 
		if r:

			data = r.json()
			#data = r

		

	except requests.exceptions.ConnectionError as e: 
		print(EMASTERCARD_URL+' Timeout')

	print('lets check data:',data)
	return data


def generateEncryptionKey():
	password_provided = "Charlio1." # This is input in the form of a string
	password = password_provided.encode() # Convert to type bytes
	salt = b'chachikulukuludi' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
	kdf = PBKDF2HMAC(
	    algorithm=hashes.SHA256(),
	    length=32,
	    salt=salt,
	    iterations=100000,
	    backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
	return key

def encrypt(data,key):
	message = data.encode()

	f = Fernet(key)
	encrypted = f.encrypt(message)
	return encrypted
def decrypt(data,key):
	f = Fernet(key)
	decrypted = f.decrypt(data)
	return decrypted

def checkInternetConnection(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def checkHost(ip, port,retry,delay):
	ipup = False
	for i in range(retry):
		if checkInternetConnection(ip, port):
			ipup = True
			break
		else:
			print('waiting for connection..')
			time.sleep(delay)
			print('retrying ....')
	return ipup

def getEmrHIVReports(site, quarter, year):
	'''Returns a list of the primary HIV reports from the EMR.'''
	def parse_report(report):
		try:
			return {
				'sitecode': site['SITECODE'],
				'sitename': site['SITENAME'],
				'report_generated_time': datetime.datetime.now().strftime(r'%Y-%m-%d %H:%M'),
				'report_name': report.name,
				'report_source': 'emr',
				'reportdata': report.get(settings.REPORTING_API, quarter, year)
			}
		except emr_exceptions.ApiError as e:
			print(f'Failed to retrieve report: {e}')
			return None

	reports = map(parse_report, emr_reports.reports())

	return tuple(filter(lambda report: report is not None, reports))

def getEMastercardReports(site, myquota, year):
	print('Retrieving Emastercard reports...')
	report_start_date, report_end_date = emr_reports.get_quarter_dates(myquota, year)
	cummulative_report_code = 1
	quarterly_report_code = 2
	return (
		getQouta(cummulative_report_code, None, report_end_date, 'Cummulative age disaggregates', site)
		+ getQouta(quarterly_report_code, report_start_date, report_end_date, 'Quarterly age disaggregates', site)
	)

def getReports(site, quarter, year):
	print(f'Retrieving reports for Q{quarter}-{year}...')
	reporting_api_type = settings.REPORTING_API['type'].lower()
	if reporting_api_type == 'emr':
		return getEmrHIVReports(site, quarter, year)
	elif reporting_api_type == 'emastercard':
		return getEMastercardReports(site, quarter, year)
	else:
		raise ValueError(f'Invalid REPORTING_API_TYPE in configuration, {reporting_api_type}')

def execute(site, year, myquota):
	reports = getReports(site, myquota, year)
	if not reports:
		logging.error('Retrieved empty report - data sending failed')
		return None

	encrypted_reports = encrypt(json.dumps(reports), ENCRYPTION_KEY)
	#print(Result)
	#print('KEY:',generateEncryptionKey())
	print(f'Encrypted reports: {encrypted_reports}')
	#print(decrypt(data_encrypted,key))

	#check internet connection to the server in HQ
	ip = SERVER
	port = str(PORT)
	retry = 5
	delay = 10
	if checkHost(ip, port,retry,delay):
		print('connection available')
		print('generating report...')

		response = sendData(encrypted_reports,ip,port,site)
		if response:
			print('data sent successfully')
		else:
			print('data sent Failed')
	else:
		print('connection not available')

flag = True
while flag == True:
	ip = SERVER
	port = str(PORT)
	retry = 5
	delay = 60 *30
	if checkHost(ip, port,retry,delay):
		print('connection available')
		site = getSite('site.txt')
		trigger = getTrigger(site['SITECODE'],ip,port)
		print('lets check ',trigger)
		if len(trigger) > 0:
			if trigger['response'] == 'Yes':
				print('about to')
				quarter = trigger['quota']
				year = trigger['year']

				if quarter and year:
					quarter = int(float(trigger['quota']))	# Unfortunately we may get floats here
					year = int(year)
					execute(site, year, quarter)
		else:
			print('No response to the server or Record Not found')

		print('to be executed next after 30 minutes ....')
		time.sleep(delay)

		
	else:
		print('connection not available')








