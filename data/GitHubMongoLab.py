import requests
import json
from util.configuration import getMongoLabUrl, getGitHubRepoSearchUrl
 
# Get list of projects from GitHub
def getProjects():
    url = getGitHubRepoSearchUrl();
    r = requests.get(url)
    projects = r.json()
    return projects
 
# Insert projects into MongoDB using REST API
def addProjects(projects):
    url = getMongoLabUrl()
    headers = {'content-type': 'application/json'}
    
    for p in projects['items']:
        r = requests.post(url, data=json.dumps(p), headers=headers)
        ret = r.json()
        print ret
 
if __name__ == '__main__':
    projects = getProjects()
    addProjects(projects)
