angular.module('ossrank.directives',[]).directive('autoComplete',['$http',function($http){
    return {
        restrict:'AE',
        scope:{
            selectedTags:'=model'
            
        },
        templateUrl:'views/autocomplete-template.html',
        link:function(scope,elem,attrs){

            scope.suggestions=[];

            scope.selectedTags=[];

            scope.selectedIndex=-1;

            scope.projects = {};

            scope.filteredProjects = {};

            scope.numPages= 0;

            scope.projectPerPage = 10;

            scope.currentPage = 1;
            
            scope.removeTag=function(index){
                scope.selectedTags.splice(index,1);
            }
            
            scope.getProjects=function() {
                tags = scope.selectedTags.join();
                console.log(tags) ;
                //alert(attrs.url);
                //scope.tags2 = tags ;

                $http.get('/api/projects'+'?tags='+tags).success(function(response){
                    scope.projects=response.projects;
                    console.log(scope.projects.length);
                    scope.numPages= Math.ceil(scope.projects.length / scope.numPerPage);
                    
                });
                
            }

            

            scope.search=function(){
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

            scope.$watch('selectedIndex',function(val){
                if(val!==-1) {
                    scope.searchText = scope.suggestions[scope.selectedIndex];
                }
            });
           /**scope.$watch('currentPage + numPerPage', function() {
             var begin = ((scope.currentPage - 1) * scope.numPerPage)
            , end = begin + scope.numPerPage;
            scope.filteredProjects = scope.projects.slice(begin, end);
            });**/
        }
    }
}]);