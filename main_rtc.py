from ConfigParser import ConfigParser, NoOptionError
import argparse
import re
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# API Definitions
api_endpoint1 = '/authenticated/identity'
api_endpoint2 = '/authenticated/j_security_check'
api_endpoint3 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository'

# Mute insecure warning 
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
ses = requests.Session()

# Starting API Calls
# get Call to api_endpoint1. post call to api_endpoint2
try:
    res = ses.get(c_jazzRepoUrl + api_endpoint1, verify=False)
    data = {
        'j_username': c_username,
        'j_password': c_password
    }
    res = ses.post(c_jazzRepoUrl + api_endpoint2, data=data, verify=False)
    res.raise_for_status()
except (requests.exceptions.RequestException, requests.HTTPError) as err:
    sys.exit("ERROR!. Please check settings in rtc.ini file and try again.\n Error: {}".format(str(err)))
except requests.exceptions.ConnectionError as err:
    sys.exit("ERROR!. Could not connect to the server. Please check internet connectivity and try again.\n Error: "
             "{}".format(str(err)))

# post call to api_endpoint3. This call will register the git repo and collect the generated key.
headers = {
    'Accept': 'text/json'
}

# Dictionary of the format {component_code: key}
comp_key = {comp: '' for comp in component_code}
for comp in component_code:
    try:
        payload = {'name': app_code + '_' + comp, 'ownerItemId': ownerItemId, 'currentPAItemId': currentPAItemId,
                   'url': git_url + '/' + comp}
        res = ses.post(c_jazzRepoUrl + api_endpoint3, params=payload, headers=headers)
        res.raise_for_status()

        # Extracting key from response using regex
        registerKey = str(res.text)
        response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)
        comp_key[comp] = response_key[0]

        # Key Fetching from Json - res.json()['soapenv:Body']['response']['returnValue']['value']['key'])

    except (requests.exceptions.HTTPError, IndexError) as err:
        comp_key[comp] = "Error!:Git Repo registration failed for component: {}. Please check whether the git repo at" \
                         " {} is already registered. If not, Please check settings in rtc.ini file and try again. " \
                         "Error: {}".format(comp, git_url + '/' + comp, str(err))
    except requests.exceptions.ConnectionError as err:
        sys.exit("ERROR!. Could not connect to the server. Please check internet connectivity and try again.\n Error: "
                 "{}".format(str(err)))
import pprint
printer = pprint.PrettyPrinter()
printer.pprint(comp_key)

