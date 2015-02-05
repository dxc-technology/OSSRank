#The following links helped greatly in the first section of this script where we connect
#to MongoDB and read in the ossrank.projects collection:

#https://docs.compose.io/languages/r.html
#http://stackoverflow.com/questions/22445419/transfer-large-mongodb-collections-to-data-frame-in-r-with-rmongodb-and-plyr

#Although the stackoverflow code produced a discrepancy in the number of documents in his/her
#MongoDB collection compared to the number of observations in R, this code worked fine for
#me. Their collection is much much larger than ours, so perhaps this is something to keep
#an eye on going forward.

#load necessary packages
library(rmongodb)
library(plyr)

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

#get a list of collections within our namespace
mongo.get.database.collections(mongo, db)

#find the number of documents in 'exampleCollection' collection in the ossrank 
#database
mongo.count(mongo, namespace, mongo.bson.empty())

#get the count
#count <- mongo.count(mongo, namespace, query)

#and bring them back into a list
#numbers <- list()
#cursor <- mongo.find(mongo, namespace, query)
#while (mongo.cursor.next(cursor)) {
        #val <- mongo.cursor.value(cursor)
        #numbers[[length(numbers)+1]] <- mongo.bson.value(val, "number")
#}

#read ossrank.projects collection from MongoDB
export = data.frame(stringAsFactors = FALSE)
DBNS="ossrank.projects"
cursor = mongo.find(mongo, DBNS)
i = 1
while(mongo.cursor.next(cursor))
{
        tmp = mongo.bson.to.list(mongo.cursor.value(cursor))
        tmp.df = as.data.frame(t(unlist(tmp)), stringAsFactors = FALSE)
        export = rbind.fill(export, tmp.df)
        i = i + 1
}
#show the size of "export"
dim(export)
#check more information on "export"
str(export)

########################################################################################

#This is where we begin to manipulate data to form scores and ranks

#create new object using the variables in 'keeps', removing the first row of NAs in 'export',
#removing the rownames, and creating a ProjectNames object to be attached after normalizing
keeps <- c("stargazers_count", "forks", "watchers")
ProjectDF <- export[keeps]
ProjectDF <- ProjectDF[2:301,]
rownames(ProjectDF) <- NULL
ProjectNames <- export$name[2:301] 

#coercing the metrics from factor to numeric
ProjectDF$stargazers_count <- as.numeric(levels(ProjectDF$stargazers_count))[ProjectDF$stargazers_count]
ProjectDF$watchers <- as.numeric(levels(ProjectDF$watchers))[ProjectDF$watchers]
ProjectDF$forks <- as.numeric(levels(ProjectDF$forks))[ProjectDF$forks]

#create function to normalize metrics on a 0-1 scale
normalize <- function(x) {
        
        (x - min(x, na.rm=TRUE))/(max(x,na.rm=TRUE) - min(x, na.rm=TRUE))
        
} 

#use lapply to apply normalize() to every column in the data frame 
ProjectDFnorm <- lapply(ProjectDF, normalize)

#coerce to data frame, attach project names, remove NAs, and remove rownames column
ProjectDFnorm <- as.data.frame(ProjectDFnorm)
ProjectDFnorm <- cbind(ProjectDFnorm, ProjectNames)
ProjectDFnorm <- na.omit(ProjectDFnorm)
rownames(ProjectDFnorm) <- NULL 

#verify that the range of all metrics is 0-1. must subset ProjectNames out of this function
lapply(ProjectDFnorm[,1:3], range)

#reorder so that ProjectNames is the first column in the data frame
ProjectDFnorm <- ProjectDFnorm[,c(4,1,2,3)]

#score projects by adding values from normalized metrics
ProjectDFnorm$Score <- ProjectDFnorm$stargazers_count + ProjectDFnorm$forks + ProjectDFnorm$watchers

#rank projects within categories(currently ProjectNames) according to their scores
#must put '-' in front of the variable to be ranked as the default setting ranks values
#low to high
ProjectDFnorm$CategoryRank <- ave(-ProjectDFnorm$Score, ProjectDFnorm$ProjectNames, FUN=rank)

#coerce ProjectDFnorm$ProjectNames to character from factor. This is done so the names 
#dont appear as numbers when written to MongoDB.
ProjectDFnorm$ProjectNames <- as.character(ProjectDFnorm$ProjectNames)

#subset to only scores and ranks. We will also remove the first row and col from 'export', 
#remove rownames, and append the scores and ranks to "export2" 
#facilitate the mongo.update function below
ProjectDFnorm.ScoresRanks <- ProjectDFnorm[,5:6]
export2 <- export[2:301, 2:87]
rownames(export2) <- NULL
export3 <- cbind(export2, ProjectDFnorm.ScoresRanks)

#coerce data frames to mongo.bson so we can write to MongoDB--not necessary for lists
export2 <- mongo.bson.from.df(export2)
export3 <- mongo.bson.from.df(export3)

#append scores and ranks to each document in mongodb
mongo.update(mongo, namespace, criteria=export2, objNew=export3, 
             flags=mongo.update.multi)

#Write data to MongoDB
#mongo.insert(mongo, namespace, ProjectDFnormMONGO)