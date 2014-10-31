## Concatenating two strings together with the '+' operator ##

  The goal of this tutorial is to show how the Python interpreter (CPython) implements the `+` operator as string concatenation. In order to show that, we will trace the execution of the following python source code through the main loop of the interpreter:
``` python
a = 'str'
b = 'ing'
c = a + b
```
which generates this byte-code:
```
1           0 LOAD_CONST               0 ('str')
            3 STORE_NAME               0 (a)

2           6 LOAD_CONST               1 ('ing')
            9 STORE_NAME               1 (b)

3          12 LOAD_NAME                0 (a)
           15 LOAD_NAME                1 (b)
           18 BINARY_ADD          
           19 STORE_NAME               2 (c)
           22 LOAD_CONST               2 (None)
```
This program **adds** two variables `a` e `b` each one containing strings (`'str'` and `'ing'`) and then as the result of this operation it generates a new string `'string'` and stores it in `c`.

For the purposes of this tutorial, we are just interested in how this **"add"** operation is executed. In our byte-code this operation is represented by the *byte offset 18* containing the opcode `BINARY_ADD`. If you are familiar to Python's interpreter you know that `BINARY_ADD` is called anytime the `+` operator appears in your source code independently of the operands' types and the interpreter takes care of doing the right thing (correct operation) in execution time.  

_we will ignore all the reference counter increasing / decreasing operations as well as all debugging and exception handling instructions not relevant to the main execution of `+`. Also, we will not cover most of the optimizations the interpreter does if it doesn't alter significantly the execution path._

So, supposing we are executing the example source code inside the main loop of `ceval.c`, we start our tracing here when it enters the `BINARY_ADD` case inside of the main execution loop. The definition of `BINARY_ADD` is located inside `ceval.c`. Here is a **simplified** version of it (removing all the stuff that we don't need to care about in this tutorial) that will help us to get a macro idea of what it does:
``` c
       case BINARY_ADD:
          w = POP();
          v = TOP();
          if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
          ...
          /* CODE EXECUTED IF the operands are Integers*/
          ...
          }
          else if (PyString_CheckExact(v) && PyString_CheckExact(w)) {
            <b>  x = string_concatenate(v, w, f, next_instr); </b>
              ...
          }
          ...
          SET_TOP(x);
          if (x != NULL) continue;
          break;
  ```
The interpreter first tries to do the integer (arithmetic) `+` checking operands' types  with `PyInt_CheckExact` (not our case). The next attempt is to verify whether the arguments are of type *string*, which is true in our example. It will then enter the `else if` statement, somehow gets the concatenated value, push it onto the stack and then return the result to its caller. The thing to notice here is that `BINARY_ADD` is actually executing just **one really relevant** line of code in which it calls `string_concatenate` - which we are going to inspect next. 

### Tracing the _string_concatenate_ call ###
When the interpreter enters this if statement it calls the `string_concatenate` function located in `ceval.c`. The arguments passed to this function are basically two operands (strings) and references to the current frame and next instruction as it will try to save the concatenation result somewhere indicated by the next `opcode + oparg` (_optimizations_). This is our the **simplified** version of `string_concatenate`:
```c
static PyObject *
string_concatenate(PyObject *v, PyObject *w, PyFrameObject *f, unsigned char *next_instr)
{
  ...
      /* When in-place resizing is not an option. */
      PyString_Concat(&v, w);
      return v;
  ...
}
```
The lines removed from this code are mainly responsible for optimizations and error handling. The original function, for instance, could do the concatenate operation faster if it was called with `+=`, some empty argument or other *inlines* formats. We skip all these lines since our execution doesn't enter any of these alternative paths.

The interpreter will eventually execute `PyString_Concat(&v, w)` (`line 4868` of `ceval.c`) . This function is locate in the `stringobject.c` file and it will then call `string_concat` after confirming that the arguments are  `PyStringObjects`. This `string_concat` function (`line 1015` of `stringobject.c`) take as parameters just the two operands and does the actual concatenation (using the C string values). This function is a little more complex than the previous ones but most of the complexity comes, again, from the exceptions/errors handling, optimizations and more complex cases. The **simplified** version of `string_concat`, removing all the lines we are not interested in, looks like this: 
``` c
static PyObject *
string_concat(register PyStringObject *a, register PyObject *bb)
{
    register Py_ssize_t size;
    register PyStringObject *op;
    ...
    size = Py_SIZE(a) + Py_SIZE(b);
    ...
    op = (PyStringObject *)PyObject_MALLOC(PyStringObject_SIZE + size);
    ...
    PyObject_INIT_VAR(op, &PyString_Type, size);
    ...
    Py_MEMCPY(op->ob_sval, a->ob_sval, Py_SIZE(a));
    Py_MEMCPY(op->ob_sval + Py_SIZE(a), b->ob_sval, Py_SIZE(b));
    op->ob_sval[size] = '\0';
    return (PyObject *) op;
    ...
}

```
In our simple example, we can skip almost all the original function code and go straight to the `line 1042` in the `stringobject.c` file where the interpreter calculates the needed memory space to allocate the resulting string and store it in this `size` variable that we are going to use few steps ahead: `size = Py_SIZE(a) + Py_SIZE(b)`
  
The interpreter then executes the next lines which are the ones mentioned above but as they are doing the core operation of our trace, i.e., the actual string concatenation, they are described in more detail:

1) ` PyObjectMALLOC(PyStringObject_SIZE + size)`

Allocates sufficient memory to store the resulting PyObject:  ( PyString Size (headers)  + `size` calculated above). This memory is allocated to the `op` object which in turn will be the returning PyString object.

2) `Py_MEMCPY(op->ob_sval, a->ob_sval, Py_SIZE(a))`

`Py_MEMCPY` is a macro that calls the `memcpy` C function. We can find its definition in the `pyport.h` file. The arguments passed to this macro are: `Py_MEMCPY(_target,source,length_)`. So, this line is basically saying that it will copy `Py_SIZE(a)` characters from the value of `a` (which is the actual C string inside the `a->sval`) to the new object `op->sval`.

3) `Py_MEMCPY(op->ob_sval + Py_SIZE(a), b->ob_sval,Py_SIZE(b)) `

The same macro is executed here but with different arguments as it needs to start copying the characters from `b->sval` to `op->sval` just after the last character already copied on the previous step, i.e., it needs to copy `Py_SIZE(b)` bytes to `op->sval` starting on the byte offset indicated by `op->sval + Py_Size(a)`.

4) `op->ob_sval[size] = '\0'`

At this point the string concatenation is already finished. `op->sval` has the `"string"` value but, as we all know, in the end it's all C under the hood and when we work with C strings we need to follow the C conventions. In this case, putting the `'\0'` character to indicate that the string ends here so that the interpreter can use this value as a regular C string.

The new object `op` is then returned to the caller and the interpreter eventually gets back to `ceval.c` returning the new string and storing it in `c` as indicated in our python source code.
