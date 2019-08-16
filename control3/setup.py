import setuptools
from setuptools.extension import Extension
from Cython.Build import cythonize

setuptools.setup(name='control3',
                 description='KSU robot control 3',
                 py_modules=['RMC_Control', 'networking'],
                 setup_requires=['Cython'],
                 install_requires=['websockets', 'pyserial', 'numpy', 'opencv-contrib-python'],
                 zip_safe=False,
                 tests_requires=['timeout-decorator'],
                 entry_points={
                     'console_scripts':[
                         'control3 = control3.control:main',
                         'robot = control3.robot:main'
                     ]
                 })