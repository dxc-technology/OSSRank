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
     #print projects
     for p in projects:
        project = p
        
        #escape wrong data
        if(not project.has_key('name')):
            continue
        print 'updating   ' + project['name']
        
        oid=project ['_id']
        document_id = oid['$oid']
        ##get category
        stack_tag_total = search_for_tag(project['name'])
        stack_intitle_total = search_in_title(project['name'])
        ##update json with stackexchange data
        today=time.strftime("%d.%m.%Y")
        stack_exchange_todays_dict={'added_at':today,'questions':stack_intitle_total, 'tagged_dicsussion':stack_tag_total}
        
        if(project.has_key('stackoverflow')):
            stack_exchange_data=project['stack_overflow']
            stack_exchange_data.update(stack_exchange_todays_dict)
        else:
            project.update({'_stackoverflow':stack_exchange_todays_dict})
        
        
        count = count +1
        print stack_exchange_todays_dict
        #update_projects(project, document_id)
        if(count==10): 
            break
        





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
