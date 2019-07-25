import configparser
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

#home_user variables
home_user = os.path.expanduser('~')

#Reading configfile.ini using configparser
config = configparser.ConfigParser()
config.read(home_user + '/reshma/rtc/configfile.ini')
#print(config.sections())

#Config_file variables
c_jazzRepoUrl= config.get('Default','jazzRepoUrl')
c_root_git_url= config.get('Default','root_git_url')
c_auth_api = config.get('Api','auth_api')
c_authentication_api = config.get('Api','authentication_api')
c_repo_reg_api = config.get('Api','repo_reg_api')
c_projectId = config.get('Rtc','projectId')
c_jazz_username = config.get('Rtc','jazz_username')
c_jazz_password = config.get('Rtc','jazz_password')

#argparse variables
app_code = args.app_code
component_code = args.component_code

code_url = c_root_git_url + args.app_code

ownerItemId = c_projectId
currentPAItemId = c_projectId

try:
	ses = requests.Session()
	req = ses.get(c_jazzRepoUrl + c_auth_api, verify=False)
	print(req)
	req.raise_for_status()
except requests.exceptions.HTTPError as err:
	print("Invalid request " , err)
	sys.exit()

try:
	data = {
	   'j_username': c_jazz_username ,
	   'j_password': c_jazz_password
	}
	req = ses.post(c_jazzRepoUrl + c_authentication_api, data=data, verify=False)
except KeyError:
	print("Authentication failed")
		
headers ={
		'Accept':'text/json'
	}
for comp in args.component_code:
	try:
		payload= {'name': app_code + '_' + comp ,'ownerItemId': ownerItemId, 'currentPAItemId': currentPAItemId, 'url': code_url + '/' + comp} 

		req = ses.post(c_jazzRepoUrl + c_repo_reg_api, params=payload, headers=headers)
		
		with open('/tmp/registerKey', "a") as myfile:
		   myfile.write(str(req.text))
	 
	except:
		print("Repo registration failed")
		
 
try:
	with open('/tmp/registerKey', 'r') as response_file:
		input = response_file.read()
	response_key = re.findall(r',"key":"([a-z0-9]*)"', input)
	print(response_key)
except:
	print("Key extraction failed")
	