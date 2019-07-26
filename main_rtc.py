#Import Packages
import requests
import re
import configparser
import argparse
import sys
import urllib2

from cookielib import LWPCookieJar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#Configparser
config = configparser.ConfigParser()
config.read('/home/ubuntu/sruthi/config_rtc.ini')
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
except requests.exceptions.RequestException as err:
    print('---Session failed---',err)
    sys.exit()

  
#Authentication security
try:
	data = {
	   'j_username': Rtc_UserId, 
	   'j_password': Rtc_Password
	}
	auth_security = session.post(JazzRepoUrl + Auth_scurity_api, data=data,verify=False)
	auth_security.raise_for_status()
#	print(auth_security)
except AuthenticationException as e:
    print('---Authentication failed---')
    sys.exit()

	
#GitRepo Registration
try:
	for i in args.Comp_code:
		payload = {'name':git_name,'ownerItemId':ProjectId,'currentPAItemId':ProjectId,'url':git_url + '/' +i}
		headers = {'Accept':'text/json'}
		gitRepo_registration = session.post(JazzRepoUrl+GitRepo_reg_api, params=payload,headers=headers)
#		print(gitRepo_registration)
		with open('/tmp/registerOut', 'a') as file:
			file.write(str(gitRepo_registration.text))
	gitRepo_registration.raise_for_status()

except:
    print('---GitRepo registration failed---')
    sys.exit()

try:
	with open('/tmp/registerOut', 'r') as content_file:
		input = content_file.read()
	matches = re.findall(r',"key":"([a-z0-9]*)"', input)
	matches[0]
	print(matches)
except IndexError:
	print('---Key not found---')
