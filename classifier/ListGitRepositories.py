#This  code will download all the git public repositories and write in
#a set of text file in json format if once started
#be aware this needs can run automatically for days before end of public repo is reached
import json
import requests
from urlparse import urljoin
from GitHubLogin import getGithubOauthtoken
import time
from util.configuration import getGitHubRepoUrl

def main():
    ##get github auth token
    git_auth_token = getGithubOauthtoken()
    
    ## start point to get data dump
    current_start=1
    incr_count=365
    
    ##create header for request containing auth token 
    headers= {
              'Authorization':'token %s'% git_auth_token
              }
    ##
    fetch_github_data=True
    ## while loop to fetch data
    print "Starting Github data dump in paginated format with each page ,365 repositories"
    while fetch_github_data :
        current_fetch_url=urljoin(getGitHubRepoUrl() , '?since='+str(current_start))
        current_fetch_res=requests.get(current_fetch_url, headers=headers)
        ##print current_fetch_res.status_code
        contentLen = len(current_fetch_res.text)
        fileName = 'github_dump_startpoint_'+str(current_start)+'.txt'
        jsonRespData=json.loads(current_fetch_res.text)
        ## dump the data in a file
        with open(fileName, 'w') as outfile:
            json.dump(jsonRespData, outfile)
            print 'Github Repository Content Staring from ' , current_start ,'written in ', fileName
         
        current_start=current_start+incr_count
        if contentLen== 2 :
            fetch_github_data=False
        ##introduce sleep so as not to reach call limit
        time.sleep(5)
    
if  __name__=='__main__':
    main()
    
