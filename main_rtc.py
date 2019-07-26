import re
import requests
import requests.exceptions
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import argparse
import ConfigParser
import sys
from requests.exceptions import ConnectionError

#Reading the values from the config file
config = ConfigParser.ConfigParser()
config.read('/home/ubuntu/arya/git/rtc.ini')
c_jazzRepoUrl = config.get('Default', 'jazzRepoUrl')
c_api1 = config.get('Api', 'api1')
c_api2 = config.get('Api', 'api2')
c_api3 = config.get('Api', 'api3')
c_url = config.get('Default', 'root_url')
c_user = config.get('Credentials', 'username')
c_password = config.get('Credentials', 'password')
c_projectId  = config.get('Default', 'projectId')

#To get Application code and Component code from Command Line
parser = argparse.ArgumentParser()
parser.add_argument('-App_code', action="store", dest="App_code",type=str)
parser.add_argument('-Comp_code', action='append', dest='comp_code',default=[],help='Add repeated values to a list')
results = parser.parse_args()


RTC_git_name = results.App_code
git_url = c_url + results.App_code 

#Create a session
ses = requests.Session()

#Authenticating the RTC Repo URL
try:
	req = ses.get(c_jazzRepoUrl + c_api1 ,verify=False)
	req.raise_for_status()

except requests.exceptions.RequestException as e:
	print('Invalid URL',e)
	sys.exit() 			
	
try:	
	data = {
	  'j_username': c_user,
	  'j_password': c_password
	}
	req = ses.post(c_jazzRepoUrl + c_api2, data=data, verify=False)
	
except KeyError:
	print("Authentication error...!!!")
	
#Registering the Git Repositories and writing the response to /tmp/registerOut
try:
	headers ={
		'Accept':'text/json'
	}
	for i in results.comp_code:
	
		name = RTC_git_name+'_'+i
		url = git_url+'/'+i
		
		payload= {'name': name ,'ownerItemId': c_projectId,'currentPAItemId': c_projectId, 'url': url}
		req=ses.post(c_jazzRepoUrl + c_api3 ,params=payload, headers=headers)
		
		with open("/tmp/registerOut", "a+") as file:
			file.write(req.text)
	
except requests.exceptions.HTTPError as e:
	print("Git Repository not registered...!!!")
	sys.exit() 

#Generating the key of the registered repositories
try:	
	with open('/tmp/registerOut','r+') as content_file:
		input = content_file.read()
	matches = re.findall(r',"key":"([a-z0-9]*)"', input)
	matches[0]
	print(matches)
except IndexError:
	print('Authentication Failed')
	



