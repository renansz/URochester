## Project Proposal ##

### Python AST Visualization Tool ###

<b> Goal:</b>
> Make a web app that shows step-by-step how Python's interpreter parse the code into AST as it executes it.

<b> Ideas: </b>
  - Use a animated graphic representation for the AST generated from a specif compiled code.
  - Dinamically generate the tree and the all the steps the compiler take when process it.
  - Show how the tree collapses/expands as the code is executed.

<b> Development: </b>
  - Web app (simulated backend maybe)
  - Based on https://github.com/pgbovine/PythonCompilerWorkbench.
  - Using some animated tree visualization graphic API
    - http://ubietylab.net/ubigraph/ 
    - google graph API

<b> Specific goals: </b>
  - Make a example of this representation with a algebric expression: `z = x * (y - z)` 
  - Make a video or an test environment that can show the idea and functionalities of this AST visualization tool.
