 Overview
 ---------
   An automation script used for registering GitHub repositories in RTC (Rational Team Concert) and generate keys for creating webhooks, developed using Python 3.6.9.
   
Requirement
 -----------------------------------
  - __python 3.6.9__

Usage
 -----------------------------------
  python3 main_rtc.py --rc_url "<Jazz Repo Url>" --user "<Username of Jazz Repo>" --pass "<Password of Jazz Repo>" --git_url "<Git Url>" --app_code "<Application Code>" --component_code "<Space seperated component codes>" --team_area "<Space separated team areas>"  
  _eg_: python3 main_rtc.py --rtc_url "https://127.0.0.1:9443/ccm" --user "username" --pass "password" --git_url "https://github.mycompany.com/" --app_code "ABD" --component_code "abc_xyz" "abc_pqr" --team_area "ABC/pqr" "ABC/stu"

 Arguments
 -------------------------------------------------
  - ___--rtc_url___: The URL for the Change and Configuration management system. _eg:_ https://127.0.0.1:9443/ccm
  - ___--user___: The name of the user which sufficient privileges to register a GitHub repository in RTC project pointed using _projectID_
  - ___--pass___: The password for the user pointed out by _username_.
  - ___--git_url___: The root URL for the GitHub enterprise repository. _eg_: https://github.mycompany.com/
  - ___--app_code___: The three letter application code. _eg_: ABC
  - ___--component_code___: Space seperated codes for the component applications. _eg_: "abc_xyz" "abc_pqr"
  - ___--team_area___: Comma seperated team areas for the component applications. _eg_: "ABC/def" "ABC/stu"

  Workflow
 -----------------------------------
  - An opener for the APIs with the Cookie handler is generated and SSL handler is disabled.
  - Then the opener is made global for all other API calls.
  - Using _-app_code_ and  _-component_code_ and _git_url_ from arguments, GitHub repository URLs are auto-generated.
  - Using the autogenerated GitHub URLs and _rtc_url_, _user_, _passw_ and _team_area_ Six successive calls are made to the following three APIs for registering GitHub repositories in RTC
     - ___rtc_url/authenticated/identity___: For enabling cookie based authentication
     - ___rtc_url/authenticated/j_security_check___: For enabling cookie based authentication
     - ___rtc_url/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository___: For Registering the Git Repository
     - ___rtc_url/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/projectAreasPaged___: For resolving Project_ID
     - ___rtc_url/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/updateRegisteredGit/Repository___:  For collecting the generated key and update the registered repo with key.
     - ___rtc_url/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/projectHierarchy___: For getting project_hierarchy.
				
   - The response text after the third and fifth call is parsed for the key using json decoder.
   
  Output
 -----------------------------------
  The output of the script will be a mapping of the following format with an info ___"Successfully updated Register Git Hub repo https://github.com/app_name/component_name with the generated key aslkdkaslkdoihaosiidhansamd"___ : {component_code_1: key1, component_code_2: key2, ....}  
  _eg:_ {'abc_xyz': 'aslkdkaslkdoihaosiidhansamd', 'abc_pqr': 'aslkdkaslkkdnlaksksndklasnd'}
