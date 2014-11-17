## Python AST Visualization Tool ##

### Python's AST Basics ###

<b> What is AST? </b>
  - AST stands for Abstract Syntax Tree. It's basically the tree structure of a python's compiled code. Everytime you run a python code you are actually pre-compiling it in bytecode and then give this bytecode to the interpreter work on it.
  - The syntax tree is the tree object that generates this byte code.
  
<b> How do I get the AST out of a python source code? </b>
  - Using the "ast" lib, and then running 'ast.parse(filename.py)

<b> How's the AST structure? </b>
  - Every node object is a ast.AST object and they can be of many types, such as BinOp, Num, Store, Name, Assign, etc.
  - There are some generic and specific attributes in each node type
  - '_fields is a attribute that each concrete class has. This attributes contains the names of all child nodes of the node.

<b> Ideas: </b>
  - Use a animated graphic representation for the AST generated from a specif compiled code.
  - Dinamically generate the tree and the all the steps the compiler take when process it.
  - Show how the tree collapses/expands as the code is executed.
  
<b> How to generate a AST:</b>
> Make a web app that shows step-by-step how Python's interpreter parse the code into AST as the code gets executed.

<b> Ideas: </b>
  - Use a animated graphic representation for the AST generated from a specif compiled code.
  - Dinamically generate the tree and the all the steps the compiler take when process it.
  - Show how the tree collapses/expands as the code is executed.

<b> Implementation Details: </b>
  - Web app (simulated backend maybe)
  - Based on https://github.com/pgbovine/PythonCompilerWorkbench.
  - Using some animated tree visualization graphic API
    - http://ubietylab.net/ubigraph/ 
    - http://bl.ocks.org/mbostock/4339083

<b> Specific goals (measurement): </b>
  - Make a example of this representation with the algebric expression: `z = x * (y - z)` 
  - Make a video or a test environment that can show the idea and functionalities of this AST visualization web app.
