# Control3
2020 RMC Robot controller.

# Setup
Install python 3 https://www.python.org/downloads/
Make sure to check the box to automaticly add python to your path during the install.
Depending on your system, python may be need to be ran using the commands py or python3.

```
cd control3
pip install -r requirements.txt
python setup.py develop
or
python setup.py install
```

# Usage
Remote control client/host:
```
usage: control3 [-h] [-n NAME] [-c] [-p PORT] [-d DISCOVERY PORT] [-a HOST]
optional arguments:
  -h, --help         show this help message and exit
  -n NAME            id used over network, first 10 characters must be unique, default: host
  -c                 is this the network client, defaults to host
  -p PORT            port to communicate over, default: 4242
  -d DISCOVERY PORT  port to preform network discovery over, default: 4243
  -a HOST            address to connect to host, or host name if discovery is
                     being used
```

Robot controller:
```
usage: robot [-h] [-n NAME] [-p PORT] [-d DISCOVERY PORT] [-a HOST]
optional arguments:
  -h, --help         show this help message and exit
  -n NAME            id used over network, first 10 characters must be unique, default: robot
  -p PORT            port to communicate over, default: 4242
  -d DISCOVERY PORT  port to preform network discovery over, default: 4243
  -a HOST            address to connect to host, or host name if discovery is
                     being used
```

# Testing
Automated unit tests are put in the control3/testes directory and should be named test____.py to be found by automatic test discovery. Use -b to suppress print statements, remove so see print statements

```
python setup.py test
```
or
```
py setup.py test
```
# Maintance
New exteral library dependencies from PyPI must be added to requirements.txt and setup.py under install_requires

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
