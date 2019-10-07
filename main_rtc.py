import argparse
import sys
import xml.etree.ElementTree as ET
import pprint
import urllib.request, urllib.parse, urllib.error
import ssl
import json
import logging
import http.cookiejar
#Configuring logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s -%(levelname)s -%(message)s' )



# API Definitions
api_endpoint1 = '/authenticated/identity'
api_endpoint2 = '/authenticated/j_security_check'
api_endpoint3 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository'
api_endpoint4 = '/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/projectAreasPaged'
api_endpoint5 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/updateRegisteredGit' \
				'Repository'
api_endpoint6 = '/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/projectHierarchy'


# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument('--rtc_url', action='store', dest='rtc_url', required=True, help='RTC url. eg: https://rtcdev.it.statestr.com:9443/ccm' )
parser.add_argument('--user', action='store', dest='username', required=True, help='User Id used for establishing connection to RTC' )
parser.add_argument('--pass', action='store', dest='password', required=True, help='Password for User ID provided in --user argument for establishing connection to RTC' )
parser.add_argument('--git_url', action='store', dest='git_url', required=True, help='Git Url. eg: https://gitdev.it.statestr.com/' )
parser.add_argument('--app_code', action='store', dest='app_code', required=True,help='Three letter code for the application.')
parser.add_argument('--component_code', dest='component_code', nargs='+', required=True,help='Component code: Team Area .If multiple components, provide component codes interleaved with spaces.')
parser.add_argument('--team_area', dest='team_area', nargs='+', required=True, help='Team Area, If multiple components, provide team areas interleaved with '' spaces.' )
args = parser.parse_args()

# argparse variables
app_code = args.app_code
component_code = args.component_code
team_area = args.team_area
if len(component_code) != len(team_area):
	sys.exit("ERROR!. The number of items in component_code and team_area should be equal")
c_username = args.username
c_password = args.password
c_jazzRepoUrl = args.rtc_url[-1] == '/' and args.rtc_url[:-1] or args.rtc_url
c_git_url = args.git_url

# API setup
git_url = (c_git_url[-1] == '/' and c_git_url or c_git_url + '/') + app_code

# Logging formatted parameters
logging.info(f'Project Area name(Application Code): {app_code}')
logging.info(f'Component Codes: {",".join(component_code)}')
logging.info(f'Team Areas:{",".join(team_area)}')
logging.info(f'RTC Url: {c_jazzRepoUrl}')
logging.info(f'RTC Username: {c_username}')
logging.info(f'Git Url Root: {git_url}')

def find_team_area(team_areas, project_hierarchy):
	team_area_split = team_areas.split('/', 1)
	for i in project_hierarchy:
		if i['name'] == team_area_split[0]:
			if len(team_area_split) == 1:
				return i.get('itemId')
			else:
				if i.get('children'):
					return find_team_area(team_area_split[1], i.get(children))
				else:
					return False
	else:
		return False


#Starting an opener with cookies and disabling ssl certificate verification
# TODO SSL Certificate verification if any
logging.warning('Disabling SSL verification.')
context = ssl._create_unverified_context() #Mute insecure warning
logging.info('Creating Cookie.')
cookie = http.cookiejar.CookieJar()
handlers = [
	urllib.request.HTTPSHandler(context=context),
	urllib.request.HTTPCookieProcessor(cookie),
]
logging.info('Creating Opener')
opener = urllib.request.build_opener(*handlers) #Opener for the APIs with the Cookie handler and disabled SSL handler
logging.info('Installing Opener')
urllib.request.install_opener(opener) #Make the opener global foe all further calls
logging.info('Opener installed successfully.')
#Starting API Calls

# get Call to api_endpoint1. post call to api_endpoint2
logging.info('Starting Authentication')
try:
	logging.info(f'API call to {c_jazzRepoUrl + api_endpoint1} for Authentication')
	opener.open(c_jazzRepoUrl + api_endpoint1)
	data = urllib.parse.urlencode({'j_username': c_username,'j_password': c_password}).encode("utf-8")
	logging.info(f'API call to {c_jazzRepoUrl + api_endpoint2} for Authentication')
	opener.open(c_jazzRepoUrl + api_endpoint2, data)
except urllib.error.HTTPError as err:
	logging.error("Authentication Failed!.Please check the parameters provided and try again. Error: {} - {}".format('api_endpoint1,api_endpoint2', str(err.code) + ':' + err.reason))
	sys.exit("Error")
except urllib.error.URLError as err:
	logging.error("Authentication Failed!. Could not connect to the server. please check rtc_url- {}, internet connectivity and try again. Error: {} - {}".format(c_jazzRepoUrl,'api_endpoint1,api_endpoint2', str(err.reason)))
	sys.exit("Error")

#get call to api_endpoint4 and resolving Project ID.

logging.info('Starting Project ID resolution.')
headers = {
	'Accept': 'text/json'
}
try:
	params = urllib.parse.urlencode({
		'hideArchivedProjects': "true",
		'owningApplicationKey': 'JTS-Sentinel-Id',
		'pageNum':0,
		'pageSize': 25,
		'nameFilter': '*' + app_code + '*'
	})
	logging.info(f'API call to {c_jazzRepoUrl + api_endpoint4 + "?" + params}')
	req = urllib.request.Request(c_jazzRepoUrl + api_endpoint4 + "?" + params, headers=headers)
	res = opener.open(req)
	res_json = json.loads(res.read().decode())
	currentPAItemId = res_json["soapenv:Body"]["response"]["returnValue"]["value"]["elements"][0]["itemId"]
	logging.info(f'Project Id resolution successfull for {app_code}: {currentPAItemId}')
except KeyError as err:
	logging.error(
		"Project ID resolution failed!. Could not find Project ID for app code: {}. Please check the parameters and try again. Error: {} - {}".format(app_code, 'api_endpoint4', str(err)))
	sys.exit("Error")
except urllib.error.HTTPError as err:
	logging.error(
		"Project ID resolution failed!. Could not find Project ID for app code: {}. Please check the parameters provided and try again. Error: {} - {}".format(app_code, 'api_endpoint4', str(err.code) + ':' + err.reason))
	sys.exit("Error")
except urllib.error.URLError as err:
	logging.error(
		"Project ID resolution failed!. Could not find Project ID for app code: {}. Could not connect to the server. Please check internet connectivity and try again.\n Error: {} - {}".format(app_code, 'api_endpoint4', str(err.reason)))
	sys.exit("Error")
except json.decoder.JSONDecodeError as err:
	logging.error(
		"Project ID resolution failed!. Please check the parameters provided and try again. Error: {} - {}".format('api_endpoint4', str(err)))
	sys.exit("Error")

logging.info('Starting Team Area Id resolution.')
# Get Call to api_endpoint6 to get project hierarchy
team_area_data = False
try:
	params = urllib.parse.urlencode({
		'uuid': currentPAItemId
	})
	logging.info(f'API call to {c_jazzRepoUrl + api_endpoint6 + "?" + params} to get Project Hierarchy')
	req = urllib.request.Request(c_jazzRepoUrl + api_endpoint6 + "?" + params, headers=headers)
	res = opener.open(req)
	res_json = json.loads(res.read().decode())
	team_area_data = res_json["soapenv:Body"]["response"]["returnValue"]["value"]["children"]
	logging.info(f'Project Hierarchy Retrieved successfully. {app_code}: {team_area_data}')
	
except KeyError as err:
	logging.error(
		"Team Area resolution failed!. Could not find Project hierarchy for given app code: {}. Error: {} - {}".format(app_code, 'api_endpoint6', str(err)))
	sys.exit("Error")
except urllib.error.HTTPError as err:
	logging.error(
		"Team Area resolution failed!. Could not find Project hierarchy for given app code: {}. Please check the parameters provided and try again. Error: {} - {}".format(app_code, 'api_endpoint6', str(err.code) + ':' + err.reason))
	sys.exit("Error")
except urllib.error.URLError as err:
	logging.error(
		"Team Area resolution failed!. Could not find Project hierarchy for given app code: {}. Could not connect to the server. Please check internet connectivity and try again.\n Error: {} - {}".format(app_code, 'api_endpoint6', str(err.reason)))
	sys.exit("Error")
	

logging.info('Parsing Project hierarchy for team area Ids')
# Resolving team area ID
team_areas_ids = {i: '' for i in team_area}
for team, comp in zip(team_area, component_code):
	logging.info(f'Processing Team Area : {team}')
	team_areas_ids[comp] = find_team_area(team.split('/', 1)[-1], team_area_data)
	if not team_areas_ids[comp]:
		logging.error("Team area resolution failed.Could not find ID for team area:{} for given app code:{}.\n Error: {}".format(team,app_code, 'I Resolving Team area ID'))
		sys.exit('Error')
	logging.info(f'Team area Id resolved for {team}: {team_areas_ids[comp]}')
	
# post call to api_endpoint3 and api_endpoint5. This call will register the git repo, collect the generated key and update the registered repo with key.
# Dictionary for the ormat {component_code: key}
logging.info('Starting Repo Registration')
comp_key = {comp: '' for comp in component_code}
for comp in component_code:
	#Generate key
	try:
		logging.info(f'Registering GitHub repo {git_url + "/" + comp}')
		payload = urllib.parse.urlencode({'name': comp, 'ownerItemId': team_areas_ids[comp], 'currentPAItemId': currentPAItemId,
				   'url': git_url + '/' + comp}).encode("utf-8")
		logging.info(f'API call to {c_jazzRepoUrl + api_endpoint3} with payload {payload}')
		req = urllib.request.Request(c_jazzRepoUrl + api_endpoint3, payload, headers=headers)
		res = opener.open(req)
		res_json = json.loads(res.read().decode())
		#response_key = re.findall(r',"key":"([a-z0-9]*)"', res.read())
		response_key = res_json['soapenv:Body']['response']['returnValue']['value']['key']
		comp_key[comp] = response_key
		logging.info(f'Git Hub repo {git_url + "/" +comp} register and secret key obtained: {response_key}')

        # Extracting key from response using regex

	except (urllib.error.HTTPError, ValueError) as err:
		logging.error("Git Repo registration failed for component: {}, repo: {}. If not, Please check the parameters provided/internet connectivity and try again. Error: {}".format(comp, git_url + '/' +comp, str(err)))
		comp_key[comp] = "Error"
		continue
	
	
	#Register Key
	try:
		logging.info(f'Updating Registered GitHub repo {git_url + "/" + comp} with key: {response_key}')
		params= urllib.parse.urlencode({
			'repoKey': comp_key[comp],
			'name': comp,
			'url': git_url + '/' + comp,
			'ownerItemId': team_areas_ids[comp],
			'secretKey': comp_key[comp],
			'ownerPresent': True,
			'configurationData': '{"com_ibm_team_git_config_use_repository_process_area_unmapped_refs":"true",'
								 '"com_ibm_team_git_config_commit_url_format":"",'
								 '"com_ibm_team_git_config_git_server_credentials":{"userId":"",'
								 '"encryptedPassword":""}}'
		}).encode("utf-8")
		logging.info(f'API call to {c_jazzRepoUrl + api_endpoint5} with payload {params}')
		req = urllib.request.Request(c_jazzRepoUrl + api_endpoint5, params, headers=headers)
		res = opener.open(req)
		logging.info(f'Successfully updated Register Git Hub repo {git_url + "/" + comp} with the generated key {response_key}')
	except (urllib.error.HTTPError, ValueError) as err:
		logging.error("Git Repo updation failed for component: {}. The git repoat {} is registered. Please delete it manually, check the parameters provided and try again. Error: {}".format(comp, git_url + '/' + comp, str(err)))
		comp_key[comp] = "Error"
		continue
	except urllib.error.URLError as err:
		logging.error("Git Repo updation failed for component: {}. The git repo at {} is registered. Please delete it manually, check internet connectivity and try again. Error: {}".format(comp, git_url + '/' + comp, str(err)))
		comp_key[comp] = "Error"
		continue
		
#Output
if len(comp_key) == 1:
	print(list(comp_key.values())[0])
else:
	printer = pprint.PrettyPrinter()
	printer.pprint(comp_key)

	


