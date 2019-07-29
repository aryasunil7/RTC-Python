import configparser
from configparser import ConfigParser, NoOptionError, NoSectionError 

import argparse
import re
import sys
import os

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Taking application code and component code through command line using argparser
parser = argparse.ArgumentParser()
parser.add_argument('-app_code', action='store', dest='app_code', type=str)
parser.add_argument('-component_code', action='append', dest='component_code', default=[], type=str)
args = parser.parse_args()
#print(args.component_code)

#argparse variables
app_code = args.app_code
component_code = args.component_code

#Reading configfile.ini using configparser
config = configparser.ConfigParser()
config.read('rtc.ini')
#print(config.sections())

#Config_file variables
try:
	c_jazzRepoUrl= config.get('Default','jazzRepoUrl')
	c_git_url= config.get('Default','git_url')
	c_api_endpoint1 = config.get('API','api_endpoint1')
	c_api_endpoint2 = config.get('API','api_endpoint2')
	c_api_endpoint3 = config.get('API','api_endpoint3')
	c_projectId = config.get('Default','projectId')
	c_username = config.get('User','username')
	c_password = config.get('User','password')
except NoOptionError as err:
	sys.exit(str(err) + "It should be provided") 

	
if not (c_jazzRepoUrl and c_git_url and c_api_endpoint1 and c_api_endpoint2 and c_api_endpoint3 and c_projectId and c_username and c_password):
	sys.exit("Error: Check the values in the config_file")


code_url = c_git_url + args.app_code

ownerItemId = c_projectId
currentPAItemId = c_projectId

#Checking RTC url status
try:
	ses = requests.Session()
	res = ses.get(c_jazzRepoUrl + c_api_endpoint1, verify=False)
	#print(res)
	res.raise_for_status()
except requests.exceptions.RequestException as err: 
	sys.exit("Something went wrong in c_jazzRepoUrl.. Please check " + str(err))

#Authentication
try:
	data = {
	   'j_username': c_username ,
	   'j_password': c_password
	}
	res = ses.post(c_jazzRepoUrl + c_api_endpoint2, data=data, verify=False)
	res.raise_for_status()
	
except (requests.exceptions.RequestException,requests.HTTPError,requests.exceptions.ConnectionError) as err:
	sys.exit("Something went wrong in api, Please check again" + str(err))

#Repo Registration	
headers ={
		'Accept':'text/json'
	}
	
comp_key={comp: '' for comp in args.component_code}
for comp in args.component_code:
	try:
		payload= {'name': app_code + '_' + comp ,'ownerItemId': ownerItemId, 'currentPAItemId': currentPAItemId, 'url': code_url + '/' + comp} 

		res = ses.post(c_jazzRepoUrl + c_api_endpoint3, params=payload, headers=headers)
		res.raise_for_status()
		
	except requests.exceptions.HTTPError as err:
		print("Repo registration failed for " + app_code + "_" + comp + str(err))
		
		
    #Key Extraction
	try:
		registerKey = str(res.text)
		response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)
		#print(res.json()['soapenv:Body']['response']['returnValue']['value']['key'])
		comp_key[comp] = response_key[0]
		
	except IndexError:
		print("Authentication and Key extraction failed for " + app_code + "_" + comp)

print(comp_key)
