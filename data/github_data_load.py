import requests
import json
from urlparse import urljoin
import time
import simplejson
import csv

#to do REFACTOR code 
#read configuration
config_reader = ConfigParser.ConfigParser()
config_reader.read('config.cfg')



GITHUB_REPO_SEARCH_URL = 'https://api.github.com/search/repositories?q=forks:">10"'
GITHUB_REPO_URL_PREFIX='https://api.github.com/repos'
GITHUB_REPO_URL = 'https://api.github.com/repositories'
#result from google big query exported in a csv file
GIT_HUB_INPUT_FILE = "..."

# Configuration
config = {
    'apiURL' : config_reader.get('Mongolab', 'apiURL' ),
    'apiKey' : config_reader.get('Mongolab', 'apiKey'),
    'database' : config_reader.get('Mongolab', 'database' ), 
    'git_token':config_reader.get('github', 'authToken' )
}

git_auth_token=config['git_token']
    
    ## start point to get data dump
per_page_result_size = 100
    
    ##create header for request containing auth token
headers_git= {
              'Authorization':'token %s'% git_auth_token
             }


def read_github_load_file():
    count = 0
    with open(GIT_HUB_INPUT_FILE, 'rb') as csvfile:
        gitprojectreader=csv.DictReader(csvfile)
        
        for row in gitprojectreader:
            count = count +1
            project_url=row['repository_url']
            if(not(project_url.rfind("https://github.com") == -1)):
                relative_uri = project_url[len("https://github.com"):]
                project_repo_url=GITHUB_REPO_URL_PREFIX+relative_uri
                print project_repo_url
                add_project(project_repo_url)
            
            
            

#methid not to be used as too time consuming

def list_github_load():
    fetch_github_data=True
    current_start=0
    incr_count=365
    print "Starting Github data dump in paginated format with each page ,365 repositories"
    while fetch_github_data :
        current_fetch_url=urljoin(GITHUB_REPO_URL , '?since='+str(current_start))
        current_fetch_res=requests.get(current_fetch_url, headers=headers_git)
        current_projects = current_fetch_res.json()
        contentLen = len(current_fetch_res.text)
        add_projects(current_projects)
        
        current_start=current_start+incr_count
        print "current start %d" , current_start
        if contentLen== 2 :
            fetch_github_data=False
        ##introduce sleep so as not to reach call limit
        time.sleep(30)
 

#load data based on search
def fetchandload_gitdata():    
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
          
          current_fetch_url = urljoin(GITHUB_REPO_SEARCH_URL, 'repositories?q=forks:>10&per_page=' + str(per_page_result_size) + '&page=' + str(current_page))
          print 'current_fetch_url is: ' + current_fetch_url
          current_page = current_page + 1
          current_fetch_res = requests.get(current_fetch_url, headers=headers)
          
          current_projects = current_fetch_res.json()
          add_projects(current_projects)
          
          
          time.sleep(30)
          

def add_project(project_url):
    collection = "projects"
    url = config['apiURL'] + config['database'] \
        +"/collections/"+ collection +"?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
        
    time.sleep(6)
    project_resp=requests.get(project_url, headers=headers_git)
    project_json=project_resp.json()
    if ("name" in project_json.keys()):
        print "Project fetched " , project_json["name"]
        score = getScore(project_json)     # add a rank
        project_json.update({'_score': score})
        project_json.update({'_rank': score})
        r = requests.post(url, data=json.dumps(project_json), headers=headers)
        ret = r.json()
        print "Project added =>" + project_json['name']



# Dummy ranker based on crude scoring 
def getScore(p):
    watchers =  p["watchers"] if "watchers" in p.keys() else 0
    openIssues = p["open_issues"] if "open_issues" in p.keys() else 0
    forks = p["forks"] if "forks" in p.keys() else 0
    stargazers = p["stargazers_count"] if "stargazers_count" in p.keys() else 0
    
    score = watchers + openIssues + forks + stargazers
    return score
 
if __name__ == '__main__':
    #list_github_load()
    read_github_load_file()
