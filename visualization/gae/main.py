#!/usr/bin/env python

# Import the Flask Framework
from flask import Flask, jsonify, abort, request, make_response, url_for
import requests

app = Flask(__name__, static_url_path = "")

# Configuration
config = {
    'apiURL' : "https://api.mongolab.com/api/1/databases/",
    'apiKey' : "",
    'database' : "ossrank"
}

@app.route('/api/projects', methods=['GET'])
def getProjects():
    url = config['apiURL'] + config['database'] \
        +"/collections/projects?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url)
    return jsonify(projects = r.json())

@app.route('/api/projects/<string:project_id>', methods=['GET'])
def getProject(project_id):
    url = config['apiURL'] + config['database'] \
        +"/collections/projects/" + project_id \
        + "?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url)
    return jsonify(project = r.json())

@app.route('/api/categories', methods=['GET'])
def getCategories():
    url = config['apiURL'] + config['database'] \
        +"/collections/categories?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url)
    return jsonify(categories = r.json())

@app.route('/api/categories/<string:category_id>', methods=['GET'])
def getCategory(category_id):
    url = config['apiURL'] + config['database'] \
        +"/collections/categories/" + category_id \
        + "?apiKey=" + config['apiKey']
    headers = {'content-type': 'application/json'}
    r = requests.get(url)
    return jsonify(categories = r.json())
