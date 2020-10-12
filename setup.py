from setuptools import setup, find_packages
from Cython.Distutils import build_ext
from setuptools.extension import Extension

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='KSRCore',
    description='KSU robot control core',
    py_modules=['KSRCore'],
    install_requires=requirements,
    zip_safe=False,
    python_requires='==3.7.*',
    entry_points={
        'console_scripts':[
            'KSRControl = KSRCore.entry:main',
        ]
    },
    cmdclass = {'build_ext': build_ext},
    ext_modules=[
    #    Extension("debugScripts.cythonExtentionTest", ["debugScripts/cythonExtentionTest.pyx"]),
    #    Extension("debugScripts.cExtentionTest", sources = ["debugScripts/cExtentionTest.cpp"])
        Extension("KSRCore.slam.processing", sources = ["KSRCore/slam/processing.cpp"]),
        Extension("KSRCore.slam.cMap", sources = ["KSRCore/slam/map2py.cpp", "KSRCore/slam/map.cpp"])
    ]
)
