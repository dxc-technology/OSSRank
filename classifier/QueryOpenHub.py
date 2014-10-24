#!/usr/bin/env python
# encoding: utf-8


#purpose is to query openhub ..check tag and description
#openhub api used from https://github.com/blackducksw/ohloh_api
#using lxml api for xml parsing doc: lxml.de
import json
import requests
from urlparse import urljoin
import sys, urllib
import time
from lxml import etree
from lxml.etree import  Element
from lxml import etree as ElementTree
#todo make the query manipulative by taking an user entry
OPENHUB_SEARCH_URL = 'https://www.openhub.net/projects.xml'

#please use your own api key by registerring yourself at openhub.net
#OPENHUB_API_KEY = '7u9sgYGrr6nv2snYk8o7w'
OPENHUB_API_KEY = '40fcNIhGvhr3kPfRpH0IkQ'

######################
#method returns the openhubquery
######################
def getOpenHubQuery(gitProjectName):
     params = urllib.urlencode({'api_key':OPENHUB_API_KEY, 'v':1})
     queryUrl = OPENHUB_SEARCH_URL+'?query='+ gitProjectName+'&'+params
     return queryUrl



def queryOpenhubDetails(gitProjectName):
    ##uncomment below for debug only
    #print getOpenHubQuery('bootstrap')
    
    f=urllib.urlopen(getOpenHubQuery(gitProjectName))
    
    
    tree = ElementTree.parse(f)
    elem = tree.getroot()
    
        
    
    #check for error first
    error=elem.find('error')
    
    projectDataDictionary= {}
    
    if error != None:
        print 'openhub api returned an error while searching for project '+ gitProjectName + ElementTree.tostring(error)
        return projectDataDictionary 
    
    result_num=elem.find('items_available')
    print 'search for '+  gitProjectName +' returned '  + result_num.text + 'results'
    
    #the strategy the query is always against name and desc, so we make sure name contains what we search
    #if found collect the tags and then break the loop
    #1000 req allowed per day
    
    ##following code is  not required we will iterate through all results
    #for node in tree.find('result/project'):
    #    if node.tag == 'name':
    #        print node.text
    #     if node.tag == 'homepage_url':
    #         print node.text
    
    prj_found=False
    for Element in tree.findall('.//project'):
        
        project_name= Element.find('.//name').text
        download_url= Element.find('.//download_url').text
        #print download_url
        if(gitProjectName.lower() in project_name.lower() ):
            #check if the download  url contains both github.com and ends with gitprojectname
            if( (download_url is not None) and('github.com' in download_url) and (gitProjectName.lower() in download_url) ):
                project_desc= Element.find('.//description').text
                print "matching projects " + project_name 
                projectDataDictionary['desc']= project_desc
 
                tags=''
                for Element in Element.findall('.//tag'):
                    tags=tags +'  '+ Element.text
                #print 'project specific tags are' + tags
                
                if(tags != ''):
                    projectDataDictionary['tag']= tags
                prj_found=True
            #print projectDataDictionary.get('tag')
        if(prj_found): break
         
    return projectDataDictionary
    
    ##test code -- to be deleted
    #for node in tree.iterfind('.//name'):
    #    print node.text
         
    
    
def main():
    queryOpenhubDetails('free-programming-books')
    
if  __name__=='__main__':
    main()
    
