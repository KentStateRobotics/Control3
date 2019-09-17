import setuptools
from Cython.Distutils import build_ext
from setuptools.extension import Extension

setuptools.setup(name='control3',
                 description='KSU robot control 3',
                 py_modules=['control3', 'networking'],
                 install_requires=['websockets', 'pyserial', 'numpy', 'opencv-contrib-python', 'pygame', 'Cython', 'timeout-decorator', 'pyopengl'],
                 zip_safe=False,
                 entry_points={
                     'console_scripts':[
                         'control3 = control3.control:main',
                         'robot = control3.robot:main'
                     ]
                 },
                 cmdclass = {'build_ext': build_ext},
                 ext_modules=[
                 #    Extension("debugScripts.cythonExtentionTest", ["debugScripts/cythonExtentionTest.pyx"]),
                 #    Extension("debugScripts.cExtentionTest", sources = ["debugScripts/cExtentionTest.cpp"])
                    ]
                )