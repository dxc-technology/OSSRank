
import json
import requests
from urlparse import urljoin
from GitHubLogin import getGithubOauthtoken
from ProjectClassifier import classify_project
from util.configuration import getGitHubRepoPrefix, getGitHubSearchPageSize,\
    getGitHubRepoSearchUrl, getGitHubSearchTerm

##################################
# Methods returns a mapping of repository name -> full name
# this result is used to search and categorize the repository
##################################
def get_projects_metadata(jsonContent):
    all_proj=[]
    
    for item in jsonContent['items']:
        projDictionary = {}
        projDictionary['project_name'] = item ['name']
        projDictionary['metadata_url'] = getGitHubRepoPrefix() + item ['full_name']
        projDictionary['category'] = classify_project(item ['name'], item ['description'])
        all_proj.append(projDictionary)
            
    return all_proj

def main():
    ##get GitHub Oauth token
    git_auth_token = getGithubOauthtoken()
    
    ## start point to get data dump
    per_page_result_size = getGitHubSearchPageSize()
    
    ##create header for request containing auth token
    headers= {
              'Authorization':'token %s'% git_auth_token
             }
    
    ## while loop to fetch data
    current_fetch_url = urljoin(getGitHubRepoSearchUrl(), '' )
    current_fetch_res = requests.get(current_fetch_url, headers=headers)
    jsonRespData = json.loads(current_fetch_res.text)
    
    ## check the search result
    resultCount =jsonRespData['total_count']
    print 'total_count is: ' + str(resultCount)
    current_page = 0
    max_page = resultCount / per_page_result_size;
    print 'max_page is: ' + str(max_page)

    while (current_page <= max_page):
        fileName = fileName = 'github_search_dump_' + str(per_page_result_size * (current_page + 1)) + '.txt'
        print 'file name is: ' + fileName

        current_fetch_url = urljoin(getGitHubRepoSearchUrl(), 'repositories?' + getGitHubSearchTerm() + '&per_page=' + str(per_page_result_size) + '&page=' + str(current_page))
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
    
