#Import Packages
import requests
import re
import configparser
import argparse
import sys
import logging

from cookielib import LWPCookieJar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#Configparser
config = configparser.ConfigParser()
config.read('/home/ubuntu/sruthi/rtcConfig.ini')
##print(config.sections()) 

#Config_values
JazzRepoUrl = config.get('Default', 'jazzRepoUrl')
Root_GitRepoUrl = config.get('Default', 'root_gitUrl')
ProjectId = config.get('Default', 'projectId')
Auth_api = config.get('Auth', 'auth_api')
Auth_scurity_api = config.get('Auth', 'auth_security')
GitRepo_reg_api = config.get('Auth', 'gitRepo_reg')
Rtc_UserId = config.get('User', 'rtc_userId')
Rtc_Password = config.get('User', 'rtc_password')

#Argparser
parser = argparse.ArgumentParser()
parser.add_argument('-App_code', action='store', dest='App_code',type=str)
parser.add_argument('-Comp_code', action='append', dest='Comp_code',type=str)
args = parser.parse_args()

print 'App_code =', args.App_code
print 'Comp_code =',args.Comp_code
git_name = args.App_code
git_url = Root_GitRepoUrl + args.App_code
print('git_url: ' + git_url) 

#jazzCookiesFile = "/tmp/jazzCookies.txt"

session = requests.Session()

#Auth_api
try:
	auth = session.get(JazzRepoUrl + Auth_api,verify=False)
	auth.raise_for_status()
#	print(auth)
except requests.exceptions.HTTPError as err:
    print('Session failed')
    sys.exit(1)
#   	print('Session failed')
  
#Authentication security
try:
	data = {
	   'j_username': Rtc_UserId, 
	   'j_password': Rtc_Password
	}
	auth_security = session.post(JazzRepoUrl + Auth_scurity_api, data=data,verify=False)
	auth_security.raise_for_status()
	return True
#	print(auth_security)
except AuthenticationException:
    print('Authentication failed')
    sys.exit(1)
#	print('Authentication failed',( str(e) ))
#	raise SystemExit

#GitRepo Registration
try:
	for i in args.Comp_code:
		payload = {'name':git_name,'ownerItemId':ProjectId,'currentPAItemId':ProjectId,'url':git_url + '/' +i}
		headers = {'Accept':'text/json'}
		gitRepo_registration = session.post(JazzRepoUrl+GitRepo_reg_api, params=payload,headers=headers)
#		print(gitRepo_registration)
		with open('/tmp/registerOut'+i, 'a') as content_file:
			content_file.write(str(gitRepo_registration.text))
		with open('/tmp/registerOut'+i, 'r') as content_file:
			input = content_file.read()
		matches = re.findall(r',"key":"([a-z0-9]*)"', input)
		print('key: ' + matches)
#	gitRepo_registration.raise_for_status()

except:
    print('GitRepo registraion failed')
    sys.exit(1)
#	print('GitRepo registraion failed')