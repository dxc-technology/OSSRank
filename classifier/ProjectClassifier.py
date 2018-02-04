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
from classifier.QueryOpenHub import queryOpenhubDetails
import os
import re
import numpy as npy
from collections import defaultdict
import logging
from sys import path
from os import getcwd




'''
 global logging definition
'''

this_logger=logging.getLogger("classifier_logger")

this_logger.setLevel(logging.DEBUG)

this_logger_handler=logging.StreamHandler()

this_logger_format= logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

this_logger_handler.setFormatter(this_logger_format)

this_logger.addHandler(this_logger_handler)




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

    print getcwd()
    with open(getcwd() +'/classifier/'+SOFTWARE_CATEGORY_FILE_NAME) as f:
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
        current_match= 'unknown category'
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
creates a dictiornary of entries {word:true} for every unique word in desc
**kwargs are options to the word set creator get_desc_words defined above
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

'''
function doing  supervised naive bayes classification
training set is in software_category_corpora
text to classify is provided as method parameter
'''

def get_naive_base_classified_result(evaluating_desc_str):


    naivebayes_logger = logging.getLogger("classifier_logger");

    evaluating_desc=get_desc_words(evaluating_desc_str)

    #define stopwords to use
    swords=stopwords.words('english')
    swords.extend(['free','whose','using','used','last','software',  'first', 'different', 'most', 'and','contain', 'multiple','new', 'include', 'use', 'full' , 'project', 'comparison'])

    #get corpora and train
    corpora_data_path=os.path.abspath(os.path.join(getcwd()+'/classifier/',
                                                   OPEN_SOURCE_CORPORA_DIR))

    #build automation
    build_automation_corpora_path=os.path.join(corpora_data_path, 'buildautomation.txt')
    train_build_automation_txt=get_desc_words(get_corpora(build_automation_corpora_path))
    train_build_automation = features_from_desc(train_build_automation_txt, 'Build Management tools', word_indicator, stopwords = swords)

    #train webapp corpora
    webapp_corpora_path=os.path.join(corpora_data_path, 'webapplicationframework.txt')
    train_webapp_txt=get_desc_words(get_corpora(webapp_corpora_path))
    train_webapp = features_from_desc(train_webapp_txt, 'Web Application Framework', word_indicator, stopwords = swords)

    #train content management corpora
    cms_corpora_path=os.path.join(corpora_data_path, 'contentmanagementsystem.txt')
    train_cms_txt=get_desc_words(get_corpora(cms_corpora_path))
    train_cms = features_from_desc(train_cms_txt, 'Content Management Systems', word_indicator, stopwords = swords)

    #train db corpora
    db_corpora_path=os.path.join(corpora_data_path, 'database.txt')
    train_db_txt=get_desc_words(get_corpora(db_corpora_path))
    train_db = features_from_desc(train_db_txt, 'Database', word_indicator, stopwords = swords)

    #train httpmodule corpora
    http_corpora_path=os.path.join(corpora_data_path, 'httpmodule_apache.txt')
    train_http_txt=get_desc_words(get_corpora(http_corpora_path))
    train_http = features_from_desc(train_http_txt, 'HTTP Modules', word_indicator, stopwords = swords)

    #train mobile api corpora
    mobile_corpora_path=os.path.join(corpora_data_path, 'mobileapi_java.txt')
    train_mobile_txt=get_desc_words(get_corpora(mobile_corpora_path))
    train_mobile = features_from_desc(train_mobile_txt, 'Mobile API', word_indicator, stopwords = swords)

    #train mobile api corpora
    javascript_corpora_path=os.path.join(corpora_data_path, 'javascript.txt')
    train_javascript_txt=get_desc_words(get_corpora(javascript_corpora_path))
    train_javascript = features_from_desc(train_javascript_txt, 'JavaScript Libraries', word_indicator, stopwords = swords)


    #train ide corpora
    ide_corpora_path=os.path.join(corpora_data_path, 'ide.txt')
    train_ide_txt=get_desc_words(get_corpora(ide_corpora_path))
    train_ide = features_from_desc(train_ide_txt, 'IDE', word_indicator, stopwords = swords)

    #train scm corpora
    scm_corpora_path=os.path.join(corpora_data_path, 'scm.txt')
    train_scm_txt=get_desc_words(get_corpora(scm_corpora_path))
    train_scm = features_from_desc(train_scm_txt, 'SCM', word_indicator, stopwords = swords)

    #train scm corpora
    css_corpora_path=os.path.join(corpora_data_path, 'css.txt')
    train_css_txt=get_desc_words(get_corpora(css_corpora_path))
    train_css = features_from_desc(train_css_txt, 'CSS', word_indicator, stopwords = swords)


    ##collect all trained set
    train_set= train_css + train_javascript + train_build_automation + train_webapp + train_cms + train_db + train_http + train_mobile + train_ide+ train_scm
    classifier = NaiveBayesClassifier.train(train_set)

    '''
    remove the stopwords first from text to be classified
    '''
    text_to_classify = [w for w in evaluating_desc if not w in stopwords.words('english')]

    #print text_to_classify

    eval_words=dict([(word, True)for word in text_to_classify])

    #print eval_words

    #get classification
    category_naive_classification= classifier.classify(eval_words)

    naivebayes_logger.debug('category as per naive bayes classification ' + category_naive_classification)

    #below line to uncommented for debug purpose only
    #classifier.show_most_informative_features()

    return category_naive_classification


'''
The function take project name and arbitrary number of relevant keywords arguments

This method classifies a git project using nltk and categorizes to one of the
available category in SoftwareCategory.json which is our master taxonomy

algorithm :

get project desc from github and any other relevant parameters (in key value format)
tokenize using nltk
1.get project desc and tags from openhub
    match against software category keyword

2.get description from git + openhub
  do word tokenize
   match against our own softwrae category keywords
   if tags available in openhub match against softwrae category keywords
3. do a supervsed classification of description against our own corpora out of wikipedia

ProjectCategory = (finding keywords in desc) + (matching keywords in found tags) + (naive bayes classification using trained defintion out of wikipedia)
what weight each one carry :: to be decided
'''
def classify_project(project_name, project_description, **kwargs):
       classifier_logger = logging.getLogger("classifier_logger");

       classifier_logger.info(' classifying '+ project_name )

       project_desc = project_description if  project_description is not None else ''

       category=''

       project_language = ''
       for key, value in kwargs.iteritems():
           if('language' in key):
               project_language = value if value is not None else ''

       '''
        concatenate project name, description ,language for classification
        we use all three information together
       '''
       project_data = project_name + " " + project_desc + " " + project_language

       '''
        word tokenize using nltk and match against keywords from softwarecategory
       '''
       current_desc_words=get_desc_words(project_data)

       #classifier_logger.debug(current_desc_words)

       category= get_category_best_keyword_match(current_desc_words)

       classifier_logger.info(' best category match as per git desc ' + category )

       #now we get keyword from openhub if exists

       test_project_dict= queryOpenhubDetails(project_name)
       if(len(test_project_dict) != 1 and len(test_project_dict) != 0 ):
           project_tags=test_project_dict.get('tag')
           current_tag_words=get_desc_words(project_tags)
           category_openhub_tag= get_category_best_keyword_match(current_tag_words)
           classifier_logger.info(' best category match as per openhub tag ' + category_openhub_tag )
           if(category_openhub_tag != category and category_openhub_tag != 'unknown category'):
            category=category+ ','+ category_openhub_tag


       #naive base classifier to be improved further
       get_naive_base_classified_result(project_data)

       return category

def main():
    print 'test in main'
    #classify_project('bootstrap', 'The most popular HTML , CSS , and JavaScript framework for developing responsive, mobile first projects on the web.', language='CSS')
    #classify_project('node', 'evented I/O for v8 javascript', language='JavaScript')
    #classify_project('Almofire', 'Elegant HTTP Networking in Swift', language='Swift')
    #classify_project('Atom', 'The Hackable editor.', language='CofeeScript')

if  __name__=='__main__':
    main()
