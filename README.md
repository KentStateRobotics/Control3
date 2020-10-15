# KSRCore
2021 Robot controller and remote manager\
Python with C++ extensions\

### Design Goles:
 - Compadable with Windows and Ubuntu on both AMD64 and ARM processors\
 - Easy for inexperienced programemrs to start contributing
 - Minimize setup complexity
 - Reliable and testable

# Setup
Install python 3 https://www.python.org/downloads/\
Make sure to check the box to automaticly add python to your path during the install.\
Depending on your system, python may be need to be ran using the commands py or python3.\
\
Downloading the repository
```
git clone https://github.com/KentStateRobotics/KSRCore.git
cd KSRCore
git submodule init
git submodule update
```
```
pip install -r requirements.txt
python3 setup.py develop
or
python3 setup.py install
```

### Generate Documentation
```
pdoc --html --output-dir docs KSRCore  
```

# Usage
Remote control client/host:
```
usage: KSRControl [-h] [-r ROBOT] [-s Server] [-p PORT] [-a ADDRESS] [-l LOGFILE]
optional arguments:
  -h, --help    show this help message and exit
  -r ROBOT   Is this a robot? Defaults to controller
  -s Server  Is this a server? Defaults to client
  -p PORT       Port to communicate over, default: 4242
  -a ADDRESS    Address to connect to host if discovery is not being used
  -l LOGFILE   File to store logs in
```

# Testing
Automated unit tests are put in the KSRCore/tests directory and should be named test_######.py to be found by automatic test discovery. Use -b to suppress print statements.
```
pytest
```

# Maintance
New exteral library dependencies from PyPI must be added to requirements.txt

# Extension
Added new Cython modules or c extensions can be done by adding an extension to the setup.py file. Under ext_modules like so:
```
ext_modules=[
  Extension("directory.cythonModule", ["directory/cythonModule.pyx"]),
  Extension("directory.cExtension", sources = ["directory/cExtension.cpp"], )
]
```
More details on c extensions:
https://docs.python.org/3/extending/extending.html
https://docs.python.org/3/extending/building.html
http://www.speedupcode.com/c-class-in-python3/

More details on Cython:
https://cython.readthedocs.io/en/latest/index.html
