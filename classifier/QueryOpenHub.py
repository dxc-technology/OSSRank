#Purpose is to query OpenHub ..check tag and description
#OpenHub API used from https://github.com/blackducksw/ohloh_api
#using lxml api for xml parsing doc: lxml.de
import urllib
from lxml.etree import  Element
from lxml import etree as ElementTree
from util.configuration import getOpenHubAPIKey, getOpenHubSearchUrl

#Method returns the OpenHub query
def getOpenHubQuery(gitProjectName):
    params = urllib.urlencode({'api_key': getOpenHubAPIKey(), 'v':1})
    queryUrl = getOpenHubSearchUrl() + '?query=' + gitProjectName + '&' + params
    return queryUrl

def queryOpenhubDetails(gitProjectName): 
    f = urllib.urlopen(getOpenHubQuery(gitProjectName))
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
    
