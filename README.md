# Control3.0
2020 RMC Robot controller.

# Setup
Install python 3 https://www.python.org/downloads/
Make sure to check the box to automaticly add python to your path during the install

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
Automated unit tests are put in the control3/testes directory and should be named test____.py to be found by automatic test discovery

```
cd control3/tests
python -m unittest
```

# Maintance
New exteral library dependencies from PyPI must be added to requirements.txt and setup.py
