## Introduction

UI for OSSRank

## Requirements
* Python 2.7
* Google App Engine SDK

## Twitter API Instructions
* Register as a developer with Twitter
* Create new app and note API keys

## Install
Run 'pip install -r requirements.txt -t lib/' to install these dependencies  in lib/ subdirectory.

## Config
Rename sample_settings.cfg to settings.cfg and fill in API keys and info

## App Engine Instructions
* Create new app
* Replace application name at top of app.yaml

### Scheduling Periodic Execution on GAE
Update cron execution frequency in cron.yaml

### Deployment
Deploy using App Engine launcher
