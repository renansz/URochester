## Concatenating two strings together with the '+' operator

  The goal of this tutorial is to show how the Python compiler (CPython) implements the '+' operator as string concatenation. In order to show that, we will trace the execution of the the following python code through the main loop of the compiler:
```python
a = 'str'
b = 'ing'
c = a + b
```
and its respective byte-code:
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
What this code does is **adds** two variables `a` e `b` each one containing strings (`'str'` and `'ing'`) and as result of this operation it generates a new concatenated string `'string'` and store it in `c`.

For the purposes of this tutorial, we are just interested in how this **"add"** operation is executed by CPython. In the our byte-code this operation is represented by the *byte offset 18* containing the opcode `BINARY_ADD`. If you are familiar to Python's compiler you know that `BINARY_ADD` is called anytime the `+` operator appears in your source code independently of the operands' types and the compiler takes care of doing the right thing (correct operation) in execution time.  

_we will ignore all the reference counter increasing / decreasing stuff as well as all debugging and exception handling not relevant to the main execution of `+`. Also, we will not go over most of the optimizations the compiler does if it doens't alter significantly the execution path._

  So, supposing we are executing the code example, we start this trace when it enters the `BINARY_ADD` case inside of the mais loop. The definition of `BINARY_ADD` is located inside *ceval.c*. Here is a **simplified** version (removing all the stuff that we don't need to care about in this tutorial) of it that will help us to get a macro definition of what it does:
```C
       case BINARY_ADD:
          w = POP();
          v = TOP();
          if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
          ...
          /* CODE EXECUTED IF the operands are Integers*/
          ...
          }
          else if (PyString_CheckExact(v) && PyString_CheckExact(w)) {
              x = string_concatenate(v, w, f, next_instr);
              ...
          }
          ...
          SET_TOP(x);
          if (x != NULL) continue;
          break;
  ```
In this case, the compiler first tries to do the integer (arithimetic) `+` checking operands' types  with `PyInt_CheckExact` and then if it fails, in the next attempt it verifies whether the arguments are of type *string*, which they are in our code. It then enters the if statement, somehow gets the concatenated value, push it onto the satack and the return.
The thing to notice here is that `BINARY_ADD` is actually executing just *one really relevant* line of code in which it calls `string_concatenate` which we are going to inspect next. 
When the compiler enters this if statement it calls the `string_concatenate` function located in `ceval.c`. The arguments passed to this function are basically the string operands and references to the current variable names and next instruction as it will save the concatenation result somewhere indicated by the next `opcode + oparg`. In our case, the next opcode is `STORE_NAME` which means that the return value will be stored in the variable `c` indicated in its oparg variable but we don't need to worry about this right now.
This is our the **simplified** version of `string_concatenate`:
```C
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
We are omitting several lines of code that are responsible for optimizations and error handling. The original function, for instance, could do the concatenae operation right away if it was called with `+=` or some other *inline* formats of it. We skip all of it since our execution doesn't enter there. The compiler will end up executing the `PyString_Concat(&v, w)` (`line 4868` of `ceval.c`) . This function takes us to the `stringobject.c` file and `PyString_Concat(&v, w)` will then call `string_concat` after confrming that the arguments are  `PyStringObjects`. This last  `string_concat` function (`line 1015` of `stringobject.c`) take as parameters just the operands and does the actual concatenation. This function is a little more complex than the previous ones but most of the complexity comes from the exceptions/errors handling and some optimizations.
The **simplified** version of `string_concat`, removing all the lines we are not interested in, looks like this: 
````C
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
As our example is simple, we can skip almost all the original function code and go straight to `line 1042` in the `stringobject.c` file where the compiler calculates the necessary size of the resulting string and store it in this `size` variable that we are going to use few steps ahead: `size = Py_SIZE(a) + Py_SIZE(b)`
  
Then the compiles continues its execution going over all the next lines. Again, we are just interested on the actual concatenation, so we are going to examie just these lines:

1. ` PyObjectMALLOC(PyStringObject_SIZE + size) `
Allocating memory of sufficient size to store the resulting PyObject  - standard PyString size (header)  + calculated `size` of the two strings. This memory is allocated to `op` which in turn will be the resulting string.

2. `Py_MEMCPY(op->ob_sval, a->ob_sval, Py_SIZE(a)) `
`Py_MEMCPY` is a macro that calls the `memcpy` C function. We can find its definition in the `pyport.h` file. The arguments passed to this macro are: `Py_MEMCPY(_target,source,length_)`. So, this line is basically saying that it will copy `Py_SIZE(a)` characters from the value of `a` (which is the actual C string inside the `sval` field of the object) to the new object's `sval`.

3. `Py_MEMCPY(op->ob_sval + Py_SIZE(a), b->ob_sval,Py_SIZE(b)) `
The same occurs here with a slightly difference as it needs to start to copy the characters from `b` to `op->sval` starting after the last character already copied on the previous step, i.e., it copies `Py_SIZE(b)` bytes to the offset starting in `op->sval + Py_Size(a)` position.

4. `op->ob_sval[size] = '\0'`
At this point the string concatenation is already finished but, as we all know, in the end it's all C under the hood so we need to follow the some C conventions sometimes. In this case, put the `'\0'` character to indicate that the string ends here so the C string value can be used by the compiler as a regular string.

The new object `op` is then returned to the caller and the compiler eventually gets back to `ceval.c` returning the new string and storing it in `c` as indicated in our python source code.
