(function () {
    
     //get users query param
     function get(name){
        if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
        return decodeURIComponent(name[1]);
      }
  
     //get data from mongo
     function httpGet()
      {
        var xmlHttp = null;
        var fetchType= get('type');
        
        //-- start prepare query url---
        //todo ::below values to be loaded from config
         var apiURL = "https://api.mongolab.com/api/1/databases/";
         var databaseName="ossrank";
         var collectionName="projects";
         var apiKeyVal="HNkm0J4u8WLmYlAJvqetUmMcumzel9vO";
         //to be loaded from config

         query_str="&q={'_category':'"+fetchType+"'}";
         query_url=apiURL+databaseName+"/collections/"+collectionName
        + "?apiKey="+apiKeyVal  
        +  query_str  
        + '&f= {"name":1,"_rank":1}' 
        +  '&s= {"_rank":-1} ';

        //--  end prepare query url

        
        xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", query_url, false );
        xmlHttp.send( null );
        return xmlHttp.responseText;
      }
    
     //draw the bubble chart
     var diameter = 600;
     var svg = d3.select('#graph').append('svg').attr('width', diameter).attr('height', diameter).attr('class','bubble');
     var bubble = d3.layout.pack().size([
        diameter,
        diameter
    ]).value(function (d) {
        return d.size;
    }).padding(3);
    
    var nodes = bubble.nodes(processData()).filter(function (d) {
        return !d.children;
    });
    var vis = svg.selectAll('g.node').data(nodes);
    vis.enter().append("g").attr("class", "node");
    vis.append("title").text(function(d) { return d.className; }); 
    vis.append('circle').attr('transform', function (d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    }).attr('r', function (d) {
        return d.r;
    }).attr('class', function (d) {
        return d.className;
    }).attr('style',function(){

     //get random colors for the bubbles
     var myColors = ['fill:green', 'fill:aquamarine', 'fill:purple','fill:red','fill:lime','fill:pink'];    
     var rand = myColors[Math.floor(Math.random() * myColors.length)];
     return rand;
     });

   //add text anchor in the middle of the bubble  
   vis.append("text").attr("text-anchor", "middle").attr("dx", function (d) { return d.x;}).attr("dy", function (d) { return d.y;}).text(function(d) { return d.className; });
    //process json data     
    function processData() {
         json = httpGet();
         obj = json;
         var newDataSet = [];
         p = JSON.parse(json);
         for (var key in p) {
        if (p.hasOwnProperty(key)) {
           // this is the visble text in the bubble
           var name = p[key]['name'] + "/" + p[key]['_rank'] ;
           //use rank to create bubble sizes
           var rank = p[key]['_rank']/1000 ;
           newDataSet.push({
                name: p[key]['name'],
                className: name.toLowerCase(),
                size: rank
            });
        }
       }
       return { children: newDataSet };
    }
}());
