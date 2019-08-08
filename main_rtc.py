from ConfigParser import ConfigParser, NoOptionError
import argparse
import re
import sys
import urllib2,cookielib,urllib
import ssl
import os
from cookielib import CookieJar

# API Definitions
api_endpoint1 = '/authenticated/identity'
api_endpoint2 = '/authenticated/j_security_check'
api_endpoint3 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository'

# Taking application code and component code through command line using argparser
parser = argparse.ArgumentParser()
parser.add_argument('--app_code', action='store', dest='app_code', required=True,
                    help='Three letter code for the application.')
parser.add_argument('--component_code', dest='component_code', nargs='+', required=True,
                    help='Component code. If multiple components, provide component codes interleaved with spaces.')
args = parser.parse_args()

# argparse variables
app_code = args.app_code
component_code = args.component_code

# Reading configfile.ini using configparser
config = ConfigParser()
config.read('rtc.ini')

# Parsing config file
try:
    c_jazzRepoUrl = config.get('Default', 'jazzRepoUrl')
    c_git_url = config.get('Default', 'git_url')
    c_projectId = config.get('Default', 'projectId')
    c_username = config.get('User', 'username')
    c_password = config.get('User', 'password')
except NoOptionError as err:
    sys.exit(str(err) + "It should be provided")

if not (c_jazzRepoUrl and c_git_url and c_projectId and c_username and c_password):
    sys.exit("Missing configurations in rtc.ini. Please check and try again.")

# API setup
git_url = (c_git_url[-1] == '/' and c_git_url or c_git_url + '/') + app_code
ownerItemId = c_projectId
currentPAItemId = c_projectId

# Starting a session. 3 API calls are made on the same session.
context = ssl._create_unverified_context()
cj = cookielib.CookieJar()
handlers = [
    urllib2.HTTPSHandler(context=context),
    urllib2.HTTPCookieProcessor(cj)
    ]
opener = urllib2.build_opener(*handlers)
urllib2.install_opener(opener)


response = opener.open(c_jazzRepoUrl + api_endpoint1)
data = {
	'j_username': c_username,
	'j_password': c_password
}
value = urllib.urlencode(data)
response = opener.open(c_jazzRepoUrl + api_endpoint2, value)


#post call to api_endpoint3. This call will register the git repo and collect the generated key.
# Dictionary of the format {component_code: key}
comp_key = {comp: '' for comp in component_code}
for comp in component_code:
	payload = {'name': app_code + '_' + comp, 'ownerItemId': ownerItemId, 'currentPAItemId': currentPAItemId,'url': git_url + '/' + comp}
	values = urllib.urlencode(payload)
	req = urllib2.Request(c_jazzRepoUrl + api_endpoint3, values,headers = {'Accept': 'text/json'})
	res= urllib2.urlopen(req)
	print(res.getcode())
	
	# Extracting key from response using regex

	registerKey = res.read()
	response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)
	comp_key[comp] = response_key[0]
import pprint
printer = pprint.PrettyPrinter()
printer.pprint(comp_key)
