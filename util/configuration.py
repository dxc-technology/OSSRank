import json

#Get MongoLab URL from configuration
def getMongoLabUrl():
    config = json.load(open("../config.json"))
    collection = config["data"]["COLLECTION"]
    apikey = config["data"]["MONGODB_API_KEY"]
    database = config["data"]["DATABASE"]
    mongolaburl = config["data"]["MONGOLAB_URL"]
    url = mongolaburl + database + "/collections/"+ collection +"?apiKey=" + apikey
    return url

# Get OpenHub API key from configuration
def getOpenHubAPIKey():
    config = json.load(open("../config.json"))
    apikey = config["classifier"]["OPENHUB_API_KEY"]
    return apikey

# Get OpenHub search URL from configuration
def getOpenHubSearchUrl():
    config = json.load(open("../config.json"))
    url = config["classifier"]["OPENHUB_SEARCH_URL"]
    return url

# Get GitHub API URL from configuration
def getGitHubAPIUrl():
    config = json.load(open("../config.json"))
    url = config["classifier"]["GITHUB_API"]
    return url

# Get GitHub repository URL
def getGitHubRepoUrl():
    config = json.load(open("../config.json"))
    url = config["classifier"]["GITHUB_REPO_URL"]
    return url

# Get GitHub repository prefix
def getGitHubRepoPrefix():
    config = json.load(open("../config.json"))
    url = config["classifier"]["GITHUB_REPO_URL_PREFIX"]
    return url

# Get GitHub repository search URL
def getGitHubRepoSearchUrl():
    config = json.load(open("../config.json"))
    url = config["classifier"]["GITHUB_REPO_SEARCH_URL"] + "?" + config["classifier"]["SEARCH_TERM"]
    return url

# Get GitHub search page size from configuration
def getGitHubSearchPageSize():
    config = json.load(open("../config.json"))
    pagesize = config["classifier"]["PAGE_SIZE"]
    return pagesize

# Get GitHub search term from configuration
def getGitHubSearchTerm():
    config = json.load(open("../config.json"))
    term = config["classifier"]["SEARCH_TERM"]
    return term

# Get GitHub Oauth token from configuration
def getGithubOauthtokenFromConfig():
    config = json.load(open("../config.json"))
    token = config["classifier"]["GitHUB_OAUTH_TOKEN"]
    return token
