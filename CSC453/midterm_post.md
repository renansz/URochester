## Concatenating two strings together with the '+' operator

  The goal of this tutorial is to show how the Python compiler (CPython)
implements the '+' operator as string concatenation. In order to show that,
we will trace the execution of the the following python code through the main
loop of the compiler:
```
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
  This code is really simple and just "add" two variables containing respectvely
'str' and 'ing' producing the result 'string' and storing it in a new variable.

  The byte-code has just one line that we are interested in, the **byte offset 18** 
containing the opcode **BINARY_ADD**. If you are familiarized with other Python 
you will notice that this **BINARY_ADD** is the same used anytime a '+' operator
appears in your code. The question is: how could CPython know that we are now
talking about strings and not integers, and that is what we will see in the
next steps.

*** For the purposes of this tutorial we will ignore all the reference counter
increasing / decreasing codes as well as all debugging and exception handling
code. Also, we will not go over all the optimizations that the compiler does
because they are not essential to the understanding of what the '+' operator
does***

            The algorithm used to implement BINARY_ADD looks like this:
```
         case BINARY_ADD:
            w = POP();
            v = TOP();
            if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
                /* INLINE: int + int */
                register long a, b, i;
                a = PyInt_AS_LONG(v);
                b = PyInt_AS_LONG(w);
                /* cast to avoid undefined behaviour
                   on overflow */
                i = (long)((unsigned long)a + b);
                if ((i^a) < 0 && (i^b) < 0)
                    goto slow_add;
                x = PyInt_FromLong(i);
            }
            else if (PyString_CheckExact(v) &&
                     PyString_CheckExact(w)) {
                x = string_concatenate(v, w, f, next_instr);
                /* string_concatenate consumed the ref to v */
                goto skip_decref_vx;
            }
            else {
              slow_add:
                x = PyNumber_Add(v, w);
            }
            Py_DECREF(v);
          skip_decref_vx:
            Py_DECREF(w);
            SET_TOP(x);
            if (x != NULL) continue;
            break;
  ```
  The first thing we need to know is what the CheckExact functions do. It turns
out that they are just a Python's compiler type checking functions. In this 
case, the compiler first tries to do the integer (PyInt_CheckExact) and then
if it fails, it tries to do something else and the next attempt is to see if
the arguments are string types, which they are in our example:
>  v = 'ing'
>  w = 'str'
when the compiler enters this if statement it now calls this string_concatenate
function putting our arguments in it as well as some some other ones: 'f' and 
'next_instr'. 'f' is a reference to the current frame where the main loop is
being executed and 'next_instr' is being processed


```
static PyObject *
string_concatenate(PyObject *v, PyObject *w,
                   PyFrameObject *f, unsigned char *next_instr)
{
    /* This function implements 'variable += expr' when both arguments
       are strings. */
    Py_ssize_t v_len = PyString_GET_SIZE(v);
    Py_ssize_t w_len = PyString_GET_SIZE(w);
    Py_ssize_t new_len = v_len + w_len;
    if (new_len < 0) {
        PyErr_SetString(PyExc_OverflowError,
                        "strings are too large to concat");
        return NULL;
    }

    if (v->ob_refcnt == 2) {
        /* In the common case, there are 2 references to the value
         * stored in 'variable' when the += is performed: one on the
         * value stack (in 'v') and one still stored in the
         * 'variable'.  We try to delete the variable now to reduce
         * the refcnt to 1.
         */
        switch (*next_instr) {
        case STORE_FAST:
        {
            int oparg = PEEKARG();
            PyObject **fastlocals = f->f_localsplus;
            if (GETLOCAL(oparg) == v)
                SETLOCAL(oparg, NULL);
            break;
        }
        case STORE_DEREF:
        {
            PyObject **freevars = (f->f_localsplus +
                                   f->f_code->co_nlocals);
            PyObject *c = freevars[PEEKARG()];
            if (PyCell_GET(c) == v)
                PyCell_Set(c, NULL);
            break;
        }
        case STORE_NAME:
        {
            PyObject *names = f->f_code->co_names;
            PyObject *name = GETITEM(names, PEEKARG());
            PyObject *locals = f->f_locals;
            if (PyDict_CheckExact(locals) &&
                PyDict_GetItem(locals, name) == v) {
                if (PyDict_DelItem(locals, name) != 0) {
                    PyErr_Clear();
                }
            }
            break;
        }
        }
    }

    if (v->ob_refcnt == 1 && !PyString_CHECK_INTERNED(v)) {
        /* Now we own the last reference to 'v', so we can resize it
         * in-place.
         */
        if (_PyString_Resize(&v, new_len) != 0) {
            /* XXX if _PyString_Resize() fails, 'v' has been
             * deallocated so it cannot be put back into
             * 'variable'.  The MemoryError is raised when there
             * is no value in 'variable', which might (very
             * remotely) be a cause of incompatibilities.
             */
            return NULL;
        }
        /* copy 'w' into the newly allocated area of 'v' */
        memcpy(PyString_AS_STRING(v) + v_len,
               PyString_AS_STRING(w), w_len);
        return v;
    }
    else {
        /* When in-place resizing is not an option. */
        PyString_Concat(&v, w);
        return v;
    }
}
```

 
