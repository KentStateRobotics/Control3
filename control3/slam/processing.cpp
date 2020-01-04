#include <Python.h>
#include <algorithm>
#include <iostream>

static PyObject *depthToGray(PyObject *self, PyObject *args){
    Py_buffer a;
    if (!PyArg_ParseTuple(args, "s*", &a)) {
      return NULL;
    }
    for(int i = 0; i < (a.len / 2); ++i){
        unsigned short value = static_cast<unsigned short*>(a.buf)[i];
        static_cast<unsigned short*>(a.buf)[i] = std::min(255, unsigned short(value / 256) + 100);
    }
    PyBuffer_Release(&a);
    return Py_None;
}

static PyObject *processFrame(PyObject *self, PyObject *args){
    std::cout << "processFrame" << std::endl;
    return Py_None;
}

//Module defs
static PyMethodDef processFrame_methods[] = {
    {"processFrame",  processFrame, METH_VARARGS,
     "Take depth frame and compute voxle"},
    {"depthToGray",  depthToGray, METH_VARARGS,
     "Convert depth data into grayscale image"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef processing_module = {
    PyModuleDef_HEAD_INIT,
    "processFrame",   /* name of module */
    "Work with depth frames that python cannot effectnly handle\n", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    processFrame_methods
};

PyMODINIT_FUNC
PyInit_processing(void) {
   return PyModule_Create(&processing_module);
}