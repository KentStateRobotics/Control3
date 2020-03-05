from setuptools import setup, find_packages
from Cython.Distutils import build_ext
from setuptools.extension import Extension

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='control3',
    description='KSU robot control 3',
    py_modules=['control3', 'networking', 'slam'],
    install_requires=requirements,
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
        Extension("slam.processing", sources = ["slam/processing.cpp"]),
        Extension("slam.cMap", sources = ["slam/map2py.cpp", "slam/map.cpp"])
    ],
    test_suite="tests"
)
