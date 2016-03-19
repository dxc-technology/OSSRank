#!/usr/bin/env python

# Import the Flask Framework
from flask import Flask, jsonify, abort, request, make_response, url_for
import requests
import ConfigParser
import json
from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(260)

app = Flask(__name__, static_url_path = "")

# Configuration
configF = ConfigParser.RawConfigParser()
configF.read('settings.cfg')
config = {
    'apiURL' : configF.get('Mongolab', 'apiURL'),
    'apiKey' : configF.get('Mongolab', 'apiKey'),
    'database' : configF.get('Mongolab', 'database')
}

@app.after_request
def addHeaders(response):
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin','*') )
    response.headers.add('Access-Control-Allow-Headers', 'Access-Control-Request-Headers')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    if app.debug:
        response.header.add('Access-Control-Max-Age', '1')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    # TODO decide whether all local or what comes from where 
    # response.headers.add('Content-Security-Policy', 'nosniff')
    return response

@app.route('/api/foo', methods=['GET'])
def doFoo():
    return 'Mr. Foo, here\'s your Bar'

@app.route('/api/projects', methods=['GET'])
def getProjects():
    tags = request.args.get('tags')
    filter = request.args.get('filter')
    query = ""
    if tags:
        # split tags list on | delimiter
        tagsList = tags.split("|")
        regex = ""
        # Lookahead regular expression matching *all* tags - this is effectively an AND operation on tags
        for tag in tagsList:
            regex += "(?=.*"+ tag +".*)";

        # Use same regex expression to search in categories and project names
        query = '{"_category": {"$regex":"'+ regex +'","$options":"i"}}'
        query += ',{"name": {"$regex":"'+ regex +'","$options":"i"}}'

        # OR operation in query to match category OR name
        query = "&q={$or: ["+ query +"]}"
    else:
        return "{}"

    if filter:
        filter = "&f={'name': 1, '_id': 1, '_rank': 1, '_category': 1,'description': 1 }&l=40"
        
    url = config['apiURL'] + config['database'] \
        +"/collections/projects?apiKey=" + config['apiKey'] + query +'&s={"_rank": -1, "_category": 1}' + filter
    headers = {'content-type': 'application/json'}
    print url.encode("ascii", "ignore")
    r = requests.get(url,timeout=200)
    return jsonify(projects = r.json())

@app.route('/api/projects/<string:project_id>', methods=['GET'])
def getProject(project_id):
    url = config['apiURL'] + config['database'] \
        +"/collections/projects/" + project_id \
        + "?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    return jsonify(project = r.json())

@app.route('/api/category_map', methods=['GET'])
def getRankedProjects():
    category_name = request.args.get('category')
    query_str="&q={'_category':'"+category_name+"'}"
    url = config['apiURL'] + config['database'] \
        +"/collections/projects" \
        + "?apiKey=" + config['apiKey'] \
        + query_str \
        + "&f= {'name':1,'_rank':1}" \
        + "&s= {'_rank':-1} "
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    return jsonify(projects = r.json())


@app.route('/api/categories', methods=['GET'])
def getCategories():
    url = config['apiURL'] + config['database'] \
        +"/collections/categories?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    return jsonify(categories = r.json())

@app.route('/api/categories/<string:category_id>', methods=['GET'])
def getCategory(category_id):
    url = config['apiURL'] + config['database'] \
        +"/collections/categories/" + category_id \
        + "?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    return jsonify(categories = r.json())

@app.route('/api/search', methods=['GET'])
def getKeywords():
    # Get list of categories 
    url = config['apiURL'] + config['database'] \
        +"/collections/categories?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url,timeout=200)
    cats1 = r.json()
    
    # extract category names 
    cats = []
    for catDict in cats1:
        cats.append(catDict['name'])
    term = request.args.get('term').lower()
    matching = [s for s in cats if term in s.lower()]
    return json.dumps(matching)
