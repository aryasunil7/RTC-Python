from ConfigParser import ConfigParser, NoOptionError
import argparse
import sys
import ssl
import urllib2
import urllib
import cookielib
import pprint
import json
import xml.etree.ElementTree as ET
import re


# API Definitions
api_endpoint1 = '/authenticated/identity'
api_endpoint2 = '/authenticated/j_security_check'
api_endpoint3 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository'
api_endpoint4 = '/process/project-areas'
api_endpoint5 = '/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/updateRegisteredGit' \
				'Repository'


# Taking application code and component code through command line using argparser
parser = argparse.ArgumentParser()
parser.add_argument('--app_code', action='store', dest='app_code', required=True,help='Three letter code for the application.')
parser.add_argument('--component_code', dest='component_code', nargs='+', required=True,help='Component code: Team Area .If multiple components, provide component codes interleaved with spaces.')
args = parser.parse_args()

# argparse variables
app_code = args.app_code

try:
	component_code = [(i.split(':')[0], i.split(':')[1]) for i in args.component_code]
	team_areas= list(set([i[1] for i in component_code]))
except IndexError:
	sys.exit('Error: --component_code should be of format component_1:team_area_1 component_2:team_area_2')



# Reading configfile.ini using configparser
config = ConfigParser()
config.read('rtc.ini')

# Parsing config file
try:
    c_jazzRepoUrl = config.get('Default', 'jazzRepoUrl')
    c_git_url = config.get('Default', 'git_url')
    c_username = config.get('User', 'username')
    c_password = config.get('User', 'password')
except NoOptionError as err:
	sys.exit(str(err) + "It should be provided")

if not (c_jazzRepoUrl and c_git_url and c_username and c_password):
	sys.exit("Missing configurations in rtc.ini. Please check and try again.")


# API setup
git_url = (c_git_url[-1] == '/' and c_git_url or c_git_url + '/') + app_code


#Starting an opener with cookies and disabling ssl certificate verification
context = ssl._create_unverified_context()
cookie = cookielib.CookieJar()
handlers = [
	urllib2.HTTPSHandler(context=context),
	urllib2.HTTPCookieProcessor(cookie),
]
opener = urllib2.build_opener(*handlers)
urllib2.install_opener(opener)

try:
	opener.open(c_jazzRepoUrl + api_endpoint1)
	data = urllib.urlencode({'j_username': c_username,'j_password': c_password})
	opener.open(c_jazzRepoUrl + api_endpoint2, data)
except urllib2.HTTPError as err:
	sys.exit("ERROR!. Please check settings in rtc.ini file and try again.\n Error: {}" "{}\n{}".format('api_endpoint1, api_endpoint2',str(err.code+':'+err.reason)))
except urllib2.URLError as err:
	sys.exit("ERROR!. Could not connect to the server.Please check the connectivity and try again .\n Error: {}" "{}\n{}".format('api_endpoint1, api_endpoint2',str(err.reason)))


#get call to api_endpoint4
try:
	res = opener.open(c_jazzRepoUrl + api_endpoint4)
	tree = ET.fromstring(res.read())

except ET.ParseError as err:
	sys.exit("ERROR!. Could not find projectid for given app code.\n Error: {}" "{}\n{}".format('api_endpoint4',str(err)))
except urllib2.HTTPError as err:
	sys.exit("ERROR!. Please check settings in rtc.ini file and try again.\n Error: {}" "{}\n{}".format('api_endpoint4',str(err.code+':'+err.reason)))
except urllib2.URLError as err:
	sys.exit("ERROR!. Could not connect to the server.Please check the connectivity and try again .\n Error: {}" "{}\n{}".format('api_endpoint4',str(err.reason)))

#Resolving project id
c_projectId = ''
team_area_url = ''
team_areas_ids = {i: '' for i in team_areas}
for i in tree:
	if i.get('{http://jazz.net/xmlns/prod/jazz/process/0.6/}name')== app_code:
		c_projectId = i.find('{http://jazz.net/xmlns/prod/jazz/process/0.6/}url').text.split('/')[-1]
		team_area_url = i.find('{http://jazz.net/xmlns/prod/jazz/process/0.6/}team-areas-url').text
if c_projectId:
	currentPAItemId = c_projectId
else:
	sys.exit("ERROR!. Could not find projectid for given app code.\n Error: ""{}".format('In resolving project id'))
	
#get call to team_area_url
if team_area_url:
	try:
		res = opener.open(team_area_url)
		tree = ET.fromstring(res.read())
	except ET.ParseError as err:
		sys.exit("ERROR!. Could not find Team Areas for given app code.\n Error: {}" "{}\n{}".format('api_endpoint4',str(err)))
	except urllib2.HTTPError as err:
		sys.exit("ERROR!. Please check settings in rtc.ini file and try again.\n Error: {}" "{}\n{}".format('api_endpoint4',str(err.code+':'+err.reason)))
	except urllib2.URLError as err:
		sys.exit("ERROR!. Could not connect to the server.Please check the connectivity and try again .\n Error: {}" "{}\n{}".format('api_endpoint4',str(err.reason)))	


#Resolving Team Area ID
	for team_area in team_areas:
		for i in tree:
			if i.get('{http://jazz.net/xmlns/prod/jazz/process/0.6/}name') == team_area:
				team_areas_ids[team_area] = \
					i.find('{http://jazz.net/xmlns/prod/jazz/process/0.6/}url').text.split('/')[-1]
		if not team_areas_ids[team_area]:
			sys.exit("ERROR!. Could not find Team Area ID {} for given app code.\n Error: {}" "{}\n{}".format(team_area,'In Resolving project id'))
else:
	sys.exit("ERROR!. Could not find Team area URL for given app code.\n Error: {}" "{}\n{}".format('In resolving project id'))


#post call to api_endpoint3. This call will register the git repo and collect the generated key			 
headers = {
    'Accept': 'text/json'
}

# Dictionary of the format {component_code: key}
comp_key = {comp[0]: '' for comp in component_code}
for comp in component_code:
	#Generate key
	try:
		payload = urllib.urlencode({'name': comp[0], 'ownerItemId': team_areas_ids[comp[1]], 'currentPAItemId': currentPAItemId,
				   'url': git_url + '/' + comp[0]})
		req = urllib2.Request(c_jazzRepoUrl + api_endpoint3, payload, headers=headers)
		res = opener.open(req)
		res_json = json.loads(res.read().decode())
		print(type(res_json))
		#response_key = re.findall(r',"key":"([a-z0-9]*)"', res.read())
		response_key = res_json['soapenv:Body']['response']['returnValue']['value']['key']
		comp_key[comp[0]] = response_key

        # Key Fetching from Json - res.json()['soapenv:Body']['response']['returnValue']['value']['key'])

	except (urllib2.HTTPError, ValueError) as err:
		comp_key[comp[0]] = "Error!:Git Repo registration failed for component: {}. Please check whether the git repo at" \
							" {} is already registered. If not, Please check settings in rtc.ini file and try again. " \
							"Error: {}".format(comp[0], git_url + '/' + comp[0], str(err))
		continue
	except urllib2.URLError as err:
		comp_key[comp[0]] = "ERROR!. Could not connect to the server.Please check the connectivity and try again .\n Error: {}" 					"{}\n{}".format(str(err))
		continue 
	
	#Register Key
	try:
		params= urllib.urlencode({
			'repoKey': comp_key[comp[0]],
			'name': comp[0],
			'url': git_url + '/' + comp[0],
			'ownerItemId': team_areas_ids[comp[1]],
			'secretKey': comp_key[comp[0]],
			'ownerPresent': True,
			'configurationData': '{"com_ibm_team_git_config_use_repository_process_area_unmapped_refs":"true",'
								 '"com_ibm_team_git_config_commit_url_format":"",'
								 '"com_ibm_team_git_config_git_server_credentials":{"userId":"",'
								 '"encryptedPassword":""}}'
		})
		req = urllib2.Request(c_jazzRepoUrl + api_endpoint5, params, headers=headers)
		res = opener.open(req)
	except (urllib2.HTTPError, ValueError) as err:
		comp_key[comp[0]] = "Error!:Git Repo registration failed for component: {}. Please check whether the git repo at" \
							" {} is already registered. If not, Please check settings in rtc.ini file and try again. " \
							"Error: {}".format(comp[0], git_url + '/' + comp[0], str(err))

	except urllib2.URLError as err:
		sys.exit("ERROR!. Could not connect to the server.Please check the connectivity and try again .\n Error: ""{}".format(str(err)))
	
#Output
printer = pprint.PrettyPrinter()
printer.pprint(comp_key)



