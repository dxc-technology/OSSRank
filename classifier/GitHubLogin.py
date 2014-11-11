import requests
import getpass
import json
from urlparse import urljoin
from util.configuration import getGitHubAPIUrl, getGithubOauthtokenFromConfig

#Define our function to return Github Oauth token
#Once the token is generated it can be used by collection API
def getGithubOauthtoken():
    #get token from configuration first
    token = getGithubOauthtokenFromConfig()
    
    if token and not token.isspace() and len(token) > 0:
        return token
    
    username = raw_input('Your Github username : ')
    password = getpass.getpass('Your Github password :')
    #the note will be associate the specific  token generated in your account
    note=raw_input('Personal Note(Optional):')
    
    url = urljoin(getGitHubAPIUrl() , 'authorizations')
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
    
    #parsing json response from GitHub
    j = json.loads(res.text)
    token = j['token']
    print 'Github Token;%s'%token
    return token