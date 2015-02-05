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

app.controller("ProjectCtrl", function ($scope, $routeParams, Project) {
    $scope.proj = "Project";

    $scope.projectId = $routeParams.projectId;
    console.log($scope.projectId);

    var project = Project.get({
        id: $scope.projectId
    }, function () {
        console.log(project);
        $scope.project = project.project;
    });

});