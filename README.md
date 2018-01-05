
![OSSRank](OSSRank_logo.png)

OSSRank is a project for ranking and categorizing open source projects - very meta.

## Introduction

There are millions of open-source software projects and libraries available on the internet and many more get added every day.
As a prospective user of open source software, you probably find yourself going through a process something like this:
* Search for candidate projects you could use to solve a particular problem
* Evaluate various projects that meet your search criteria
* Visit each of their project sites and source code repositories to try to determine things like maturity of the project, size and activity level of the community, responsiveness to issues
* Look around on StackOverflow, Twitter and various discussion forums to see what people are saying about it

OSSRank attempts to automate this whole process by:
* Discovering open-source projects by collecting their metadata from GitHub
* Classifying them into a growing list of specified categories
* Collecting data about them from stackexchange & finding their social footprint on twitter
* Continuously evaluating them and tracking their growth over a timeline
* Ultimately ranking each project within its categories

### Data Collection
Project metadata is collected from Github and stored in a NoSQL database currently MongoDB.  Each project's metadata is periodically augmented with related data from Twitter and StackOverflow.

### Classification
Project descriptions are analyzed and compared against a text corpus to automatically place projects into one or more categories   

### Ranking
Project metadata from these sources is analyzed to assign a rank based on criteria such as number of commits, size of community, number of questions asked and answered.

### Visualization
The results of this analysis is used to provide an interactive searchable UI at http://ossrank.appspot.com which includes visualizations to help OSS users to evaluate projects suitable for their use.

### Future Plans
In the future we plan to do much more adding sentiment analysis of the feeds in twitter, and add security analysis as part of our evaluation.

## How to Get Help

If you want to help improve OSSRank directly we have a
[fairly detailed CONTRIBUTING guide in the repository][contrib] that you can
use to understand how code gets in to the system, how the project runs, and
how to make changes yourself.

## Reporting Issues

If you find any issues, feel free to report them in the [issues][issues] section of this repository.



[contrib]:      CONTRIBUTING.md
[license]:      LICENSE
[issues]:       https://github.com/dxc-technology/OSSRank/issues


## Build Status
![Build Status](https://travis-ci.org/theroys/OSSRank.svg?branch=master)
