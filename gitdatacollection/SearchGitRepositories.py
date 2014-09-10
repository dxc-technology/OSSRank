
import json
import requests
from urlparse import urljoin
from GitHubLogin import getGithubOauthtoken
import time
import simplejson
from ProjectClassifier import classify_project
#todo make the query manipulative by taking an user entry
GITHUB_REPO_SEARCH_URL = 'https://api.github.com/search/repositories?q=stars:">100"'
GITHUB_REPO_URL_PREFIX='https://api.github.com/repos/'

##################################
# methods returns a mapping of reponame->fullename
# this reuslt is used to search and categorize the repo
##################################
def get_projects_metadata(jsonContent):
    all_proj=[]
    i= 0
    for item in jsonContent['items']:
        projDictionary= {}
        projDictionary['project_name']=item ['name']
        projDictionary['metadata_url']=GITHUB_REPO_URL_PREFIX +item ['full_name']
        projDictionary['category'] = classify_project(item ['name'], item ['description'])
        all_proj.append(projDictionary)
        
        
    return all_proj

def main():
    ##get github auth token
    #git_auth_token = getGithubOauthtoken()
    git_auth_token='cd4bef7f31ccd9096368cdf2a197998e829c6509'
    
    ## start point to get data dump
    per_page_result_size=100
    
    
    ##create header for request containing auth token
    headers= {
              'Authorization':'token %s'% git_auth_token
              }
    ##
    fetch_github_data=True
    ## while loop to fetch data
    
    current_fetch_url=urljoin(GITHUB_REPO_SEARCH_URL, '' )
    current_fetch_res=requests.get(current_fetch_url, headers=headers)
    jsonRespData=json.loads(current_fetch_res.text)
    #check the search result
    resultCount =jsonRespData['total_count'] 
    while fetch_github_data :    
        
        fileName = 'github_search_dump_'+str(per_page_result_size)+'.txt'
        
        ## dump the data in a file/not in mongo
        
        filtered_proj_data=get_projects_metadata(jsonRespData)
            
        with open(fileName, 'w') as outfile:
            json.dump(filtered_proj_data, outfile)
         
        break;
        ##time.sleep(5)
    
if  __name__=='__main__':
    main()
    
