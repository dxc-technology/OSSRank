angular.module('ossrank.filters',[]).filter('string2array', function()
        {
            return function(string){
       var strArray = string.split(',');
       console.log("hello");
       return strArray;    //converted as array.
   }
 });