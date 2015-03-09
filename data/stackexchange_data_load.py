import json
import stackexchange
import requests
import sys
import requests
import time
from urlparse import urljoin


# Configuration
config = {
    'apiURL' : "https://api.mongolab.com/api/1/databases/",
    'apiKey' : "HNkm0J4u8WLmYlAJvqetUmMcumzel9vO",
    'database' : "ossrank", 
    'collection': "projects"
}

#stackoverflow
s_exchange= stackexchange.Site(stackexchange.StackOverflow, app_key='HcSvRsRs4ys3mG2VfS30SA((', impose_throttling = True)

#mongolab url
query_url = config['apiURL'] + config['database'] +"/collections/"+ config['collection'] +"?l=1000&apiKey=" + config['apiKey']
headers = {'content-type': 'application/json'}

# Get list of projects from Github
def get_projects_mongolab():
    
     headers = {'content-type': 'application/json'}
     res = requests.get(query_url,headers=headers)
     projects = res.json()
     count = 0
     
     #iterate
     for p in projects:
        project = p
        
        #escape wrong data in mongo lab if there is no name no search possible
        if(not project.has_key('name')):
            continue
        
        print 'updating   ' + project['name']
        
        #find document id for update
        oid=project ['_id']
        document_id = oid['$oid']
        #get stackoverflow result
        
        project_name=project['name']
        project_name_alnum=get_alaphanumeric_string(project_name)
        
        #does project name contains special char search with or without
        #modify it to search similar name -- todo
        
        if(project_name is project_name_alnum ):
            stack_tag_total = search_for_tag(project['name'])
            stack_intitle_total = search_in_title(project['name'])
        else:
            stack_tag_total = search_for_tag(project['name'])+search_for_tag(project_name_alnum)
            stack_intitle_total = search_in_title(project['name'])+ search_in_title(project_name_alnum)
            
        #update json with stackexchange data
        today=time.strftime("%d.%m.%Y")
        stack_exchange_todays_dict={'added_at':today,'questions':stack_intitle_total, 'tagged_dicsussion':stack_tag_total}
        
        if(project.has_key('stackoverflow')):
            stack_exchange_data=project['stack_overflow']
            stack_exchange_data.update(stack_exchange_todays_dict)
        else:
            project.update({'_stackoverflow':stack_exchange_todays_dict})
        
        
        count = count +1
        print stack_exchange_todays_dict
        update_projects(project, document_id)
        

#removes special character to do a similarity search
def get_alaphanumeric_string(project_name):
    if(not project_name.isalnum()):
        new_name= ''.join(e for e in project_name if e.isalnum())
        print new_name
        return new_name
    else:
        return project_name

def search_for_tag(project_name):
    
    qs=s_exchange.search(tagged=project_name, filter='total')
    print('Searching in tagged for %s...'% (project_name))
    print qs.total
    return qs.total;

def search_in_title(project_name):
    
    qs=s_exchange.search(intitle=project_name, filter='total')
    print('Searching in title for %s...'% (project_name))
    print qs.total
    return qs.total;

    
# update projects into MongoDB using REST API
def update_projects(project, document_id):
    url = config['apiURL'] + config['database'] +"/collections/"+ config['collection']+"/" + document_id +"?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r= requests.put(url, data=json.dumps(project), headers=headers)
    ret = r.json()
    print ret



if __name__ == '__main__':
    #search_for('bootstrap')
    get_projects_mongolab()
    
