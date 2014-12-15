## Introduction

A project for ranking and categorizing OSS projects.
Data Collected from Github and Social Media

## How to Get Help

If you want to help improve OSSRank directly we have a
[fairly detailed CONTRIBUTING guide in the repository][contrib] that you can
use to understand how code gets in to the system, how the project runs, and
how to make changes yourself.

## Reporting Issues

If you find any issues, feel free to report them in the [issues][issues] section of this repository.

### TODO List ###
Classifier instructions - consider to move to wiki
* GitHubLogin.py - This code responsible for Oauth in github asks users credential while running , this class is used by all 2 other classes in this dir Search & List namely
* ListGitRepositories.py - It is a bot if you strat running it , it will dump all public git repo in your local machine until end of repo is reached
* QueryOpenHub.py - queries openhub for specific project and fetches desc & tags to be used for classification
* SearchGitRepositories.py - searches github with specific search criteriea and then classifies the result--classification part to be committed soon
* SoftwareCategory.json - currently defined categories for our classification and this file is going to enriched , for now used for classifying search result

[contrib]:      CONTRIBUTING.md
[license]:      LICENSE
[issues]:       https://github.com/csc/OSSRank/issues
