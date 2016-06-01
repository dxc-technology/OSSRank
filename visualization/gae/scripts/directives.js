angular.module('ossrank.directives', []).directive('autoComplete', ['$http', function ($http) {
        return {
            restrict: 'AE',
            scope: {
                selectedTags: '=model',
            },
            templateUrl: 'views/autocomplete-template.html',
            link: function (scope, elem, attrs) {

                scope.suggestions = [];

                // Try loading selectedTags from sessionstorage
                savedTags = angular.fromJson(window.sessionStorage.getItem("selectedTags"));
                scope.selectedTags = savedTags ? savedTags : [];

                // Now try loading saved projects
                matchingProjects = angular.fromJson(window.sessionStorage.getItem("matchingProjects"));
                scope.projects = matchingProjects ? matchingProjects : [];

                scope.selectedIndex = -1;

                scope.tags = '';

                scope.itemsPerPage = 10

                scope.currentPage = 1;


                //max number of pagination
                scope.maxSize = 15;


                scope.removeTag = function (index) {
                    scope.selectedTags.splice(index, 1);
                    // Send tags to find matching projects
                    scope.getProjects();
                }

                scope.getProjects = function () {
                    // first, empty results list just in case
                    scope.projects = {};
                    scope.filteredProjects = {};
                    tags = scope.selectedTags.join('|');
                    // Persist selected tags
                    window.sessionStorage.setItem("selectedTags", angular.toJson(scope.selectedTags));
                    if (tags.length < 1) {
                        return;
                    }
                    console.log(tags);
                    $http.get('/api/projects' + '?filter=1&tags=' + tags).success(function (response) {
                        scope.projects = response.projects;

                        // Add an attribute for rank withing filtered results
                        for (i = 0; i < scope.projects.length; i++) {
                            scope.projects[i].filteredRank = i + 1;
                        }

                        // Persist matching projects
                        window.sessionStorage.setItem("matchingProjects", angular.toJson(response.projects));
                        if (typeof response.projects === 'undefined' || typeof response.projects.length === 'undefined') {
                            return;
                        }

                        console.log(scope.projects.length);
                        scope.totalItems = scope.projects.length;
                        scope.filteredProjects = scope.projects.slice(0, 10);
                        scope.pageCount = function () {
                            return Math.ceil(scope.projects.length / scope.itemsPerPage);
                        };

                    });
                }

                scope.search = function () {
                    $http.get(attrs.url + '?term=' + scope.searchText).success(function (data) {
                        if (data.indexOf(scope.searchText) === -1) {
                            data.unshift(scope.searchText);
                        }
                        scope.suggestions = data;
                        scope.selectedIndex = -1;
                    });
                }

                scope.addToSelectedTags = function (index) {
                    if (scope.selectedTags.indexOf(scope.suggestions[index]) === -1) {
                        scope.selectedTags.push(scope.suggestions[index]);
                        scope.searchText = '';
                        scope.suggestions = [];
                        // Send tags to find matching projects
                        scope.getProjects();
                    }
                }



                scope.checkKeyDown = function (event) {
                    if (event.keyCode === 40) {
                        event.preventDefault();
                        if (scope.selectedIndex + 1 !== scope.suggestions.length) {
                            scope.selectedIndex++;
                        }
                    } else if (event.keyCode === 38) {
                        event.preventDefault();
                        if (scope.selectedIndex - 1 !== -1) {
                            scope.selectedIndex--;
                        }
                    } else if (event.keyCode === 13) {
                        scope.selectedIndex = scope.selectedIndex >= 0 ? scope.selectedIndex : 0;
                        console.log("selected::" + scope.selectedIndex);
                        scope.addToSelectedTags(scope.selectedIndex);
                    }
                }

                scope.pageChanged = function (page) {
                    scope.currentPage = page;
                    console.log('Page changed to: ' + scope.currentPage);
                    //console.log('number  of projects' + scope.projects.length);
                };

                scope.$watch('selectedIndex', function (val) {
                    if (val !== -1) {
                        scope.searchText = scope.suggestions[scope.selectedIndex];
                    }
                });
                scope.$watch('currentPage + itemsPerPage', function () {
                    var begin = ((scope.currentPage - 1) * scope.itemsPerPage),
                        end = begin + scope.itemsPerPage;
                    scope.filteredProjects = scope.projects.slice(begin, end);
                });
            }
        }
}])
    .directive('loading', ['$http', function ($http)
        {
            return {
                restrict: 'A',
                link: function (scope, elm, attrs) {
                    scope.isLoading = function () {
                        return $http.pendingRequests.length > 0;
                    };

                    scope.$watch(scope.isLoading, function (v) {
                        if (v) {
                            $(elm).show();
                        } else {
                            $(elm).hide();
                        }
                    });
                }
            };

    }]);
