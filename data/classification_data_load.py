import requests
import json
import sys
sys.path.insert(0, './../classifier')
from ProjectClassifier import classify_project
import requests
from urlparse import urljoin



# Configuration
config = {
    'apiURL' : "https://api.mongolab.com/api/1/databases/",
    'apiKey' : "HNkm0J4u8WLmYlAJvqetUmMcumzel9vO",
    'database' : "ossrank", 
    'collection': "projects"
}

query_url = config['apiURL'] + config['database'] +"/collections/"+ config['collection'] +"?l=1000&apiKey=" + config['apiKey']
headers = {'content-type': 'application/json'}

# Get list of projects from Github
def get_projects_mongolab():
    
     headers = {'content-type': 'application/json'}
     res = requests.get(query_url,headers=headers)
     projects = res.json()
     count = 0
     #print projects
     for p in projects:
        project = p
        print 'updating   ' + project['full_name']
        oid=project ['_id']
        document_id = oid['$oid']
        ##get category
        project_category = get_projects_category(project)
        ##update json
        project.update({'_category':project_category})
        count = count +1
        update_projects(project, document_id)
        
        
        
# update projects into MongoDB using REST API
def update_projects(project, document_id):
    url = config['apiURL'] + config['database'] +"/collections/"+ config['collection']+"/" + document_id +"?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r= requests.put(url, data=json.dumps(project), headers=headers)
    ret = r.json()
    print ret

def get_projects_category(project):
     
     category = classify_project(project['name'], project ['description'])
        
     return category

if __name__ == '__main__':
    get_projects_mongolab()
