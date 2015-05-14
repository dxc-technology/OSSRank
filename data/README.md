## Data Collection module

This module collects Projects data from sources around the web and stores 
them in OSSRank repository.Current state of implementation only fetches data
from github public repository and stores them in a NoSQL DB.
Our intention is to allow data collection configurable from different sources.
After preliminary project data collection, each project is classified into one
or multiple categories and project document is enriched with category information.

Other parts of our current data collection includes 

1.Collection social media data from Twitter about projects

2.Collection of StackOverflow data (e.g. number of questions,tags etc.)

We enrich our collection with all these data along the timeline to use it for
ranking and analysis. 

## How to Get Help

If you want to help improve OSSRank directly we have a
[fairly detailed CONTRIBUTING guide in the repository][contrib] that you can
use to understand how code gets in to the system, how the project runs, and
how to make changes yourself.


