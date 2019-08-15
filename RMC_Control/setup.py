import setuptools
from setuptools.extension import Extension
from Cython.Build import cythonize

setuptools.setup(name='RMC_Control',
                 description='KSU RMC control',
                 py_modules=['RMC_Control', 'networking'],
                 setup_requires=['Cython'],
                 install_requires=['websockets', 'pyserial', 'numpy', 'opencv-contrib-python'],
                 zip_safe=False,
                 tests_requires=['timeout-decorator'],
                 entry_points={
                     'console_scripts':[
                         'RMC_Control = RMC_Control.control:main',
                         'RMC_Robot = RMC_Control.robot:main'
                     ]
                 })