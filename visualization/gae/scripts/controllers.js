app.controller("HomeCtrl", function ($scope, Category, Project) {
    $scope.proj = "Projects";

    var categories = Category.get(function () {
        //console.log(categories.categories);
        $scope.categories = categories.categories;
    }); //query() returns all the categories

    var projects = Project.get(function () {
        //console.log(projects.projects);
        $scope.projects = projects.projects;
    });
});

app.controller("AbouCtrl", function ($scope) {
    
});




app.controller("ProjectCtrl", function ($scope, $routeParams, Project) {
    $scope.proj = "Project";

    $scope.projectId = $routeParams.projectId;
    console.log($scope.projectId);

    var project = Project.get({
        id: $scope.projectId
    }, function () {
        //console.log(project);
        $scope.project = project.project;
        //get tweets
        var tweets = $scope.project._twitter ;
        tweets_length = Object.keys(tweets).length;
        if(tweets_length > 0){
         $scope.today_tweets =  " on " + Object.keys(tweets)[tweets_length-1] + " , "  + tweets[Object.keys(tweets)[tweets_length-1]]   ;
         //todo optimize following part - bad coding
         var tweet_mention_dates = [];
         var tweet_mention_numbers = [];
         
         var reversed_tweet_dates = Object.keys(tweets).reverse();
         for (i=0;i<tweets_length;i++){
               //show only last 7 days
               if(i == 7) break;
               tweet_mention_dates[i] = reversed_tweet_dates[i] ;
               tweet_mention_numbers[i] = tweets[tweet_mention_dates[i]];
          }
         //make graph 
         $scope.labels = tweet_mention_dates;
         $scope.series = ['Tweets']; 
         $scope.data = [ tweet_mention_numbers ];
        }else{
           $scope.today_tweets =  "N/A" ;
        }
        
        
        //console.log(Object.keys(tweets).length);

       
       
        
    });

    

    

    $scope.showCategoryMap= function() {
         var appCategory= $scope.project._category ;
         var popupURL= window.location.protocol + "//" + window.location.host + "/category_map?type=" + appCategory;
         window.open(popupURL,"menubar=no, toolbar=no,location=no, width=700,height=600");  
    };

});