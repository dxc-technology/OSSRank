#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import webapp2
import os
import sys
sys.path.insert(0, 'lib')
import requests
from twython import Twython
from twython import TwythonStreamer

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class MainHandler(webapp2.RequestHandler):
    def get(self):

        consumer_key="ipIRGSPl6xyoG95HCoqQ"
        consumer_secret="EWM9oArBTJNfOdrVTKXEabUsBDNkV8gB4CaYHs8UkFI"
        access_token="15930713-BZ4qrTnWnNW3ZKkEzSJwFh5YxPF1hPBuvC5tVs5TZ"
        access_token_secret="l3KRZjdOuOq0zircat6VFu4NkMrMubxgpbE14GVFSY"

        twitter = Twython(consumer_key, consumer_secret,
                           access_token, access_token_secret)

        # Fetch live statuses for keywords
        # https://dev.twitter.com/docs/using-search
        # Get keywords
        api = self.request.get('api', 'twitter') # rest or stream
        keywords = self.request.get('keywords', 'bootstrap OR nodejs OR jquery')
        twmode = self.request.get('twmode', 'rest') # rest or stream

        # Fetch top projects from GitHub
        url = "https://api.github.com/search/repositories?q=forks%3A%22%3E+100%22&sort=stars&order=desc"
        r = requests.get(url)
        projects = r.json()

        # Search twitter fgor project keywords
        kwset = set()
        for project in projects['items']:
            kwset.add(project['name'])
        
        # Convert project names to hash tags
        keywords = '#' + ' OR #'.join(kwset)
        tweets = twitter.search(q=keywords, result_type='popular')
        #print tweets['search_metadata']

        for tweet in tweets['statuses']:
          print tweet['user']
        
        # Load attributes to show in web page template	
        template_values = {
            'projects':  projects,
            'twmode': twmode,
            'keywords': keywords,
            'tweets': tweets['statuses']
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

        self.response.write('Contact')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
