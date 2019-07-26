import re
import requests
import configparser
import argparse, sys
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.exceptions import ConnectionError

#Importing all the configuration details from rtc_config.ini using configparser
config = configparser.ConfigParser()
config.read('/home/ubuntu/Soorya/rtc_config.ini')
c_jazzRepoUrl=config['Default']['jazzRepoUrl']
c_git_url=config['Default']['git_url']
c_projectId=config['Default']['projectId']
c_api_endpoint1=config['API']['api_endpoint1']
c_api_endpoint2=config['API']['api_endpoint2']
c_api_endpoint3=config['API']['api_endpoint3']
c_username=config['User']['username']
c_password=config['User']['password']

#Using argparse for app_code comp_code to parse there values through commandline
parser = argparse.ArgumentParser()
parser.add_argument('-app_code', dest='app_code', action="store", type=str)
parser.add_argument('-comp_code', action='append', dest='comp_code',default=[])
results =  parser.parse_args()
print("App Code=    ",results.app_code)
print("Comp Code=    ",results.comp_code)
 
 
rtc_git_name = 'Git_'+results.app_code
url=c_git_url + results.app_code
print(url)


#Checking whether the RTC url is accessible

ses = requests.Session()

try:
	req = ses.get(c_jazzRepoUrl + c_api_endpoint1, verify=False)
	req.raise_for_status()
except requests.exceptions.RequestException as e:
	print('Invalid URL',e)
	sys.exit()

#Sending the credentials for authentication to enter RTC
try:	
	data = {
	  'j_username': c_username,
	  'j_password': c_password
	}
	req = ses.post(c_jazzRepoUrl + c_api_endpoint2, data=data, verify=False)
	req.raise_for_status()
except requests.exceptions.HTTPError as e:
	print(req)
	print("Authentication error...!!!") 
	sys.exit()

	
#Looping the component code inorder to perform the registration of respective git repos 
try:
	for i in results.comp_code:
		headers ={
			'Accept':'text/json'
		}
		payload= {'name': rtc_git_name+'_'+i ,'ownerItemId': c_projectId,'currentPAItemId': c_projectId, 'url': url+'/'+i}
		req=ses.post(c_jazzRepoUrl+c_api_endpoint3 ,params=payload, headers=headers)
		req.raise_for_status()
		print(req)
		with open("/home/ubuntu/Soorya/registerOut", "a") as file:
			file.write(str(req.text))   
		
except requests.exceptions.HTTPError as e:
	print("Registration Failed")
	sys.exit()

#Printing the Keys and Checking for authentication
try:
	with open('/home/ubuntu/Soorya/registerOut', 'r') as content_file:
		input = content_file.read()
	matches = re.findall(r',"key":"([a-z0-9]*)"', input)
	matches[0]
	print(matches)

except IndexError:
	print('Authentication Failed')
