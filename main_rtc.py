from ConfigParser import ConfigParser, NoOptionError
import argparse
import re
import sys
import ssl
import urllib2
import urllib
import cookielib
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree


# API Definitions
api_endpoint1 = '/authenticated/identity'
api_endpoint2 = '/authenticated/j_security_check'
api_endpoint3 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository'
api_endpoint4 = '/process/project-areas'



# Taking application code and component code through command line using argparser
parser = argparse.ArgumentParser()
parser.add_argument('--app_code', action='store', dest='app_code', required=True,help='Three letter code for the application.')
parser.add_argument('--component_code', dest='component_code', nargs='+', required=True,help='Component code. If multiple components, provide component codes interleaved with spaces.')
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


# Starting API Calls
# get Call to api_endpoint1. post call to api_endpoint2
try:
	
	context = ssl._create_unverified_context()
	cj = cookielib.MozillaCookieJar()
	handlers = [
	urllib2.HTTPSHandler(context=context),
	urllib2.HTTPCookieProcessor(cj),
	]
	opener = urllib2.build_opener(*handlers)
	urllib2.install_opener(opener)
	response = opener.open(c_jazzRepoUrl + api_endpoint1)
	
	# save cookies to disk. you can load them with cookies.load() as well.


	data = {
		'j_username': c_username,
		'j_password': c_password
	}
	data_encoded = urllib.urlencode(data)
	response = opener.open(c_jazzRepoUrl + api_endpoint2, data_encoded)
	print(cj)
	for cookie in cj:
		print(cookie.name, cookie.value)
	
	
	#res = ses.post(c_jazzRepoUrl + api_endpoint2, data=data, verify=False)
	#res.raise_for_status()
except Exception as err:
	sys.exit("ERROR!. Please check settings in rtc.ini file and try again.\n Error: {}".format(str(err)))

			 
headers = {
    'Accept': 'text/json'
}

# Dictionary of the format {component_code: key}
comp_key = {comp: '' for comp in component_code}
for comp in component_code:
    try:
		data = {'name': app_code + '_' + comp, 'ownerItemId': ownerItemId, 'currentPAItemId': currentPAItemId,
                   'url': git_url + '/' + comp}
		data_encoded = urllib.urlencode(data)
		req = urllib2.Request(c_jazzRepoUrl + api_endpoint3, data_encoded, headers)
		res = opener.open(req)
        # Extracting key from response using regex
		registerKey = res.read()
		response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)
		comp_key[comp] = response_key[0]

        # Key Fetching from Json - res.json()['soapenv:Body']['response']['returnValue']['value']['key'])

    except (urllib2.HTTPError, IndexError) as err:
        comp_key[comp] = "Error!:Git Repo registration failed for component: {}. Please check whether the git repo at" \
                         " {} is already registered. If not, Please check settings in rtc.ini file and try again. " \
                         "Error: {}".format(comp, git_url + '/' + comp, str(err))
	except requests.exceptions.ConnectionError as err:
		sys.exit("ERROR!. Could not connect to the server. Please check internet connectivity and try again.\n Error: "
			 "{}".format(str(err)))

import pprint
printer = pprint.PrettyPrinter()
printer.pprint(comp_key)



