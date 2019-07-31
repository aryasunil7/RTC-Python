# RTC-Python
	
 Overview
 ---------
  RTC-Python is developed in Python2.This application is developed for integrating RTC and GitHub such that it will automate the Repo_registration in Rtc and extraction of key.

  - A session is first created 
  - "jazzRepoUrl/authenticated/identity" and "jazzRepoUrl/authenticated/j_security_check" are the two RTC URL for authenticating 
  - "jazzRepoUrl/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository?        name=$name&ownerItemId=$ownerItemId&currentPAItemId=$currentPAItemId&url=$url&description=$description" is the RTC URL for registering    the git repository in RTC
  - Keys for the registered repositories are generated and stored in a dictionary

 Explanation for Configuration File and argparser
 -------------------------------------------------
   
 - The 'jazzRepoUrl','git_url','projectId','username','password','api_endpoint1','api_endpoint2','api_endpoint3' values are read from      rtc_config.ini using ConfigParser.
 - Application code 'app_code' and Component code 'component_code' values are given through command line argument using ArgParser.
 - The 'help' in argparser will provide useful help messages.
 - 'nargs' in argparser is used to handle variable number of arguments (nargs='+').
 
 I) Requirement
   -------------
     requests==2.22.0
 
II) Recommended Modules
   ---------------------
  a) requests
       Requests is a Python module that you can use to send all kinds of HTTP requests. It is an easy-to-use library with a lot of features ranging from passing parameters in URLs to sending custom headers and SSL Verification. 
	
    i) Installation
        pip install requests

    ii) Usage
        import requests

        res = ses.get(url)
        res = ses.post(url)		
  
  b) configparser
        This module provides the ConfigParser class which implements a basic configuration language which provides a structure similar to what’s found in Microsoft Windows INI files. You can use this to write Python programs which can be customized by end users easily.
	
    i) Usage
        import configparser

        config = configparser.ConfigParser()
        config.read('example.ini')	
		variable_name= config.get('session','option')
		
  c) argparse
        Python argparse is the recommended command-line argument parsing module in Python.
	
    i) Usage   
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-app_code', action='store', dest='app_code', type=str)	
        args = parser.parse_args()

  d) Regex 
        A regular expression in a programming language is a special text string used for describing a search pattern. It is extremely useful for extracting information from text such as code, files, log, spreadsheets or even documents.
	
    i) Usage
        import re
  
        response_key = re.findall(r',"key":"([a-z0-9]*)"', registerKey)

  e) sys
        This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
	
    i) Usage 
        import sys
 
        sys.exit()
	
III) Exception Handled
-----------------------
  The various exceptions handled in the code are:-
    - NoOptionError for checking if the sessions contains all options needed in the configuration file.
    - RequestException to check whether the connection is alive or not.
    - HTTPError for handling exotic HTTP errors, such as requests for authentication.
    - ConnectionError for checking if the url is not working and site is not loading.
    - IndexError for checking the list is empty or not.

	
IV) Command for Running the Code
------------------------------------
  python main_rtc.py -app_code name --component_code name1 name2 .....
      
 V) Expected Output
---------------------
  - The expected output from the code are the list of keys which are registered as repo in the Rtc along with each component codes.
      eg:- {'componenent_code1': 'key1', 'component_code2': 'key2', ....}
  - These keys are stored as a dictionary.
  
VI) Known Errors
------------------
  - The second post api_endpoint2 is giving 200 as status if the username or password given is wrong instead of 404 error status.
  - But the repo is not registered in Rtc if username and passord is wrong.
  

     
