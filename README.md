# RTC-Python

RTC-Python is developed in Python3.This application is developed for integrating RTC and GitHub

The 'jazzRepoUrl','git_url','projectId','username','password','api_endpoint1','api_endpoint2','api_endpoint3' values are read from rtc_config.ini using ConfigParser

Application code 'app_code' and Component code 'comp_code' values are given through command line argument using ArgParser

- A session is first created
- "jazzRepoUrl/authenticated/identity" and "jazzRepoUrl/authenticated/j_security_check" are the two RTC URL for authenticating
- "jazzRepoUrl/service/com.ibm.team.git.common.internal.IGitRepositoryRegistrationRestService/RegisterGitRepository?name=$name&ownerItemId=$ownerItemId&currentPAItemId=$currentPAItemId&url=$url&description=$description" is the RTC URL for registering the git repository in RTC
- Keys for the registered repositories are generated and stored in a dictionary

I) Requirement requests==2.9.1

II) Modules
  
  a) requests
       Requests is a Python module that you can use to send all kinds of HTTP requests. It is an easy-to-use library with a lot of features ranging from passing parameters in URLs to sending custom headers and SSL Verification. In this tutorial, you will learn how to use this library to send simple HTTP requests in Python.
                
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
        
  - To run the application: 
  
         python rtc.py -App_code XYZ -Comp_code frontend -Comp_code UI
