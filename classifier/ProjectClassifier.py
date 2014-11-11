'''
Project classifier class
'''
import json
import nltk.classify
from nltk.tokenize  import wordpunct_tokenize
from nltk.corpus  import stopwords
from nltk import NaiveBayesClassifier
from QueryOpenHub import queryOpenhubDetails
import os
import re
from collections import defaultdict

SOFTWARE_CATEGORY_FILE_NAME='SoftwareCategory.json'
OPEN_SOURCE_CORPORA_DIR='software_category_corpora'

'''
Read our category definition json file and 
get the best match from keywords and return category
if none return category others
'''
def get_category_best_keyword_match(desc_key_set):
    current_match=''
    with open('./' + SOFTWARE_CATEGORY_FILE_NAME) as f:
        json_data= json.load(f)
        best_feature_match=0
        
    for categories in json_data['softwareCategories']:
            category_name= categories['name'] 
            keyword_set= set(categories['keyWords']) 
            matched_feature=keyword_set.intersection(desc_key_set)
            current_feature_match=len(matched_feature)
            
            if((current_feature_match > best_feature_match) and (current_feature_match > 0) ):
                best_feature_match=current_feature_match
                current_match=category_name if (current_match == '') else (current_match + ' , ' + category_name )
    if (current_match == ''):
        current_match= 'undefined category'
    return current_match


def get_desc_words(software_desc, stopwords=[]):
    #use wordpunct_tokenize not to split on underscores
    #we  have some keyword or tags that contains with underscore
    #however we want to remove \n if newline exists
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
        features[w]=True
    return features


def features_from_desc(descs, label, feature_extractor, **kwargs):
    '''
    Make a (features, label) tuple for each desc in a list of a certain,
    label of desc ('webapp', 'data',....) and return a list of these tuples.

    '''
    features_labels = []
    for desc in descs:
        features = feature_extractor(desc, **kwargs)
        features_labels.append((features, label))
    return features_labels

def get_corpora(path):
    '''
    Read in the corpora in a specific path

    Returns a string.
    '''
    with open(path, 'rU') as con:
        desc = con.readlines()
        first_blank_index = desc.index('\n')
        desc = desc[(first_blank_index + 1): ]
        return ''.join(desc) 
    
def get_naive_base_classified_result(evalutaing_desc):
    #define stopwords to use
    swords=stopwords.words('english')
    swords.extend(['last', 'first']) 
    test_desc= features_from_desc(evalutaing_desc, 'testset', word_indicator, stopwords = swords)
    
    #get corpora and train
    corpora_data_path=os.path.abspath(os.path.join('.', OPEN_SOURCE_CORPORA_DIR))
    
    #build automation
    build_automation_corpora_path = os.path.join(corpora_data_path, 'buildautomation.txt')
    train_build_automation_txt = get_corpora(build_automation_corpora_path)
    train_build_automation = features_from_desc(train_build_automation_txt, 'build_automation', word_indicator, stopwords = swords)
    
    #train webapp corpora
    webapp_corpora_path=os.path.join(corpora_data_path, 'webapplicationframework.txt')
    train_webapp_txt=get_corpora(webapp_corpora_path)
    train_webapp = features_from_desc(train_webapp_txt, 'webapp', word_indicator, stopwords = swords)
    
    train_set= train_build_automation+train_webapp
    classifier = NaiveBayesClassifier.train(train_set)
    #print 'Test accuracy for '  
    print  nltk.classify.accuracy(classifier,test_desc)
   
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
             
       #naive base classifier to be improved before it can be used -algo to be correcetd
       #get_naive_base_classified_result(current_desc_words)
       return category
    
