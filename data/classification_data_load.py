#!/usr/bin/env python
# encoding: utf-8
'''
This file is part of OSSRank initiative

ClassificationDataLoad class is responsible for updating projects with classification attribute in OSSRank Repository


'''


import requests
import json
import sys
sys.path.insert(0, './../classifier')
from ProjectClassifier import classify_project
import requests
from urlparse import urljoin
import ConfigParser
from common_data_layer import DataLayer
import logging


class ClassificationDataLoad:

    logger=logging.getLogger("classification_loader_logger")
    
    config_reader = ConfigParser.ConfigParser()
    config = {
                'noOfProjectsPerLoadingUnit' : 0, 
                'loaderTimeInterval': 0, 
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
            self.config['noOfProjectsPerLoadingUnit'] = int(self.config_reader.get('ClassificationLoader', 'no_per_project_loading_unit' ))
            self.config['loaderTimeInterval'] = int(self.config_reader.get('ClassificationLoader', 'loader_time_interval' ))
            self.config['collectionProjects'] = self.config_reader.get('Mongolab', 'collection_project' )

         except ConfigParser.Error as e:
             raise Error(e) # should not continue in case of config error
             sys.exit(0)


    '''
     Return number of iteration cycles to perform while classifying all the projects in OSSRank Repository
    '''
    def    __getIterationCycles(self):
        
        classificationloader_logger = logging.getLogger("classification_loader_logger")
        
        classificationloader_logger.info("Calculating Number of iterations to be performed for classifying all projects in repository")
        classificationData = DataLayer()
        
        totalProjectsToClassify = classificationData.get_collectionlength_ossrank_repo(self.config['collectionProjects'])
        
        totalCycles= (totalProjectsToClassify/self.config['noOfProjectsPerLoadingUnit']) if (totalProjectsToClassify%self.config['noOfProjectsPerLoadingUnit'] == 0) else (totalProjectsToClassify/self.config['noOfProjectsPerLoadingUnit'] + 1)
        
        classificationloader_logger.debug('total iteration needed %d' ,   totalCycles)
        
        return totalCycles
     
     
    '''
     Get projects classification using OSSRank classification algorithm 
    '''
    def __getProjectCategory(self, project):
    
        getcategory_logger = logging.getLogger("classification_loader_logger")
        
        category = classify_project(project['name'], project ['description'], language=project ['language'])
        
        return category
    
        
        
    '''
     updateAllProjectWithClassification is the method to be invoked from external program to classifying all projects
    '''
    def updateAllProjectWithClassification(self):
       
        projectupdate_logger = logging.getLogger("classification_loader")
        
        projectupdate_logger.info("Staring Process for updating projects with classification")
        
        totalLoadCycles = self.__getIterationCycles()
        
        if(totalLoadCycles == 0):
            projectupdate_logger.info("No Projects to classify in OSSRank Repository")
            sys.exit(0)
        
        projectupdate_logger.info("No of cycles to perform to classify all projects in OSSRank Repository %d", totalLoadCycles )
        
        
        classificationData = DataLayer()
        
        currentResultLimit = int(self.config['noOfProjectsPerLoadingUnit'])
        
        for num in range(1,totalLoadCycles ):
            
           projects = classificationData.get_jsonobjects_from_ossrank_repo(self.config['collectionProjects'],str(currentResultLimit), str((num-1)*int(self.config['noOfProjectsPerLoadingUnit'])) )
           
           self.__processProjects(projects)
            
           currentResultLimit =  currentResultLimit + int(self.config['noOfProjectsPerLoadingUnit'])
           
           
         
            
        
        projectupdate_logger.info("Finishing Process for updating projects with classification")
        
        
    '''
     process projects and update them with category element & push update to OSSRank repo 
    '''
    def __processProjects(self, projects):
        
        processProject_logger = logging.getLogger("classification_loader")
        
        classificationData = DataLayer()
        
        for proj in projects :
            processProject_logger.info('Current project to process %s ', proj['full_name'])
            document_Id = proj['_id']
            object_id_repo= document_Id['$oid']
            proj.update({'_category':self.__getProjectCategory(proj)})
            classificationData.update_jsonobject_in_ossrank_repo( self.config['collectionProjects'],proj, object_id_repo )
            

if __name__ == '__main__':
    classificationLoad = ClassificationDataLoad()
    classificationLoad.updateAllProjectWithClassification()
