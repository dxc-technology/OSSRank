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

app.controller("AboutCtrl", function ($scope) {
    
});




app.controller("ProjectCtrl", function ($scope,$http,$routeParams, Project) {
    $scope.proj = "Project";

    $scope.projectId = $routeParams.projectId;
    console.log($scope.projectId);

    var project = Project.get({
        id: $scope.projectId
    }, function () {
        //console.log(project);
        $scope.project = project.project;
        //get relative rank
        var projCategory= $scope.project._category ;
        
         var projectName = $scope.project.name ;
        
        $http.get('/api/category_map'+'?category='+projCategory).success(function(response){
                var ranked_projects=response.projects;
                //all_proj = JSON.parse(ranked_projects);
                 var rank=1;
                 var after = "";
                 var before = "";
                for (var key in ranked_projects) {
                   if (ranked_projects.hasOwnProperty(key)) {
                         var name= ranked_projects[key]['name'];
                         //console.log(name);
                         if(projectName == name){
                              $scope.projectRank=rank;
                              break;
                            }
                        after = name ;
                        rank++;
                     }
                }
                $scope.after_project = (after == "")?"" : " In ranking After " + after ; 
                //console.log(ranked_projects);
                });
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

        // get stack exchange api data
        var stack_exchange_data = $scope.project._stackoverflow;
      
        $scope.nbr_of_years = Object.keys(stack_exchange_data).length;
       
        $scope.questions = 0;
        $scope.tagged_discussions = 0 ;

        var years = [];
        var questions_per_year = [];
        var tagged_discussions_per_year = [];
           
        if($scope.nbr_of_years > 0) {
            angular.forEach(stack_exchange_data, function(value, key){
                angular.forEach(value , function(value,key){
                    years.push(key);
                    questions_per_year.push(value.questions);
                    tagged_discussions_per_year.push(value.tagged_discussions); 
                    $scope.questions = $scope.questions + value.questions;
                    $scope.tagged_discussions = $scope.tagged_discussions + value.tagged_discussions;
                        })
                    });
            }

        $scope.year_labels = years;
        $scope.questions_series = questions_per_year;
        $scope.tagged_discussions_series = tagged_discussions_per_year;    
        
        //console.log(Object.keys(tweets).length)
        
    });

    

    

    $scope.showCategoryMap= function() {
         var appCategory= $scope.project._category ;
         var popupURL= window.location.protocol + "//" + window.location.host + "/category_map?type=" + appCategory;
         window.open(popupURL,"menubar=no, toolbar=no,location=no, width=700,height=600");  
    };

});