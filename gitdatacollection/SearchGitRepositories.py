
import json
import requests
from urlparse import urljoin
from GitHubLogin import getGithubOauthtoken
import time
import simplejson
from ProjectClassifier import classify_project
#todo make the query manipulative by taking an user entry
#as in the https://developer.github.com/v3/search/#search-repositories
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
        projDictionary = {}
        projDictionary['project_name'] = item ['name']
        projDictionary['metadata_url'] = GITHUB_REPO_URL_PREFIX + item ['full_name']
        projDictionary['category'] = classify_project(item ['name'], item ['description'])
        all_proj.append(projDictionary)
            
    return all_proj

def main():
    ##get github auth token
    #git_auth_token = getGithubOauthtoken()
    git_auth_token='cd4bef7f31ccd9096368cdf2a197998e829c6509'
    
    ## start point to get data dump
    per_page_result_size = 100
    
    ##create header for request containing auth token
    headers= {
              'Authorization':'token %s'% git_auth_token
             }
    ##
    fetch_github_data=True
    ## while loop to fetch data
    
    current_fetch_url = urljoin(GITHUB_REPO_SEARCH_URL, '' )
    current_fetch_res = requests.get(current_fetch_url, headers=headers)
    jsonRespData = json.loads(current_fetch_res.text)
    
    #check the search result
    resultCount =jsonRespData['total_count']
    print 'total_count is: ' + str(resultCount)
    current_page = 0
    max_page = resultCount / per_page_result_size;
    print 'max_page is: ' + str(max_page)

    while (current_page <= max_page):
          fileName = fileName = 'github_search_dump_' + str(per_page_result_size * (current_page + 1)) + '.txt'

          print 'file name is: ' + fileName

          current_fetch_url = urljoin(GITHUB_REPO_SEARCH_URL, 'repositories?q=stars:>100&per_page=' + str(per_page_result_size) + '&page=' + str(current_page))
          print 'current_fetch_url is: ' + current_fetch_url
          
          current_fetch_res = requests.get(current_fetch_url, headers=headers)
          jsonRespData = json.loads(current_fetch_res.text)

          ##dump the data in a file/not in mongo
          filtered_proj_data = get_projects_metadata(jsonRespData)
            
          with open(fileName, 'w') as outfile:
              json.dump(filtered_proj_data, outfile)

          current_page = current_page + 1
        
if  __name__=='__main__':
    main()
    
