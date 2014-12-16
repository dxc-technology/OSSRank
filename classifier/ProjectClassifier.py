#!/usr/bin/env python
# encoding: utf-8
'''
project classifier class
'''

import json
import requests
from urlparse import urljoin
import nltk.classify
from nltk.tokenize  import wordpunct_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus  import stopwords
from nltk import NaiveBayesClassifier
from QueryOpenHub import queryOpenhubDetails
import os
import re
import numpy as npy
from collections import defaultdict




SOFTWARE_CATEGORY_FILE_NAME='SoftwareCategory.json'

OPEN_SOURCE_CORPORA_DIR='software_category_corpora'

'''
Read our category definition json file and 
get the best match from keywords and return category
if none return category others
'''
def get_category_best_keyword_match(desc_key_set):
    data =''
    current_match=''
    
    with open('./../classifier/'+SOFTWARE_CATEGORY_FILE_NAME) as f:
        json_data= json.load(f)
        best_feature_match=0
        
    for categories in json_data['softwareCategories']:
            category_name= categories['name'] 
            keyword_set= set(categories['keyWords']) 
            matched_feature=keyword_set.intersection(desc_key_set)
            current_feature_match=len(matched_feature)
            if((current_feature_match>best_feature_match) and (current_feature_match>0) ):
                best_feature_match=current_feature_match
                current_match=category_name if (current_match == '') else (current_match + ' , '+category_name )
    if (current_match == ''):
        current_match= 'undefined category'
    return current_match


def get_desc_words(software_desc, stopwords=[]):
    #use wordpunct_tokenize not to split on underscores
    #we  have some keyword or tags that contains with underscore
    #however we want to remove \n if newline exists
    
    if (software_desc is None):
        return 'undefined'

    desc_words=set(wordpunct_tokenize(software_desc.replace('\n', '').lower()))
    
    #get rid of stopwords if there is any
    desc_words = desc_words.difference(stopwords)
    #we need to get rid punctuation token , numbers and single letters
    desc_words = [w for w in desc_words if re.search('[a-zA-Z]', w) and len(w)>1]
    
    return desc_words

'''
thanks ipython.org for the method
creates a dictiornary of entries {word:true} for every unique word in desc
**kargs are options to the word set creator get_desc_words defined above
'''
def word_indicator(desc, **kwargs):
    features =defaultdict(list)
    desc_words=get_desc_words(desc, **kwargs)
    for w in desc_words:
        #print w
        features[w]=True
    #print features
    return features


def features_from_desc(descs, label, feature_extractor, **kwargs):
    '''
    Make a (features, label) tuple for each desc in a list of a certain,
    label of desc ('webapp', 'data',....) and return a list of these tuples.

    
    '''
    features_labels = []
    #features_labels = set()
    for desc in descs:
        
        features = feature_extractor(desc, **kwargs)
        features_labels.append((features, label))
    return features_labels


def get_corpora(path):
    '''
    Read in the corpora in a specific path

    Returns a string.
    '''
    desc = ''
    with open(path, 'rU') as con:
        desc = con.read().replace('\n', '')
        
    return desc 
    


def get_naive_base_classified_result(evalutaing_desc):
    
    #define stopwords to use
    swords=stopwords.words('english')
    swords.extend(['last', 'first', 'different', 'new', 'include', 'use', 'full'])
    
    #get corpora and train
    corpora_data_path=os.path.abspath(os.path.join('./../classifier/', OPEN_SOURCE_CORPORA_DIR))
    
    #build automation
    build_automation_corpora_path=os.path.join(corpora_data_path, 'buildautomation.txt')
    train_build_automation_txt=get_desc_words(get_corpora(build_automation_corpora_path))
    train_build_automation = features_from_desc(train_build_automation_txt, 'build_automation', word_indicator, stopwords = swords)
    
    #train webapp corpora
    webapp_corpora_path=os.path.join(corpora_data_path, 'webapplicationframework.txt')
    train_webapp_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_webapp = features_from_desc(train_webapp_txt, 'webapp', word_indicator, stopwords = swords)
    
    #train content management corpora
    cms_corpora_path=os.path.join(corpora_data_path, 'contentmanagementsystem.txt')
    train_cms_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_cms = features_from_desc(train_webapp_txt, 'cms', word_indicator, stopwords = swords)

    #train db corpora
    db_corpora_path=os.path.join(corpora_data_path, 'database.txt')
    train_db_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_db = features_from_desc(train_webapp_txt, 'db', word_indicator, stopwords = swords)

    #train httpmodule corpora
    http_corpora_path=os.path.join(corpora_data_path, 'httpmodule_apache.txt')
    train_http_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_http = features_from_desc(train_webapp_txt, 'httpmodule', word_indicator, stopwords = swords)
    
    #train mobile api corpora
    mobile_corpora_path=os.path.join(corpora_data_path, 'mobileapi_java.txt')
    train_mobile_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_mobile = features_from_desc(train_webapp_txt, 'mobile', word_indicator, stopwords = swords)
    
    #train ide corpora
    ide_corpora_path=os.path.join(corpora_data_path, 'ide.txt')
    train_ide_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_ide = features_from_desc(train_webapp_txt, 'ide', word_indicator, stopwords = swords)

    ##collect all trained set
    train_set=  train_build_automation + train_webapp + train_cms + train_db + train_http + train_mobile + train_ide
    classifier = NaiveBayesClassifier.train(train_set)
    
    
    eval_words=dict([(word, True)for word in evalutaing_desc])
    
    #get classification
    category_naive_classification= classifier.classify(eval_words)
    print 'category as per naive bayes classification ->'+ category_naive_classification
    
    

'''
This method classifies a git project using nltk and categorizes 
in one of the available categories
algorithm is described below : to be improved
algo desc:
get project desc from github
tokenize using nltk
get project desc and tags from openhub
match against software category keyword
toadd :first improvement check related project verify categories

the algo is following
get description from git + openhub
do word tokenize
match against our own softwrae category keywords
if tags available in openhub match against softwrae category keywords
do a supervsed classification of description against our own corpora out of wikipedia
ProjectCategory = (finding keywords in desc) + (matching keywords in found tags) + (naive bayes classification using trained defintion out of wikipedia)
what weight each one carry :: to be decided
'''
def classify_project(git_project_name, project_description):
       print ' classifying '+ git_project_name
       category=''
       #word tokenize using nltk and match against keywords from softwarecategory
       current_desc_words=get_desc_words(project_description)
       category= get_category_best_keyword_match(current_desc_words)
       print ' best category match as per git desc ->' + category
    
       #now we get keyword from openhub if exists
       
       test_project_dict= queryOpenhubDetails(git_project_name)
       if(len(test_project_dict) != 1 and len(test_project_dict) != 0 ):
           project_tags=test_project_dict.get('tag')
           current_tag_words=get_desc_words(project_tags)
           category_openhub_tag= get_category_best_keyword_match(current_tag_words)
           print ' best category match as per openhub tag ->' + category_openhub_tag
           if(category_openhub_tag != category):
            category=category+ ','+ category_openhub_tag 
           
       
       #naive base classifier to be improved further
       get_naive_base_classified_result(current_desc_words)
         
       return category
       
def main():
    print 'test in main'
    classify_project('bootstrap', 'The most popular front-end framework for developing responsive, mobile first projects on the web.')
    
    
if  __name__=='__main__':
    main()
    
