#!/usr/bin/env python
# encoding: utf-8
'''
This file is part of OSSRank initiative

DataLoader is responsible for pushing data to any database that OSSRank choose to use 
Current implementation is geared towards document oriented database/specifically mongodb

All other classes that is loading a specific collection should use this class
with the specific collection name and a json object
'''

import requests
import json
from urlparse import urljoin
import simplejson
import logging
import ConfigParser
import sys

class DataLayer:
    
    logger=logging.getLogger("datalayer_logger")
    
    config_reader = ConfigParser.ConfigParser()
    config = {
                'apiURL' : '',
                'api_key' : '', 
                'database':''
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
            self.config['apiURL'] = self.config_reader.get('Mongolab', 'apiURL' )
            self.config['api_key'] = self.config_reader.get('Mongolab', 'apiKey' )
            self.config['database'] = self.config_reader.get('Mongolab', 'database' )
         except ConfigParser.Error as e:
             raise Error(e) # should not continue in case of config error
             sys.exit(0)
             

        
        
        
    

    '''
     update_jsonobject_in_ossrank_repo updates a specific json object in a collection   
    '''
    @classmethod
    def update_jsonobject_in_ossrank_repo(self , collection_name,jsonObject, object_id ):
        
        dataloader_logger = logging.getLogger("datalayer_logger")
        
        dataloader_logger.debug("updating collection ," + collection_name.strip())
         
        if not collection_name.strip():
             raise ValueError('A Specific collection name needs to be specified')
        
        url = self.config['apiURL'] + self.config['database'] \
        +"/collections/"+ collection_name +"/"+ object_id +"?apiKey=" + self.config['api_key']
        
        headers = {'content-type': 'application/json'}
    
        #update the data in repository
        try:
            r = requests.put(url, data=json.dumps(jsonObject), headers=headers)
            ret = r.json()
            dataloader_logger.debug(ret)
        except requests.exceptions.RequestException as e:
            dataloader_logger.error(e)
    
    '''
     get_jsonobjects_from_ossrank_repo returns a set of projects in json format by querying OSSRank repository
     result_limit parameter is used to determine to specify number of results the query should eturn
     numebrs_to_skip is used to specify to limit the number of results in resultset
     The use of this method is to iterate over a large document database
      e.g. for a db with 10000 object
             it can iterate in a list in batch of 1000
             first call will be
             get_jsonobjects_from_ossrank_repo( "collection_x",1000, 0 )
             next
             get_jsonobjects_from_ossrank_repo( "collection_x",2000, 1000 )
             so on...
    '''
    @classmethod
    def get_jsonobjects_from_ossrank_repo(self , collection_name,result_limit, numbers_to_skip ):
        dataloader_logger = logging.getLogger("datalayer_logger")
        
        dataloader_logger.debug("updating collection ," + collection_name.strip())
         
        if not collection_name.strip():
             raise ValueError('A Specific collection name needs to be specified')
        
        url = self.config['apiURL'] + self.config['database'] \
        +"/collections/"+ collection_name +"?sk="+numbers_to_skip+"&l="+result_limit+"&apiKey=" + self.config['api_key']
        
        headers = {'content-type': 'application/json'}
        
        #get the collection
        try:
            r = requests.get(url, headers=headers)
            objects = r.json()
            #dataloader_logger.debug(objectCount)
            return objects
        except requests.exceptions.RequestException as e:
            dataloader_logger.error(e)
            raise e

    
    '''
     get_collectionlength_ossrank_repo returns number of objects in a specific collection
    '''
    @classmethod
    def get_collectionlength_ossrank_repo(self , collection_name):
        dataloader_logger = logging.getLogger("datalayer_logger")
        
        dataloader_logger.debug("Checking collection length ," + collection_name.strip())
         
        if not collection_name.strip():
             raise ValueError('A Specific collection name needs to be specified')
        
        url = self.config['apiURL'] + self.config['database'] \
        +"/collections/"+ collection_name +"?c=true&apiKey=" + self.config['api_key']
        
        headers = {'content-type': 'application/json'}
        
        #query collection to fetch the numbers
        try:
            r = requests.get(url, headers=headers)
            objectCount = r.json()
            dataloader_logger.debug(objectCount)
            return objectCount
        except requests.exceptions.RequestException as e:
            dataloader_logger.error(e)
            raise e

    
