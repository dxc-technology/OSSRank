#load necessary packages
library(rmongodb)
library(plyr)
library(rjson)
library(rowr)
#create credential variables
host <- "ds039860.mongolab.com:39860"
username <- "ossrank"
password <- "cscOSSRank1"
db <- "ossrank"

#connect to MongoDB server
mongo <- mongo.create(host=host, db=db, username=username, password=password)

#lets create a string that points to our namespace
collection <- "projects"
namespace <- paste(db, collection, sep=".") 

#read in data from mongolab
collection <- "ossrank.projects"
ProjectList <- mongo.find.all(mongo, collection)

#take first 3 elements from ProjectList for development
#ProjectList <- ProjectList[1:3]

#Extract relevant list items
ProjectList2 <- sapply(ProjectList, "[", c("_category","id","open_issues","forks", 
                                           "watchers")) 
ProjectList3 <- t(ProjectList2)
ProjectDF <- as.data.frame(ProjectList3)
#Extract StackOverflow questions and attach to dataframe
SO <- sapply(ProjectList, "[", "_stackoverflow")
SO <- sapply(SO, "[", "questions")
ProjectDF$StackOverflow <- SO
#Extract Twitter data, sum values, and attach to dataframe
Twitter <- sapply(ProjectList, "[", "_twitter")
Twitter <- sapply(Twitter, as.numeric)
Twitter <- sapply(Twitter, sum)
ProjectDF$Twitter <- Twitter
#coercing non-numeric cols to numeric
ProjectDF$open_issues <- as.numeric(ProjectDF$open_issues)
ProjectDF$forks <- as.numeric(ProjectDF$forks)
ProjectDF$watchers <- as.numeric(ProjectDF$watchers)
ProjectDF$StackOverflow <- as.numeric(ProjectDF$StackOverflow)

#create function to normalize metrics on a 0-1 scale
norm2 <- function(x) {
        
        (x - min(x, na.rm=TRUE))/(max(x,na.rm=TRUE) - min(x, na.rm=TRUE))
        
} 

#normalize metrics 
ProjectDFnorm <- sapply(ProjectDF[3:7], norm2)

#coerce to data frame, attach IDs, remove NAs, coerce ID to character
IDs <- ProjectDF$id
Categories <- ProjectDF[1]
ProjectDFnorm <- as.data.frame(ProjectDFnorm)
ProjectDFnorm <- cbind.fill(ProjectDFnorm, IDs, Categories)
ProjectDFnorm <- na.omit(ProjectDFnorm)
names(ProjectDFnorm)[6:7] <- c("ID","Category")
ProjectDFnorm <- ProjectDFnorm[,c(7,6,1,2,3,4,5)]
ProjectDFnorm$ID <- as.character(ProjectDFnorm$ID)
ProjectDFnorm$Category <- as.character(ProjectDFnorm$Category)

#score projects by adding values from normalized metrics
ProjectDFnorm$ProjectScore <- ProjectDFnorm$watchers + ProjectDFnorm$forks + 
        ProjectDFnorm$open_issues + ProjectDFnorm$StackOverflow + ProjectDFnorm$Twitter

#coerce Category to factor to facilitate ranking. must coerce to character first
ProjectDFnorm$Category <- as.character(ProjectDFnorm$Category)
ProjectDFnorm$Category <- as.factor(ProjectDFnorm$Category)

#rank projects within categories according to their scores
#must put '-' in front of the variable to be ranked as the default setting ranks values
#low to high
ProjectDFnorm$CategoryRank <- ave(-ProjectDFnorm$ProjectScore, ProjectDFnorm$Category, 
                                  FUN=rank)

rank <- c(2,4,6)

#add timestamp
ProjectDFnorm$LastUpdated <- Sys.time()

#function to update the DB
update_db <- function(ProjectList,ProjectDFnorm)
{
  for(i in 1:nrow(ProjectDFnorm))
  {
    if(!is.na(ProjectDFnorm[i,"ID"]))
    {
      row <- ProjectDFnorm[i,]
      pos <- grep(ProjectDFnorm[i,"ID"],ProjectList)
      rec <- ProjectList[[pos]]
      score <- ProjectDFnorm[i,"ProjectScore"]
      CategoryRank <- ProjectDFnorm[i, "CategoryRank"]
      LastUpdated <- ProjectDFnorm[i, "LastUpdated"]
      rec$Rank <- c(score, CategoryRank, LastUpdated)
      #criteria    <- list("id"=id)
      #fields      <- do.call(c, unlist(ProjectList[1], recursive=FALSE))
      #fields      <- test2
      #b           <- mongo.bson.from.JSON(toJSON(rec.json))
      #crit        <- mongo.bson.from.list(lst=criteria)
      #mongo.update(mongo, namespace, criteria=crit, objNew=b)
      bnew <- mongo.bson.from.list(list("$set"=list("ProjectScore"=ProjectDFnorm[i,"ProjectScore"],"CategoryRank"=ProjectDFnorm[i, "CategoryRank"], "LastUpdated"=ProjectDFnorm[i, "LastUpdated"])))
      #print(bnew)
      #print(ProjectDFnorm[i,"IDs"])
      #flush.console()
      #browser()
      res = mongo.update(mongo, namespace,paste('{"id":',ProjectDFnorm[i,"ID"],'}'), objNew=bnew)
    }
    
  }
  
}

update_db(ProjectList,ProjectDFnorm)

#Subset only including scores and ranks
# ProjectDFnorm.ScoresRanks <- ProjectDFnorm[,4:5]

#coerce data frames to mongo.bson so we can write to MongoDB--not necessary for lists
# IDs2 <- as.list(IDs)
# ProjectDFnorm2 <- mongo.bson.from.df(ProjectDFnorm)

# #append scores and ranks to each document in mongodb..separate out ID and use that as criteria
# mongo.update(mongo, namespace, criteria=OneID, objNew=ProjectDFnorm2)#criteria needs to be one id...new object
# #needs to either add specific fields or be the entire list from mongo.find.all with the new fields appended.
# test <- as.character(IDs2$IDs)
# criteria    <- list("_id"=test[1])
# #fields      <- do.call(c, unlist(ProjectList[1], recursive=FALSE))
# fields      <- test2
# b           <- mongo.bson.from.JSON(test2.json)
# crit        <- mongo.bson.from.list(lst=criteria)
# #mongo.update(mongo, namespace, criteria=crit, objNew=b)
# mongo.update(mongo, namespace, criteria=list("_id"=crit), objNew=list('$set' =b))
