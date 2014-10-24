import requests
import json
 
# Get list of projects from Github
def getProjects():
url = "https://api.github.com/search/repositories?q=forks%3A%22%3E+100%22&sort=stars&order=desc"
r = requests.get(url)
projects = r.json()
return projects
 
# Insert projects into MongoDB using REST API
def addProjects(projects):
apiKey = "HNkm0J4u8WLmYlAJvqetUmMcumzel9vO"
database = "ossrank"
collection = "projects"
url = "https://api.mongolab.com/api/1/databases/"+ database \
+"/collections/"+ collection +"?apiKey=" + apiKey
headers = {'content-type': 'application/json'}
for p in projects['items']:
r = requests.post(url, data=json.dumps(p), headers=headers)
ret = r.json()
print ret
 
if __name__ == '__main__':
projects = getProjects()
addProjects(projects)
