'use strict';

var app = angular.module('ossrank', ['ngRoute', 'ngResource', 'ossrank.directives', 'chart.js', 'ui.bootstrap'])
    .config(function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'views/main.html',
                controller: 'HomeCtrl'
            })
            .when('/s/:sid', {
                templateUrl: function (params) {
                    return 'views/' + params.sid + '.html';
                },
                controller: 'TaxonomyCtrl'
            })
            .when('/project/:projectId/:filteredRank', {
                templateUrl: 'views/project.html',
                controller: 'ProjectCtrl'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

app.factory('Category', function ($resource) {
    return $resource("/api/categories");
});

app.factory('Project', function ($resource) {
    return $resource("/api/projects/:id");
});
