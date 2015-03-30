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
    });

    $scope.alltweets = function(){
        var twitterData= $scope.project._twitter ;
        var currentTotal = 0;
        var currentKey = null ; 
        for ( key in twitterData ) {
           //$scope.objectHeaders.push(property);
           console.log(key);
           currentTotal=twitterData[key];
           currentKey = key; 
        }
        return tweets= currentTotal + "since " + currentKey ; 
    };

    $scope.showCategoryMap= function() {
         var appCategory= $scope.project._category ;
         var popupURL= window.location.protocol + "//" + window.location.host + "/category_map?type=" + appCategory;
         window.open(popupURL,"menubar=no, toolbar=no,location=no, width=700,height=600");  
    };

});