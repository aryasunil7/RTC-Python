import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

jazzRepoUrl="https://18.144.18.92:9443/ccm"
projectId="_noACAKbtEemBaOpk7wfjpg"     # UUID of the jazz project area
jazzUserId="admin"
jazzPassword="admin"
jazzCookiesFile="/tmp/jazzCookies.txt"
name="GitRepo_arya"
description="AGitRepository_trial"
ownerItemId="_noACAKbtEemBaOpk7wfjpg"
currentPAItemId="_noACAKbtEemBaOpk7wfjpg"
url="https://github.com/aryasunil7/sample_rtc.git"

ses = requests.Session()


req = ses.get(jazzRepoUrl+'/authenticated/identity',verify=False)

data = {
  'j_username': jazzUserId,
  'j_password': jazzPassword
}
req = ses.post(jazzRepoUrl + '/authenticated/j_security_check', data=data, verify=False)


headers ={
	'Accept':'text/json'
}
payload= {'name': name ,'ownerItemId': ownerItemId,'currentPAItemId': currentPAItemId, 'url':url}

req=ses.post(jazzRepoUrl+'/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository' ,params=payload, headers=headers)

with open("/tmp/registerOut1", "a") as file:
	file.write(req.text)

with open('/tmp/registerOut1','r') as content_file:
	    input = content_file.read()
matches = re.findall(r',"key":"([a-z0-9]*)"', input)
print(matches[0])



	



