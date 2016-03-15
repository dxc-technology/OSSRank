#!/usr/bin/env python
import webapp2
import tweepy
import ConfigParser
from tweepy import *
from time import ctime, gmtime, mktime, strftime
import datetime
import requests
import json
from flask import jsonify

class TwitterHandler(webapp2.RequestHandler):
    def runTwitterLoad(self):
        config = ConfigParser.RawConfigParser()
        config.read('settings.cfg')

        # http://dev.twitter.com/apps/myappid
        CONSUMER_KEY = config.get('Twitter', 'CONSUMER_KEY')
        CONSUMER_SECRET = config.get('Twitter', 'CONSUMER_SECRET')
        # http://dev.twitter.com/apps/myappid/my_token
        ACCESS_TOKEN_KEY = config.get('Twitter', 'ACCESS_TOKEN_KEY')
        ACCESS_TOKEN_SECRET = config.get('Twitter', 'ACCESS_TOKEN_SECRET')

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        # If the authentication was successful, you should
        # see the name of the account print out
        Iam = api.me().name
        #print Iam
        
        # get Projects
        projects = getProjects(config)
        self.response.write("Num projects : " + str(len(projects)) + "<br/>")
        
        # Search for projects
        self.searchOSS(api, config, projects)

    def searchOSS(self, api, config, projects):
        # Grab API keys
        apiURL = config.get('Mongolab', 'apiURL')
        apiKey = config.get('Mongolab', 'apiKey')
        database = config.get('Mongolab', 'database')

        # Set API call headers
        headers = {'content-type': 'application/json'}
        
        # Set start date for stats
        startDate = getStartDate(config)
        print "START DATE :: " + startDate

        # Set number of projects per run
        projectsPerRun = config.get('OSSRank', 'PROJECTS_PER_RUN')
        #projectsPerRun = 2
        i = 0
        for p in projects:
            theID = p["_id"]["$oid"]    # Project ID in mongoDB
            term = "#" + p['name']      # Create hashtag from project name
            #term = "#nodejs"
            self.response.write(term + " : ")
            j = 0
            projectTweets = 0;
            for page in tweepy.Cursor(api.search, q=term, count=100, since=startDate).pages():
                projectTweets += len(page)
                j = j + 1
                if j > 10:  # Max of ten pages, 1000 tweets per period
                    break
            self.response.write(projectTweets)
            self.response.write("<br/>")
            i = i + 1
            if i > projectsPerRun:
                break
            
            # Update project entry in mongolab with PUT
            stats = {startDate : projectTweets} # stats for period
            # Look for existing _twitter element and add if necessary
            if '_twitter' in p:
                p['_twitter'].update(stats)
            else:
                p['_twitter'] = stats

            url = apiURL + database +"/collections/projects/"+ theID +"?apiKey=" + apiKey 
            print url
            r = requests.put(url, data=json.dumps(p), headers=headers)
            ret = r.json()
            print ret

            
    def log(self, message):
        timestamp = strftime("%Y %b %d %H:%M:%S UTC: ", gmtime())
        print (timestamp + message + '\n')
    
    def get(self):
        try:
            self.runTwitterLoad()
            print("Ran TwitterLoad")
        except TweepError as te:
            print te.message

def getProjects(config):
    apiURL = config.get('Mongolab', 'apiURL')
    apiKey = config.get('Mongolab', 'apiKey')
    database = config.get('Mongolab', 'database')
    # Get start date for stats
    startDate = getStartDate(config)

    # Set number of projects per run
    projectsPerRun = config.get('OSSRank', 'PROJECTS_PER_RUN')

    # Get twitter stats from start date
    url = apiURL + database +"/collections/projects?apiKey=" + apiKey + '&sk=0' + \
                      '&q={"_twitter.' + startDate + '": {$exists: false}}&l=' + projectsPerRun
    print url
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    return r.json()

def getStartDate(config):
    # Set number of projects per run
    searchDays = int(config.get('OSSRank', 'SEARCH_DAYS'))
    startDate = datetime.date.fromordinal(datetime.date.today().toordinal()-searchDays) 
    startDate = str(startDate)
    return startDate

    

app = webapp2.WSGIApplication([
    ('/twitterload', TwitterHandler)
], debug=False)
