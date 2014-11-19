## Python AST Visualization Tool ##

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
  - this program generates the AST,
  - parses it to a format that the d3.js library can plot as a "collapsible" tree
  - generate the json output from that and save it in a place that my webserver read it as its input data
- link to the website: http://renansz.no-ip.org:8080/index3.html
  - It's already collapsible and the step-by-step visualization can be easy done
  - But.... I need a way to store the intermediate steps (show in class)
   
