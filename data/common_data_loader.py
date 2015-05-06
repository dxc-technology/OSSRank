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
import config

class DataLoader:
    
    logger=logging.getLogger("dataloader_logger")
    
    config_reader = ConfigParser.ConfigParser()
    

    
    def __init__(self):
        
         #initialize logger fully
         self.logger.setLevel(logging.DEBUG)
         self.logger_handler=logging.StreamHandler()
         self.logger_format= logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
         self.logger_handler.setFormatter(this_logger_format)
         self.logger.addHandler(this_logger_handler)
         
         #load configuration
         self.config_reader.read('config.cfg')
         self.config = {
                'apiURL' : self.config_reader.get('Mongolab', 'apiURL' ),
                'api_key' : self.config_reader.get('Mongolab', 'apiKey'), 
                'database':self.config_reader.get('Mongolab', 'database')
            }

        
        
        
    


    @classmethod
    def push_jsonobject_to_ossrank_repo(collection_name,jsonObject ):
        
        dataloader_logger = logging.getLogger("dataloader_logger");
       
        if('' in collection_name.strip()):
             raise ValueError('A Specific collection name needs to be specified')
        
        url = config['apiURL'] + config['database'] \
        +"/collections/"+ collection_name +"?apiKey=" + config['apiKey']
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(category), headers=headers)
        ret = r.json()
        dataloader_logger.debug(ret)

 
