#!/usr/bin/env python
# encoding: utf-8

GITHUB_API = 'https://api.github.com'

import requests
import getpass
import json
from urlparse import urljoin

#Define our function to return Github Oauth token
#Once the token is generated it can be used by collection API
def getGithubOauthtoken():

    username = raw_input('Your Github username : ')
    password = getpass.getpass('your Github password :')
    #the note will be asociate the specific  token generated in your account
    note=raw_input('Personal Note(Optional):')

    url = urljoin(GITHUB_API , 'authorizations')
    payload = {}
    if note:
        payload['note']=note
    res= requests.post(
                      url,
                      auth=(username, password),
                      data=json.dumps(payload),
                      )
    #print statements are for debug only
    print res.status_code
    print res.headers['content-type']
    print res.text

    #parsing json response from git hub
    j=json.loads(res.text)
    token=j['token']
    print 'Github Token;%s'%token
    return token
