#############################################
#                                           #
# Program to calculate RANK                 #
# The program uses mongolite to fetch data  #
# rank projects                             #
# REST API to update ,future goal is to use #
# mongolite for both                        #
# Ranking algorithm is described            #
#############################################

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
library(mongolite)

#This code ranks projects in their category
#It iterates over the categories
#for a group of projects in same category it runs the ranking algorithm

#function to get configuration
readConfiguration <- function() {
  config = yaml:::yaml.load_file("config.yml")
  return (config)
}

#get number of cores..used for creating cluster to run the job parallely
getNumberOfCores <- function() {
  return(parallel:::detectCores())
}



#get connection to mongodb
getOSSrankRepoCon <- function() {
  connUrl <-
    paste(
      'mongodb://',readConfiguration()$user,':',readConfiguration()$password,'@',readConfiguration()$host,':',readConfiguration()$port,'/',readConfiguration()$database,sep =
        ''
    )
  con <-
    mongo(
      collection = readConfiguration()$collection,url = connUrl,verbose = TRUE
    )
  return(con)
}


#query projects by category
#ex.
#{
#"_category": {
#  "$regex": ".*JavaScript.*",
#  "$options": "i"
# }
#}
getProjectsByCategory <- function(category_name,repo_conn) {
  query_str = paste('{ "_category":{ "$regex": ".*',category_name,'.*", "$options": "i" } }',sep =
                      "")
  print(query_str)
  #projects <- repo_conn$find('{ "_category":{ "$regex": ".*JavaScript.*", "$options": "i" } }')
  projects <-
    repo_conn$find(query_str,fields = '{"_id" : 1,"git_url":1,"created_at":1,"updated_at":1,"subscribers_count":1,"network_count":1,"watchers_count":1,"stargazers_count":1,"_twitter":1}')
  return(projects)
}


###########REST API SPECIFIC FUNCTIONS ############

# Create Post URL for a specific document
#   the REST URL is mongolab specific
getPostURL <- function(documentId) {
  postURL <-
    paste(
      readConfiguration()$apiURL,readConfiguration()$database,"/collections/",readConfiguration()$collection,"/",as.character(documentId),"?apiKey=",readConfiguration()$apiKey,sep =
        ""
    )
  #print(postURL)
  return(as.character(postURL))
  
}

#Commit a document to repository
#   update document in mongolab
commitDataToRepository_rest <- function(documentId,jsonData) {
  dataReq <- httr:::PUT(
    getPostURL(documentId),
    httr:::add_headers("Content-Type" = "application/json;charset=utf-8"),
    body = jsonData
  );
  status <- httr:::http_status(dataReq)
  print(status)
}



# Create REST URL to fetch the data
#        the REST URL is mongolab specific
getProejctGetURL <- function(projectId) {
  baseURL <-
    paste(
      readConfiguration()$apiURL,readConfiguration()$database,"/collections/",readConfiguration()$collection,"/",projectId,"?apiKey=",readConfiguration()$apiKey,sep =
        ""
    )
  print(baseURL)
  return (baseURL)
}

##############END REST API functions ################




#function to get mongo document id for a project
#this convoluted approach is to be replaced
#https://github.com/jeroenooms/mongolite/issues/32
getProjectDocumentId <- function(aProject) {
  idFrame <- as.data.frame(aProject["_id"])
  idAsCharList <- as.character(idFrame[1,][[1]])
  return(paste(idAsCharList,collapse = ""))
}






#create function to normalize metrics on a 0-1 scale
norm2 <- function(x) {
  return((x - min(x, na.rm = TRUE)) / (max(x,na.rm = TRUE) - min(x, na.rm =
                                                                   TRUE)))
}



####################################################################
# Ranking algorithm method
# Current Ranking algo
# For each attributes normalize values for projects in same category
# add them 
####################################################################

rankByCategory <- function(categoryName) {
  current_projects <-
    getProjectsByCategory(categoryName,getOSSrankRepoCon())
  
  
  
  #projects_collection_normalized$objectid <- apply(current_projects[,c("_id")],1,getProjectDocumentId1)
  
  projects_collection_normalized <-
    select(current_projects,starts_with("_id"))
  
  if ("subscribers_count" %in% colnames(current_projects)) {
    norm_subscriber_count <-
      convertNAandNormalize(select(current_projects,subscribers_count))
    projects_collection_normalized[,"norm_subscriber_count"] <-
      norm_subscriber_count
  }
  
  if ("network_count" %in% colnames(current_projects)) {
    norm_network_count <-
      convertNAandNormalize(select(current_projects,network_count))
    projects_collection_normalized[,"norm_network_count"] <-
      norm_network_count
  }
  
  
  norm_watchers_count <-
    convertNAandNormalize(select(current_projects,watchers_count))
  projects_collection_normalized[,"norm_watchers_count"] <-
    norm_watchers_count
  
  
  
  all_score_projects <-
    rowSums(projects_collection_normalized[,-1])
  #print(all_score_projects)
  
  projects_collection_normalized[,"score"] <- all_score_projects
  
  #print(projects_collection_normalized)
  
  projects_collection_normalized <-
    arrange(projects_collection_normalized,desc(score))
  
  projects_collection_normalized <-
    mutate(projects_collection_normalized, '_ossrank' = row_number())
  
  
  #projects_collection_normalized$objectid <- apply(projects_collection_normalized[,c('_id')],1,getProjectDocumentId)
  
  #print(projects_collection_normalized)
  
  return(projects_collection_normalized)
  
  
}

convertNAandNormalize <- function(singleColumnDf) {
  #make NA to 0..we don't need NA values
  singleColumnDf[is.na(singleColumnDf)] <- 0
  #nromalize and return
  return(norm2(as.vector(singleColumnDf)))
  
  
}



#list of categories to process
category_list <-
  c(
    "IDE","Mobile API","BigData","JavaScript Libraries","Web Application Framework","Database","Batch Processing"
  )

for (category_name in category_list) {
  print (paste("Ranking projects for category " , category_name ,sep = " "))
  
  #call ranking function
  
  ranked_projects <- rankByCategory(category_name)
  
  #parallelized loop..as many cores available to the machine
  current_cluster <-
    makeCluster(getNumberOfCores()) #set number of cores
  registerDoSNOW(current_cluster)
  
  #update project rank in parallel
  foreach(
    i = 1:nrow(ranked_projects),.combine = cbind,.packages = c('dplyr','curl')
  ) %dopar% {
    document_id <- getProjectDocumentId(ranked_projects[i,])
    #project_get_url <- getProejctGetURL(document_id)
    projectDocumentFromMongo <-
      curl(getProejctGetURL(document_id)) %>% jsonlite:::fromJSON()
    
    if ("_ossrank_rank" %in% names(projectDocumentFromMongo)) {
      print(projectDocumentFromMongo["_ossrank_rank"])
      rankData <- projectDocumentFromMongo[["_ossrank_rank"]]
      rankData[[category_name]] <- i
      projectDocumentFromMongo[["_ossrank_rank"]] <- rankData
    }else{
      rankData <- list()
      rankData[[category_name]] <- i
      projectDocumentFromMongo[["_ossrank_rank"]] <- rankData
    }
    
    #convert to json and commit to repo
    projData <- rjson:::toJSON(projectDocumentFromMongo)
    commitDataToRepository_rest(document_id,projData)
    
  }
  
  ##stop the cluster
  stopCluster(current_cluster)
}
