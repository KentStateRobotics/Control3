#include <Python.h>

static PyObject *add(PyObject *self, PyObject *args){
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
      return NULL;
   }

    return Py_BuildValue("i", a + b);
}