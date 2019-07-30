from configparser import ConfigParser, NoOptionError
import configparser
import argparse
import re
import requests
import sys
import urllib3

# Mute insecure warning 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Taking application code and component code through command line using argparser
parser = argparse.ArgumentParser()
parser.add_argument('--app_code', dest='app_code', action="store",required=True, help='Three letter code for the application.')
parser.add_argument('--component_code', dest='component_code',nargs='+', required=True, help='Component code. If multiple components, provide component codes interleaved with spaces.')
args =  parser.parse_args()

# argparse variables
app_code = args.app_code
component_code = args.component_code

# Reading configfile.ini using configparser
config = configparser.ConfigParser()
config.read('rtc_config.ini')

# Parsing config file
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
    raise sys.exit("Missing configurations in rtc.ini. Please check and try again.")


# API setup
rtc_git_name = 'Git_'+ app_code
git_url=c_git_url + args.app_code
ownerItemId = c_projectId
currentPAItemId = c_projectId

# Starting a session. 3 API calls are made on the same session.
ses = requests.Session()

# Starting API Calls
# get Call to api_endpoint1
try:
	res = ses.get(c_jazzRepoUrl + c_api_endpoint1, verify=False)
	res.raise_for_status()
except requests.exceptions.RequestException as err:
	sys.exit("Error at api_endpoint1. Please check jazzRepoUrl and api_endpoint1 setting in rtc.ini file and try "
             "again. Error: {}".format(str(err)))
	
# post Call to api_endpoint2
try:	
	data = {
	  'j_username': c_username,
	  'j_password': c_password
	}
	res = ses.post(c_jazzRepoUrl + c_api_endpoint2, data=data, verify=False)
	res.raise_for_status()
except (requests.exceptions.RequestException,requests.HTTPError,requests.exceptions.ConnectionError) as err: 
	sys.exit("Error at api_endpoint2. Please check jazzRepoUrl, api_endpoint2, username and password setting in "
             "rtc.ini file and try again. Error: {}".format(str(err)))

# post call to api_endpoint3. This call will register the git repo and collect the generated key. 
headers ={
	'Accept':'text/json'
}

# Dictionary of the format {component_code: key}
comp_key = {comp: '' for comp in component_code}

for comp in component_code:
	try:
		payload= {'name': rtc_git_name+'_'+comp ,'ownerItemId': ownerItemId,'currentPAItemId': currentPAItemId, 'url': git_url+'/'+comp}
		res=ses.post(c_jazzRepoUrl+c_api_endpoint3 ,params=payload, headers=headers)
		res.raise_for_status()
	
		# Extracting key from response using regex
		registerKey = str(res.text)
		response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)
		comp_key[comp] = response_key[0]
		
		# Key Fetching from Json - res.json()['soapenv:Body']['response']['returnValue']['value']['key'])

	except requests.exceptions.HTTPError as err:
		comp_key[comp] = "Git Repo registration failed for component: {}. Please check jazzRepoUrl, api_endpoint3 " \
                         "and projectId setting in rtc.ini file and try again. Error: {}".format(comp, str(err))

	except IndexError:
		comp_key[comp] = "Git Repo registration failed for component: {}. Please check username and password setting " \
                         "in rtc.ini file and try again. Error: {}".format(comp, str(err))

print(comp_key)




