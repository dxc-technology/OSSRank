#Load necessary packages
library(RankAggreg)
library(jsonlite)
library(RMongo)

#Make sure files are in your working directory. Type ?setwd is you need assistance.

#reading in json files and converting lists to data frames if necessary.
#the jsonlite package allows for conversion between JSON and R objects.
GitHubSample <- fromJSON(txt="OSSRankSampleJSONGitHub.json")

TwitterSample <- fromJSON(txt="OSSRankSampleJSONTwitter.json")

TwitterSample <- as.data.frame(TwitterSample)

#subset github data to include a particular OSS category
WebAppFrame <- subset(GitHubSample, GitHubSample$ategor=="Web Application Framework")

#example of matching github project name with twitter user name
ExampleMatch <- WebAppFrame[WebAppFrame$roject_nam %in% TwitterSample$twitter.user.name,]

#subset the twitter data to only include OSS projects in the ExampleMatch DF. 
#add an id variable to ExampleMatch and the Twitter data subset and merge them together.
#how will this process work with SO data?

#filter out all variables that aren't in the feature set(e.g. twitter follows)
#sort by each metric to see where projects rank on each metric
#apply ranking algo

#example rank aggregation without weights. 
x <- matrix(c("A", "B", "C", "D", "E",
              "B", "D", "A", "E", "C",
              "B", "A", "E", "C", "D",
              "A", "D", "B", "C", "E"), byrow=TRUE, ncol=5)

#read in json data in mongo and run ranking algo on that

ExampleRank <- RankAggreg(x, 5, method="CE", distance="Spearman", N=100, convIn=5, rho=.1)

#Explaining the ranking algorithm:

#The RankAggreg algorithm aggregates rank-ordered lists. Ranks can be weighted 
#if desired. For example, if we decide Twitter follows are more important than 
#GitHub forks, the algorithm can accommodate this. There are two methods for
#ranking general problems: the Cross-Entropy Monte Carlo Algorithm and the 
#Genetic Algorithm. Alternatively, the brute force approach can be used for 
#small problems where the top-k list is less than or equal to 10. This approach
#simply generates all possible ordered lists and outputs the optimal top-k list.
#For larger k's, Cross-Entropy Monte Carlo is generally superior to the Genetic 
#Algorithm and I see no reason why our case would differ. This approach
#consists of an iterative procedure for solving a combinatorial problem like ours
#when it's too computationally expensive to directly find the optimal solution using 
#brute force. Instead, the algorithm searches for the list which is as close as 
#possible to the collection of ordered lists using either Spearman's footrule 
#distance or Kendall's tau distance. The list with the highest amount of "closeness"
#serves as the top-k list. 
