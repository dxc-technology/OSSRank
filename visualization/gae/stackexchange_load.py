#!/usr/bin/env python
import webapp2
import stackexchange
import ConfigParser
from time import ctime, gmtime, mktime, strftime
import time
import datetime
import requests
import json
from flask import jsonify

class StackExchangeHandler(webapp2.RequestHandler):
	def get(self):
			try:
				self.runStackExchangeLoad()
			except NameError as ne:
				print ne.message
	
	def runStackExchangeLoad(self):
		
		 # Parse settings.cfg Configuration File
		 config = ConfigParser.RawConfigParser()
		 config.read('settings.cfg')

		 # Read StackExchange Configuration Keys
		 CLIENT_ID = config.get('StackExchange', 'client_id')
		 CLIENT_SECRET = config.get('StackExchange', 'client_secret')
		 APP_KEY =  config.get('StackExchange', 'key')
		
		 #Use API Key with Library
		 stack_exchange = stackexchange.Site(stackexchange.StackOverflow, app_key=APP_KEY)
		 
		 ##########Explaination from https://github.com/lucjon/Py-StackExchange##################
		 #With an API key, requests are limited to thirty per five seconds. 
		 #By default, the library will return an error before even making an HTTP request if we go over this limit. 
		 #Alternatively, you can configure it such that it will wait until it can make another request without returning an error.
		 #To enable this behaviour. set the impose_throttling and throttle_stop property
		 #########################################################################################
		 #Set Impose Throttling to True 
		 #Set Throttle Stop to False

		 stack_exchange.impose_throttling = True  
		 stack_exchange.throttle_stop = False 	  

		 # Read all the Projects from MongoDB (OSSRank Database)
		 projects = getProjects(config)

		 # For each Project , Get Top Questions and Tagged Discussions for last N years from stack exchange sites
		 self.searchStackExchange(stack_exchange,config,projects)

		 self.response.write("Num projects : " + str(len(projects)) + "<br/>")

	def searchStackExchange(self,stack_exchange,config,projects):
		
		# Read configuration to determine number of years in past
		# for which we want to fetch Top Questions and Tagged Discussions and thier count
		searchYears = int(config.get('OSSRank', 'SEARCH_YEARS'))
		
		# Parse each project , get data from Stack Exchange and update it back to Mongo DB
		for project in projects:

			stack_exchange_data = []
			for eachYear in xrange(0,searchYears):

				# Calculate target year to fetch data for Project from Stack Exchange
				targetYear = getCurrentOrPriorYear(eachYear)
				
                # Define and convert from/to date to Epoch Format as required by Stack Exchange API
				fromDate = dateToEpoch(targetYear + '-01-01')
				toDate = dateToEpoch(targetYear + '-12-31')
				
				# Search for Stack Exchange Data in Questions Title and Format it
				keyword_in_title = project['name']	
				searched_questions = self.search_in_title (keyword_in_title, stack_exchange, fromDate, toDate)
				
				# Search for Stack Exchange Data in Tagged Discussions and Format it
				tagged_project = project['name']
				tagged_questions = self.search_for_tag (tagged_project, stack_exchange, fromDate, toDate)
				
				#Club Questions and tagged discussions togather
				all_questions = {targetYear : {'questions' : searched_questions.total , 'tagged_discussions' : tagged_questions.total}}
				
				#Update Stack Exchange Data for the project Grouped by Year
				stack_exchange_data.append(all_questions)

			# Update back fetched data to Project Object
			project.update({'_stackoverflow':stack_exchange_data})
			
			# Extract document id to make updates to DB
			project_oid = project['_id']
			project_document_id = project_oid['$oid']
			
			# Update Project Data to Mongo DB
			update_project_data(config,project,project_document_id)
	
	def search_in_title(self, keyword_in_title ,stack_exchange, fromDate, toDate):
		#Search Questions in StackExchange API between given dates, Response is Sorted by Votes and ordered.
		questions=stack_exchange.search(intitle=keyword_in_title,fromdate=fromDate,todate=toDate,filter='total')
		return questions	

	def search_for_tag (self, tagged_project ,stack_exchange, fromDate, toDate):
		#Search Tagged Discussions in StackExchange API between given dates, Response is Sorted by Votes and ordered.
		questions=stack_exchange.search(tagged=tagged_project,fromdate=fromDate,todate=toDate,filter='total')
		return questions


def getProjects(config):

	#Read Mongo DB Configuration from settings.cfg
	apiURL = config.get('Mongolab', 'apiURL')
	apiKey = config.get('Mongolab', 'apiKey')
	database = config.get('Mongolab', 'database')

	# Get start date for stats
	startDate = getStartDate(config)

	# Get project stats from start date
	url = apiURL + database +"/collections/projects?apiKey=" + apiKey 
	
	headers = {'content-type': 'application/json'}
	r = requests.get(url,timeout=200)
	return r.json()

def update_project_data(config,project,project_document_id):

	#Read Mongo DB Configuration from settings.cfg
	apiURL = config.get('Mongolab', 'apiURL')
	apiKey = config.get('Mongolab', 'apiKey')
	database = config.get('Mongolab', 'database')

	#build Project Document URL
	url = apiURL + database + "/collections/projects/" + project_document_id + "?apiKey=" + apiKey 
	header = {'content-type': 'application/json'}
	response = requests.put(url,data=json.dumps(project),headers=header)
	ret = response.json()
	#print ret

def getStartDate(config):
	# Set number of projects per run
	searchDays = int(config.get('OSSRank', 'SEARCH_DAYS'))
	startDate = datetime.date.fromordinal(datetime.date.today().toordinal()-searchDays) 
	startDate = str(startDate)
	return startDate	

def getCurrentOrPriorYear(yearCount):
	# Get Current Year and subtract yearCount from it. 
	calc_Year = datetime.date.today().year-yearCount
	calc_Year = str(calc_Year)
	return calc_Year

def dateToEpoch(dateStr):
	pattern = '%Y-%m-%d'
	epoch = int(time.mktime(time.strptime(dateStr, pattern)))
	return epoch 

app = webapp2.WSGIApplication([
		('/stackexchange', StackExchangeHandler)
	], debug=False)
