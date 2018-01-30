## Data Collection module
**OSSRanking** collects *Open Source Projects metadata* to analyse and rank.
This module collects Projects data from sources around the web and stores
them in OSSRank repository. Current state of implementation  fetches project metadata
from *GitHub public repository* and stores them in a *NoSQL DB*.
Our intention is to allow data collection configurable from different sources.
After preliminary project data collection, each project is classified into one
or multiple categories and project document is enriched with category information.

Other parts of our current data collection includes

1.Collection social media data from Twitter about projects

2.Collection of StackOverflow data (e.g. number of questions, tags etc.)

We enrich our collection with all these data along the timeline to use it for
ranking and analysis.


### Data Collection Mechanism

>####The Story behind ####
This section explains our initial project *metadata* collection process. We are
using GitHub *FOSS projects* as initial source of projects information. Even
GitHub contains millions *FOSS Projects*, going through them sequentially and
removing forks as part of data collection can be cumbersome and time-consuming.
So our initial effort is to collect *metadata* of projects that have more than
10 forks. It turns out there are more than 100000 projects meeting this criteria
and *GitHub API v3* only provides us with metadata for first top 1000 projects
matching that criteria.
*GitHub Archive* and *Google BigQuery* helps us solve the issue , so that we can collect data in few hours.
Using BigQuery on latest *GitHub Archive* we fetch list of all projects & metadata URLs in matter of few seconds. Once available , this data is dumped to a csv file. Our loader goes through the csv file and fetches project metadata using the *URLs* and store in **OSSRank** Repository.
