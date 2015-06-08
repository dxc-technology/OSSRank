##Overview of Ranking Process

The ranker reads the project data from MongoDB and creates scores and ranks based on metrics like GitHub forks and Twitter mentions, which are normalized on a 0-1 scale. The metrics are normalized so that we can give equal weight to metrics with different magnitudes. For example, we would expect that a project would have a large difference in the amount of GitHub forks compared to the amount of Twitter mentions. Normalizing allows us to rectify this difference. 

Scores are created for each project by summing the normalized metrics. We then rank projects within their respective categories based on these scores and write back to MongoDB.

The code is heavily commented and one can understand most everything going on just by following the comments in the code. However, I have provided further guidance below for those new to R and in regards to reading in the data.

##Instructions for Running the Code

####For those new to R

We recommend installing RStudio when you install R. RStudio is an IDE that greatly improves the R experience.

You will notice a number of "library" functions at the top of the script. These are commands that load various R packages. You will need to install these packages using the install.packages function to get the code to work properly. Here is an example. At the console, simply type: install.packages("rmongodb"). It is also worth noting that R is case-sensitive.

####Reading from the Database
Our data is stored in a MongoDB database. You can follow the documentation regarding data collection and project classification to understand how to get to the point where the data is stored in a MongoDB database. You can follow the ranking code to understand how to read that data from MongoDB. If you choose to store your data somewhere other than MongoDB, then you will need to ascertain how to read the data into R on your own.

The database credentials are stored in a YAML file. This file is stored in the same directory as the R script. R's YAML package allows for the parsing of YAML files. Doing this enables others to observe the R code without allowing them to access your database.

##Questions?
Contact Kyle Zellman at kylezellman@gmail.com with the subject 'OSSRank.'

