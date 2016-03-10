#Load necessary packages
library(jsonlite)
library(dplyr)
library(yaml)
library(curl)
library(httr)
library(rjson)
library(foreach)
library(doSNOW)
library(parallel)
# infuture to improve the code with parallel library


#function to get configuration
readConfiguration <- function(){
  config=yaml:::yaml.load_file("config.yml")
  return (config)
}

#get collection length..used for number of iteration to perform on data
getProjectCollectionSize <- function(){
  collectionLengthFindURL <-paste(readConfiguration()$apiURL,readConfiguration()$database,"/collections/",readConfiguration()$collection,"?apiKey=",readConfiguration()$apiKey,"&c=true",sep="")
  collectionSize <- curl(collectionLengthFindURL)%>% jsonlite ::: fromJSON()
  #print()
  return(as.integer(collectionSize))
}

#Number of iteration to perform
# to process full data dump
getNumIterations <- function(){
  total_document_num <- getProjectCollectionSize()
  
  print(total_document_num)
  
  if((total_document_num %% readConfiguration()$processing_chunk) == 0){
    
      return((total_document_num / readConfiguration()$processing_chunk))  
  
    }else{
    
      return((total_document_num %/% readConfiguration()$processing_chunk)+1)  
  }
  
}



#verify if platform is windows
isPlatformWindows <- function(){
  return(grep("Windows",Sys.getenv("OS"),ignore.case = TRUE) ==1)
}

#get number of cores..used for creating cluster to run the job parallely
getNumberOfCores <- function(){
  return(parallel:::detectCores())
}


# Create REST URL to fetch the data
#        the REST URL is mongolab specific
getProejctBaseURL <-function(numOfDocumentToSkip){
  baseURL <-paste(readConfiguration()$apiURL,readConfiguration()$database,"/collections/",readConfiguration()$collection,"?apiKey=",readConfiguration()$apiKey,"&sk=",as.character(numOfDocumentToSkip),"&l=",readConfiguration()$processing_chunk,sep="")
  print(baseURL)
  return (baseURL)    
}

# Create Post URL for a specific document
#   the REST URL is mongolab specific  
getPostURL <- function(documentId){
  
  postURL <-paste(readConfiguration()$apiURL,readConfiguration()$database,"/collections/",readConfiguration()$collection,"/",as.character(documentId),"?apiKey=",readConfiguration()$apiKey,sep="")
  #print(postURL)
  return(as.character(postURL))
  
}

#create function to normalize metrics on a 0-1 scale
norm2 <- function(x) {
  
   return((x - min(x, na.rm=TRUE))/(max(x,na.rm=TRUE) - min(x, na.rm=TRUE)))
  
} 

#Commit a document to repository
#   update document in mongolab
commitDataToRepository_rest <- function(documentId,jsonData){
  dataReq <- httr:::PUT(getPostURL(documentId),
             httr:::add_headers(
                "Content-Type" = "application/json;charset=utf-8"
              ),
             body = jsonData
  );
  status <- httr:::http_status(dataReq)
  print(status)
}

# Function to return difference between currentdate and specified date in days
getDateDifferenceInDays <- function(thisDate){
  return (as.integer(Sys.Date()- thisDate))
}

# Function to calculate score
#   The scoring algorithm -first version - need improvement
#   assumes - a better or popular project has more followers,pull requests over time...
#   so project creation time is a factor in calculating the score
#   different attribute used in scoring algorithm are
#   num_forks + stargazers count + num_watchers + network_count + twitter mentions 
#   right now twitter mentions is very skeewed towards positive .. improvement needed for doing 
#   input is a json structure representing a project
#   There are several other factors which needs to be used in calculating score .like last push to repo. etc.
#   This is an experimental algorithm that will be improved over time
calCulateProjectScore <- function (project,num_tweets){
  
  current_diff <- getDateDifferenceInDays(as.Date(as.character(project["created_at"])))
  
  
  sum_all_scores <- 0
  
  # add all counts
  if("stargazers_count" %in% colnames(project))
  {
    sum_all_scores <- sum_all_scores + as.numeric(project["stargazers_count"])
  }
  if("forks" %in% colnames(project))
  {
    sum_all_scores <- sum_all_scores + as.numeric(project["forks"])
    
  }
  if("watchers" %in% colnames(project))
  {
    sum_all_scores <- sum_all_scores + as.numeric(project["watchers"])
    
  }
  if("network_count" %in% colnames(project))
  {
    sum_all_scores <- sum_all_scores + as.numeric(project["network_count"])
    
  }
  
  sum_all_scores <- sum_all_scores + as.numeric(num_tweets)

  rank_score <- (sum_all_scores/current_diff)
  return(rank_score)
}


# function to get mongo document id for a project
getProjectDocumentId <- function(aProject){
    return(as.character(aProject["_id"][1,]))
}

# function to add project score and date time stamp to the project
addProjectScore <- function(aProject,ossrankScore){
  todaysDate <- Sys.Date()
  #at the moment the score is not appended .. but replaced..
  #this is just to fix scoring algorithm to an acceptable level then to append
  scoreDf <- data.frame("scoreDate"=character(),
                        "ossrankscore"=double(),
                        stringsAsFactors=FALSE)
  scoreDf[nrow(scoreDf)+1,] <- c(as.character(todaysDate),as.double(ossrankScore))
  
  scoreElement <- as.character("_ossrank_score")
  
  scoreList <- list(scoreDf)
  #append score to project 
  aProject[scoreElement] <- as.double(ossrankScore) 
  
  return(aProject)
  
}


getProjectCollectionSize()



#parallelized loop..as many cores available to the machine
current_cluster<- makeCluster(getNumberOfCores()) #set number of cores
registerDoSNOW(current_cluster)

iteration_length <- getNumIterations()

skipDocument <- 0
for(it in 1:iteration_length){
  
    
  #get a dataframe of project objects
  projects<- curl(getProejctBaseURL(skipDocument)) %>% jsonlite ::: fromJSON()
  
  skipDocument <- skipDocument + as.integer(readConfiguration()$processing_chunk)
  

  #foreach parallely is using %dopar% works only registerred cluster 
  #the code will shift to sequential if no cluster is registerred 
  #or only 1 core found

  foreach (i=1:nrow(projects)) %dopar% {
  
    if("_twitter" %in% colnames(projects[i,]))
    {
      tweet_length <- length(projects[i,"_twitter"])
      last_tweets_num <- as.numeric(projects[i,"_twitter"][1,tweet_length])
    } else{
      last_tweets_num <- 0
    } 
  
    ossrank_score <- calCulateProjectScore(projects[i,],last_tweets_num)
    updatedProject <- addProjectScore(projects[i,],ossrank_score)
    projData<- rjson ::: toJSON(updatedProject)
  
    project_documentId_mongo <- getProjectDocumentId(projects[i,])
    #print(projects[i,"name"] )
    commitDataToRepository_rest(project_documentId_mongo,projData)
  
  }

}

stopCluster(current_cluster)











