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
import socket
import time

import emr_api.reports as emr_reports
import settings # enviroment variabless

#set timezone
os.environ['TZ'] = 'Africa/Blantyre'
time.tzset()

URL = os.getenv("URL")
SERVER = os.getenv("SERVER")
PORT = os.getenv("PORT")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

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
def getQouta(code,reportStartDate,quota, year,site):
	
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
	{'code':1,'type':None,'reportStartDate':None,'reportEndDate':str(year) + quota }
	]

	print(PARAMS)
	#sys.exit()
	data = [] 
	for param in PARAMS:
		try:  
			r = requests.get(url = URL, params = param) 
			print('recieved data', r)
			data.append({'sitecode':site['SITECODE'],'sitename':site['SITENAME'],'report_generated_time':datetime.datetime.now().strftime("%Y-%m:%d, %H:%M:%S"),'reportdata':r.json()})
		except requests.exceptions.ConnectionError as e: 
			print('Timeout')

	print('report generated')
	return data


def sendData(data,server,port,site):
	
	URL = 'http://'+ server + ':' + str(port) + '/sms'
	response = requests.post(URL, data={'Body':data,'sitename':site['SITENAME'],'sitecode':site['SITECODE'],'district':site['DISTRICT']})
	if response.status_code == 200:
		return True
	else:
		return False

def getTrigger(site,server,port):
	URL = 'http://'+server+':'+port+'/trigger_per_site'
	PARAMS = {'site':site}
	data = []
	try:  
		r = requests.get(url = URL, params = PARAMS) 
		if r:

			data = r.json()
			#data = r

		

	except requests.exceptions.ConnectionError as e: 
		print(URL+' Timeout')

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
	parse_report = lambda report: {
		'sitecode': site['SITECODE'],
		'sitename': site['SITENAME'],
		'report_generated_time': datetime.datetime.now().strftime(r'%Y-%m-%d %H:%M'),
		'reportdata': report.get(settings.EMR_API, quarter, year)
	}

	return map(parse_report, emr_reports.reports())

def getEMastercardReports(site, myquota):
	now = datetime.datetime.now()
	code = 1
	reportStartDate = None
	if myquota == 1:
		quota = '-03-31'
		Result = getQouta(code,reportStartDate,quota,now.year,site)
	elif myquota == 2:
		quota = '-06-30'
		Result = getQouta(code,reportStartDate,quota,now.year,site)
	elif myquota == 3:
		quota = '-09-30'
		Result = getQouta(code,reportStartDate,quota,now.year,site)
	elif myquota == 4:
		quota = '-12-31'
		Result = getQouta(code,reportStartDate,quota,int(now.year) +1,site)

	return [Result]

def execute(myquota,site):
	key = bytes(ENCRYPTION_KEY, encoding='utf-8') # Key should be generated dynamically

	emr_reports = getEmrHIVReports(site, myquota, datetime.date.today())
	emastercard_reports = getEMastercardReports(site, myquota)
	reports = (*emr_reports, *emastercard_reports)

	encrypted_reports = [encrypt(json.dumps(report), key) for report in reports]
	#print(Result)
	#print('KEY:',generateEncryptionKey())
	print(f'Encrypted reports: {encrypted_reports}')
	#print(decrypt(data_encrypted,key))

	#check internet connection to the server in HQ
	ip = SERVER
	port = str(PORT)
	retry = 5
	delay = 10
	for report in encrypted_reports:
		if checkHost(ip, port,retry,delay):
			print('connection available')
			print('generating report...')

			response = sendData(report,ip,port,site)
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
				if trigger['quota']:
					myquota = float(trigger['quota'])
					execute(myquota,site)
		else:
			print('No response to the server or Record Not found')

		print('to be executed next after 30 minutes ....')
		time.sleep(delay)

		
	else:
		print('connection not available')








