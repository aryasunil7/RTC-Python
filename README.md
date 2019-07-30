# RTC-Python

RTC-Python is developed in Python3.This application is developed for integrating RTC and GitHub

The 'jazzRepoUrl','git_url','projectId','username','password','api_endpoint1','api_endpoint2','api_endpoint3' values are read from rtc_config.ini using ConfigParser 

Application code 'app_code' and Component code 'comp_code' values are given through command line argument using ArgParser

- A session is first created 
- "jazzRepoUrl/authenticated/identity" and "jazzRepoUrl/authenticated/j_security_check" are the two RTC URL for authenticating 
- "jazzRepoUrl/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository?name=$name&ownerItemId=$ownerItemId&currentPAItemId=$currentPAItemId&url=$url&description=$description" is the RTC URL for registering the git repository in RTC
- Keys for the registered repositories are generated and stored in a dictionary
