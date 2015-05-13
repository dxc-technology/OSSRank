import requests
import json
import sys
sys.path.insert(0, './../classifier')
from ProjectClassifier import classify_project
import requests
from urlparse import urljoin
import ConfigParser
from common_data_layer import DataLayer


class ClassificationDataLoad:

    logger=logging.getLogger("classification_loader_logger")
    
    config_reader = ConfigParser.ConfigParser()
    config = {
                'noOfProjectsPerLoadingUnit' : '', 
                'loaderTimeInterval':'', 
                'collectionProjects':''
              }
    
    def __init__(self):
        
         #initialize logger fully
         self.logger.setLevel(logging.DEBUG)
         this_logger_handler=logging.StreamHandler()
         this_logger_format= logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
         this_logger_handler.setFormatter(this_logger_format)
         self.logger.addHandler(this_logger_handler)
         
         #load configuration
         try:
            self.config_reader.read('config.cfg')
            self.config['noOfProjectsPerLoadingUnit'] = self.config_reader.get('ClassificationLoader', 'no_per_project_loading_unit' )
            self.config['loaderTimeInterval'] = self.config_reader.get('ClassificationLoader', 'loader_time_interval' )
            self.config['collectionProjects'] = self.config_reader.get('Mongolab', 'collection_project' )

         except ConfigParser.Error as e:
             raise Error(e) # should not continue in case of config error
             sys.exit(0)


    '''
     It is intended to perform classification of project in a number of 
    '''
    def    _getIterationCycles(self):
        
        classificationloader_logger = logging.getLogger("classification_loader_logger")
        
        classificationloader_logger.info("Calculating Number of iterations to be performed for classifying all projects in repository")
        classificationData = DataLayer()
        
        totalProjectsToClassify = classificationData.get_collectionlength_ossrank_repo(self.config['collectionProjects'])
        
        totalCycles= (totalProjectsToClassify/self.config['noOfProjectsPerLoadingUnit']) if (totalProjectsToClassify%self.config['noOfProjectsPerLoadingUnit'] == 0) else (totalProjectsToClassify/self.config['noOfProjectsPerLoadingUnit'] + 1)
        
        classificationloader_logger.debug('total iteration count',  totalCycles)
        
        return totalCycles
     
        
    def _get_projects_category(project):
    
     print "project language" , project ['language']
     category = classify_project(project['name'], project ['description'], language=project ['language'])
        
     return category

# Get list of projects from Github
def get_projects_mongolab():
    
     headers = {'content-type': 'application/json'}
     #res = requests.get(query_url,headers=headers)
     #projects = res.json()
     count = 800
     
     classificationData = DataLayer()
     
     classificationData.get_collectionlength_ossrank_repo("projects")
     ''''
     #print projects
     for p in projects:
        count = count +1
        project = p
        print 'updating   ' + project['full_name']
        oid=project ['_id']
        document_id = oid['$oid']
        ##get category
        project_category = get_projects_category(project)
        ##update json
        project.update({'_category':project_category})
        
        #update_projects(project, document_id)
        classificationData.update_jsonobject_in_ossrank_repo( "projects", project , document_id )
     '''  
        
        
        


if __name__ == '__main__':
    get_projects_mongolab()
