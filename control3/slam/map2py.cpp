#include<Python.h>
#include"map.h"
#include<stdint.h>

//Map(uint16_t blockSize=256, uint8_t unitSize = 10, uint8_t precision = 5);
PyObject* construct(PyObject* self, PyObject* args, PyObjects* kwds){
    uint16_t blockSize;
    uint8_t unitSize;
    uint8_t percision;

    static char *kwlist = {"blockSize", "unitSize", "percision", NULL};

    PyArg_ParseTupleAndKeywords(args, kwds, "|Hbb", kwlist, &blockSize, &unitSize, &percision);

    Map* map = new Map(blockSize, unitSize, percision);

    PyObject* mapCapsule = PyCapsule_New((void*)map, "MapPtr", NULL);
    PyCapsule_SetPointer(mapCapsule, (void*)map);

    return Py_BuildValue("O", mapCapsule);
}

//std::pair<double, uint8_t> getFromIndice(int x, int y) const;
PyObject* getFromIndice(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    int x, y;

    PyArg_ParseTuple(args, "Oii", &mapArg, &x, &y);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    auto value = map->getFromIndice(x, y);
    return Py_BuildValue("dB", value.first, value.second)
}

//std::pair<double, uint8_t> getFromDistance(double x, double y) const;
PyObject* getFromDistance(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    double x, y;

    PyArg_ParseTuple(args, "Odd", &mapArg, &x, &y);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    auto value = map->getFromDistance(x, y);
    return Py_BuildValue("dB", value.first, value.second)
}

//std::pair<int,int> getIndiceFromDistance(double x, double y) const;
PyObject* getIndiceFromDistance(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    double x, y;

    PyArg_ParseTuple(args, "Odd", &mapArg, &x, &y);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    auto value = map->getIndiceFromDistance(x, y);
    return Py_BuildValue("ii", value.first, value.second)
}

//std::pair<double,double> getDistanceFromIndice(int x, int y) const;
PyObject* getDistanceFromIndice(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    int x, y;

    PyArg_ParseTuple(args, "Oii", &mapArg, &x, &y);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    auto value = map->getDistanceFromIndice(x, y);
    return Py_BuildValue("dd", value.first, value.second)
}

//void setByDistance(double x, double y, double height, uint8_t confidence);
PyObject* setByDistance(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    double x, y, height;
    uint8_t confidence;

    PyArg_ParseTuple(args, "Odddb", &mapArg, &x, &y, &height, &confidence);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->setByDistance(x, y, height, confidence);
    return Py_BuildValue("")
}

//void setByIndice(int x, int y, double height, uint8_t confidence);
PyObject* setByIndice(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    int x, y;
    double height;
    uint8_t confidence;

    PyArg_ParseTuple(args, "Oiidb", &mapArg, &x, &y, &height, &confidence);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->setByIndice(x, y, height, confidence);
    return Py_BuildValue("")
}

//double heightUnitsToMeters(int16_t value) const;
PyObject* heightUnitsToMeters(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    uint16_t value;

    PyArg_ParseTuple(args, "OH", &value);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    return Py_BuildValue("d", map->heightUnitsToMeters(value))
}

//int16_t metersToHeightUnits(double distance) const;
PyObject* metersToHeightUnits(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    double value;

    PyArg_ParseTuple(args, "Od", &value);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    return Py_BuildValue("H", map->metersToHeightUnits(value))
}

//void applyMinHeightIndice(int x, int y, double height);
PyObject* applyMinHeightIndice(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    int x, y;
    double height;

    PyArg_ParseTuple(args, "Oiid", &mapArg, &x, &y, &height);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->applyMinHeightIndice(x, y, height);
    return Py_BuildValue("")
}

//void applyMaxHeightIndice(int x, int y, double height);
PyObject* applyMaxHeightIndice(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    int x, y;
    double height;

    PyArg_ParseTuple(args, "Oiid", &mapArg, &x, &y, &height);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->applyMaxHeightIndice(x, y, height);
    return Py_BuildValue("")
}

//void applyDepthImage(const uint16_t* image, int height, int width, double hFov, double vFov, double x, double y, double z, double rX, double rY, double rZ);
PyObject* applyDepthImage(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;
    Py_buffer image;
    int x, y;
    double height, width, hFov, vFov, x, y, z, rX, rY, rZ;

    PyArg_ParseTuple(args, "Os*iidddddddd", &mapArg, &image, &height, &width, &hFov, &vFov, &x, &y, &z, &rX, &rY, &rZ);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->applyDepthImage(static_cast<uint16_t*>(image.buf), height, width, hFov, vFov, x, y, z, rX, rY, rZ);
    PyBuffer_Release(&image);
    return Py_BuildValue("")
}

//std::pair<int, float*> getPoints();
PyObject* getPoints(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;

    PyArg_ParseTuple(args, "O", &mapArg);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    auto points = map->getPoints();
    return Py_BuildValue("iy#" points.first, static_cast<char*>(points.second), points.first * sizeof(float));
}

//void clear();
PyObject* clear(PyObjecdt* self, PyObject* args){
    PyObject* mapArg;

    PyArg_ParseTuple(args, "O", &mapArg);
    Map* map = (Map*)PyCapsule_GetPointer(mapArg, "MapPtr");

    map->clear();
    return Py_BuildValue("");
}

PyMethodDef cMapFunctions[] = {
    {"construct", (PyCFunction)(void(*)(void))construct, METH_VARARGS | METH_KEYWORDS, 
    "Create Map object"},
    {"getFromIndice", getFromIndice, METH_VARARGS, 
    "Obtain the indivisual voxel described by the locations indice"},
    {"getFromDistance", getFromDistance, METH_VARARGS, 
    "Obtain the indivisual voxel described by the locations real world location"},
    {"getIndiceFromDistance", getIndiceFromDistance, METH_VARARGS, 
    "Find locations map index from its location"},
    {"getDistanceFromIndice", getDistanceFromIndice, METH_VARARGS, 
    "Find locations location from its map indice"},
    {"setByDistance", setByDistance, METH_VARARGS, 
    "Set the indivisual voxel described by its location"},
    {"setByIndice", setByIndice, METH_VARARGS, 
    "Set the indivisual voxel described by its map indice"},
    {"heightUnitsToMeters", heightUnitsToMeters, METH_VARARGS, 
    "Convert the maps height units to meters"},
    {"metersToHeightUnits", metersToHeightUnits, METH_VARARGS, 
    "Convert the meters to the maps height unit"},
    {"applyMinHeightIndice", applyMinHeightIndice, METH_VARARGS, 
    "Provide evidence that this location is at least this tall, found from the endpoints of the vectors"},
    {"applyMaxHeightIndice", applyMaxHeightIndice, METH_VARARGS, 
    "Provide evidence that this location is less tall than this, found by vectors that pass though this location"},
    {"applyDepthImage", applyDepthImage, METH_VARARGS, 
    "Apply the data from a depth camera to update the map"},
    {"getPoints", getPoints, METH_VARARGS, 
    "Get a list of vertxies representing the map, can be given to opengl in point mode"},
    {"clear", clear, METH_VARARGS, 
    "Resets the map data, config stays the same"},
    {NULL, NULL, 0, NULL}
}

struct PyModuleDef cMapModule = {
    PyModuleDef_HEAD_INIT,
    "cMap",
    "A 2d voxel height map",
    -1,
    cMapFunctions
};

PyMODINIT_FUNC PyInit_cMap(void){
    return PyModule_Create(&cMapModule);
}