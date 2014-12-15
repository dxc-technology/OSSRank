import requests
import json

# Configuration
config = {
    'apiURL' : "https://api.mongolab.com/api/1/databases/",
    'apiKey' : "xxxxxxx",
    'database' : "ossrank"
}

# Get list of projects from Github
def getProjects():
    for page in range(1, 11):
        url = "https://api.github.com/search/repositories?q=forks%3A%22%3E+50%22&sort=stars&order=desc&page="+ str(page)
        r = requests.get(url)
        projects = r.json()
        addProjects(projects)
 
# Insert projects into MongoDB using REST API
def addProjects(projects):
    collection = "projects"
    url = config['apiURL'] + config['database'] \
        +"/collections/"+ collection +"?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    for p in projects['items']:
        score = getScore(p)     # add a rank
        p.update({'_rank': score})
        r = requests.post(url, data=json.dumps(p), headers=headers)
        ret = r.json()
        print ret

# Dummy ranker based on crude scoring 
def getScore(p):
    watchers =  p["watchers"] if "watchers" in p.keys() else 0
    openIssues = p["open_issues"] if "open_issues" in p.keys() else 0
    forks = p["forks"] if "forks" in p.keys() else 0
    stargazers = p["stargazers_count"] if "stargazers_count" in p.keys() else 0
    
    score = watchers + openIssues + forks + stargazers
    return score
 
if __name__ == '__main__':
    getProjects()
