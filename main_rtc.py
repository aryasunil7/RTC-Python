import re
import requests
import configparser
import argparse
import sys
from configparser import ConfigParser, NoOptionError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.exceptions import ConnectionError


#Importing all the configuration details from rtc_config.ini using configparser
config = configparser.ConfigParser()
config.read('rtc_config.ini')
try:
	c_jazzRepoUrl=config['Default'].get('jazzRepoUrl')
	c_git_url=config['Default'].get('git_url')
	c_projectId=config['Default'].get('projectId')
	c_api_endpoint1=config['API'].get('api_endpoint1')
	c_api_endpoint2=config['API'].get('api_endpoint2')
	c_api_endpoint3=config['API'].get('api_endpoint3')
	c_password=config['User'].get('password')
	c_username=config['User'].get('username')
	
except NoOptionError as err:
    sys.exit(str(err) + "It should be provided")

if not (c_jazzRepoUrl and c_git_url and c_projectId and  c_api_endpoint1 and  c_api_endpoint2 and c_api_endpoint3 and c_username and c_password):
	sys.exit('Please check into rtc_config.ini , Check whether key value pairs are properly assigned!!!')


#Using argparse for app_code comp_code to parse there values through commandline
parser = argparse.ArgumentParser()
parser.add_argument('-app_code', dest='app_code', action="store",help='enter an app_code of type string', required=True)
parser.add_argument('--comp_code', dest='comp_code',nargs='+',help='enter a list of component code of type string', required=True)
results =  parser.parse_args()
print("App Code=    ",results.app_code)
print("Comp Code=    ",results.comp_code)
rtc_git_name = 'Git_'+results.app_code
url=c_git_url + results.app_code


#Checking whether the RTC url is accessible
ses = requests.Session()
try:
	res = ses.get(c_jazzRepoUrl + c_api_endpoint1, verify=False)
	res.raise_for_status()
except requests.exceptions.RequestException as e:
	sys.exit('Something went wrong in the url, Please check again...'+str(e))

	
#Sending the credentials for authentication to enter RTC
try:	
	data = {
	  'j_username': c_username,
	  'j_password': c_password
	}
	res = ses.post(c_jazzRepoUrl + c_api_endpoint2, data=data, verify=False)
	res.raise_for_status()
except (requests.exceptions.RequestException,requests.HTTPError,requests.exceptions.ConnectionError) as e: 
	sys.exit('Something went wrong , Please check again... '+str(e)) 

	
	
#Looping the component code inorder to perform the registration of respective git repos 
headers ={
	'Accept':'text/json'
}
comp_key={comp: '' for comp in results.comp_code}
for comp in results.comp_code:
	try:

		payload= {'name': rtc_git_name+'_'+comp ,'ownerItemId': c_projectId,'currentPAItemId': c_projectId, 'url': url+'/'+comp}
		res=ses.post(c_jazzRepoUrl+c_api_endpoint3 ,params=payload, headers=headers)
		res.raise_for_status()
	except requests.exceptions.HTTPError as e:
		sys.exit('Registration Failed !!! Please Check Again... '+str(e))
		
#Printing the Keys and Checking for authentication	
	try:
		response=res.text
		matches = re.findall(r',"key":"([a-z0-9]*)"', response)
		#print(res.json()['soapenv:Body']['response']['returnValue']['value']['key']) 
		comp_key[comp]=matches[0]
	except IndexError as e:
		sys.exit('Authentication or Key Generation Failed !!! Please Check Again... '+str(e))

print(comp_key)



