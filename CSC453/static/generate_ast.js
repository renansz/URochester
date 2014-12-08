var margin = {top: 120, right: 20, bottom: 120, left: 20},
    width = 1280 - margin.right - margin.left,
    height = 1080 - margin.top - margin.bottom;
    
var i = 0,
    duration = 750,
    root;
    
var rectSize = 50;

var tree = d3.layout.tree()
    .size([height, width]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.x, d.y]; });

var svg = d3.select(".container").append("svg")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
assert(typeof(svg) == "object","graphic placeholder not generated");

d3.json('/get_ast', function(error, ast) {
    assert(typeof(ast) == "object", "JSON query didn't return a object");
    root = ast;
    root.y0 = height / 2;
    root.x0 = 0;
    function collapse(d) {
      var aux = ''; 
      if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
      }
    }
  root.children.forEach(collapse);
  update(root);
});

d3.select(self.frameElement).style("height", "auto");

function update(source) {
  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
      links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Update the nodes…
  var node = svg.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node.enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.x0 + "," + source.y0 + ")"; })
      .on("click", click);

  nodeEnter.append("rect")
      .attr("class","node")
      .attr("x", function(d) { return  -rectSize/2;  })
      .attr("y", function(d) { return  -rectSize/2;  })
      .attr("width", rectSize)
      .attr("height", rectSize)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeEnter.append("text")
      .attr("x", function(d) { return -rectSize/2 ; })
      .attr("dy", ".15em")
      .attr("text-anchor", "right")
      .text(function(d) { console.log("text: "+ d.name);return d.name; })
      .style("fill-opacity", 1e-6);

  //Toggling collapsed and open form
  if (source.children == null && source.collapsed != undefined){
      source.temp = source.name; 
      source.name = source.collapsed;
  }
  if (source.children != null && source.collapsed != undefined && source.temp != undefined){
     source.name = source.temp;
  }

  // Transition nodes to their new position.
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

  nodeUpdate.select("text")
    .style("fill-opacity", 1)
    .text(function(d) { return d.name; });
  
// Transition exiting nodes to the parent's new position.
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.x + "," + source.y + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6);

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links…
  var link = svg.selectAll("path.link")
      .data(links, function(d) { return d.target.id; });

  // Enter any new links at the parent's previous position.
  link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      });

  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}

// Expand all nodes.
function expand_all(d){
    if (d.children != undefined) {
        d.children.forEach(function(e){
            click(e);
            expand_all(e);
        });
    }
}

//Starts all expanded
function initial_state(){
    expand_all(root);
}

function try_initialize(){    
    if (typeof(root) == "undefined") 
        setTimeout(try_initialize,1000);
    else
        initial_state();
}

try_initialize();
