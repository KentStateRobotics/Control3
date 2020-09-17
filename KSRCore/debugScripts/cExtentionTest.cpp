#include <Python.h>

static PyObject *add(PyObject *self, PyObject *args){
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
      return NULL;
   }

    return Py_BuildValue("i", a + b);
}

static char add_docs[] = "Add some ints\n";


static PyMethodDef addMethods[] = {
    {"add",  add, METH_VARARGS,
     "Do an add."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef addmodule = {
    PyModuleDef_HEAD_INIT,
    "add",   /* name of module */
    add_docs, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    addMethods
};

PyMODINIT_FUNC
PyInit_cExtentionTest(void) {
   return PyModule_Create(&addmodule);
}