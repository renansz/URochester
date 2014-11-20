>This blog post is about Python's AST and how one can visualize it in order to improve the understanding of the internals of Python interpreter.
>First I want to talk a little bit about the AST itself giving you some concepts and definitions and then show you the motivation for this project as well as the implementation process and the actual code.
>Hopefully there will be a live demo when I finish this post, so you can test and see what I am talking about here.

### Python's AST Basics ###

<b> What is AST? </b>
  - AST stands for Abstract Syntax Tree. It's basically the tree structure of a python's compiled code. Everytime you run a python code you are actually pre-compiling it in bytecode and then give this bytecode to the interpreter work on it.
  - The syntax tree is the tree object that generates the byte code that the interpreter reads in order to execute the program.
  
<b> How do I get the AST out of a python source code? </b>
  - Using the "ast" lib `import ast`,
  - and then running `ast.parse(filename.py)`

<b> How does the AST structure look like? </b>
  - It's a tree structure
  - Every node object is a `ast.AST` subtype and they can be of many types, such as `BinOp`, `Num`, `Store`, `Name`, `Assign`, etc.
  - There are <b>generic</b> and <b>specific</b> attributes in each node type
  - `_fields` is a attribute that each concrete class has. This attribute contains all of the names of a node's children.
  - `TO-DO`<b>MISSING THE SPECIFIC FIELDS FOR THE TYPES I'M USING</b>

<b> How to visualize the AST: </b>
  - Python has a way to visit all the nodes of a AST but has no visualization for it.
  - This project proposes a way to plot ASTs in an comprehensive way so that people can understand how Python parse their code.
  - A step-by-step approach would be nice as it can show the sequence of instructions that Python executes in order to get the expected result.

> The "how to visualize AST" topic gives us an ideia of how not trivial it is to start working with the Python's parsing tree. This is the motivation of this project.
  
## Python AST Visualization Tool ##
> This project aims to help students visualizing the AST strucutre of a python code using a web interface.

#### Proposal ####
<b> How to generate a AST:</b>
> Make a web app that shows step-by-step how Python's interpreter parse the code into AST as the code gets executed.

<b> Ideas: </b>
  - Use a animated graphic representation for the AST generated from a specif compiled code.
  - Dinamically generate the tree and the all the steps the compiler take when process it.
  - Show how the tree collapses/expands as the code is executed.

<b> Implementation Details: </b>
  - Web app (simulated backend maybe, just hosting a page)
  - Based on https://github.com/pgbovine/PythonCompilerWorkbench.
  - Using some animated tree visualization graphic API
    - http://bl.ocks.org/mbostock/4339083 (d3.js library)

<b> Specific goals (measurement): </b>
  - Make a example of this representation with the algebric expression: `z = x * (y - z)` 
  - Make a video or a test environment that can show the idea and functionalities of this AST visualization web app.


#### What's been done so far ####
- python code: `tree.py` hosted in github
  - this program generates the `AST`,
  - parses it to a format that the `d3.js` library can plot as a "collapsible" tree
  - generate the `JSON` output from a given input and save it in a place that my webserver reads it as its input data
  - the webpage then just renders it making use of the `d3.js` tree visualization type.
- link to the website: http://renansz.no-ip.org:8080/index3.html
  - It's already collapsible/expandable and the step-by-step visualization can be easily done.
   
#### Next steps ####
- The expand/collapse actions are working but not as I intended to.
- I need to recursively walk through all the nodes in the same sequence as the python byte code generator in order to get the intermediate results right.
  - Ex: `x + ( y + z )`
    - The deepest `BinOp` node should display `y + z` when collapsed and the parent BinOp should display `x + ( y + z )` when collapsed.
    - When expanded they all should display their "ast" type as their labels.
    - I want to do the same with all the `Store`, `Load`, `Assign`, etc codes, but I think they will be easy when the `BinOps` were done.
  - Make sure that the interface is dumb. Don't put logic on javascript (maybe just the expanded/collapsed conditions)
  - Use assertions on the code to verify the steps and also make it easier to implement future `ast` types
  - The initial state should be all expanded.
