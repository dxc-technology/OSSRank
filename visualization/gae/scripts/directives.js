angular.module('ossrank.directives',[]).directive('autoComplete',['$http',function($http){
    return {
        restrict:'AE',
        scope:{
            selectedTags:'=model',
        },
        templateUrl:'views/autocomplete-template.html',
        link:function(scope,elem,attrs){

            scope.suggestions=[];

            scope.selectedTags=[];

            scope.selectedIndex=-1;

            scope.tags='';

            scope.itemsPerPage = 10

            scope.currentPage = 1;

            scope.projects = [];

            //max number of pagination 
            scope.maxSize= 15;


            scope.removeTag=function(index){
                scope.selectedTags.splice(index,1);
                // Send tags to find matching projects
                scope.getProjects();
            }
            
            scope.getProjects=function() {
                tags = scope.selectedTags.join('|');
                console.log(tags);
                $http.get('/api/projects'+'?filter=1&tags='+tags).success(function(response){
                scope.projects=response.projects;
                console.log(scope.projects.length);
                scope.totalItems= scope.projects.length;
                scope.filteredProjects = scope.projects.slice(0,10);

                scope.pageCount = function () {
                 return Math.ceil(scope.projects.length / scope.itemsPerPage);
                };

                    
                });
            }

            scope.search=function() {
                // search only for 3 or more characters
                if (scope.searchText.length < 3)
                    return;
                
                $http.get(attrs.url+'?term='+scope.searchText).success(function(data){
                    if(data.indexOf(scope.searchText)===-1){
                        data.unshift(scope.searchText);
                    }
                    scope.suggestions=data;
                    scope.selectedIndex=-1;
                });
            }

            scope.addToSelectedTags=function(index){
                if(scope.selectedTags.indexOf(scope.suggestions[index])===-1){
                    scope.selectedTags.push(scope.suggestions[index]);
                    scope.searchText='';
                    scope.suggestions=[];
                    // Send tags to find matching projects
                    scope.getProjects();
                }
            }

            

            scope.checkKeyDown=function(event){
                if(event.keyCode===40){
                    event.preventDefault();
                    if(scope.selectedIndex+1 !== scope.suggestions.length){
                        scope.selectedIndex++;
                    }
                }
                else if(event.keyCode===38){
                    event.preventDefault();
                    if(scope.selectedIndex-1 !== -1){
                        scope.selectedIndex--;
                    }
                }
                else if(event.keyCode===13){
                    scope.addToSelectedTags(scope.selectedIndex);
                }
            }

             scope.pageChanged = function(page) {
               scope.currentPage = page ;
               console.log('Page changed to: ' + scope.currentPage);
               //console.log('number  of projects' + scope.projects.length);
             };

            scope.$watch('selectedIndex',function(val){
                if(val!==-1) {
                    scope.searchText = scope.suggestions[scope.selectedIndex];
                }
            });
            scope.$watch('currentPage + itemsPerPage', function() {
                var begin = ((scope.currentPage - 1) * scope.itemsPerPage),
                end = begin + scope.itemsPerPage;
                scope.filteredProjects = scope.projects.slice(begin, end);
            });
        }
    }
}]);
