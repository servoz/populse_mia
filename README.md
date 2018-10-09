# populse_mia                                                                                                                            [![](https://travis-ci.org/populse/populse_mia.svg?branch=master)](https://travis-ci.org/populse/populse_mia)        [![](https://ci.appveyor.com/api/projects/status/tk00pnvn08h56dia?svg=true)](https://ci.appveyor.com/project/ouvrierl/populse-mia-rrm4w)                                                                                                                          [![](https://codecov.io/github/populse/populse_mia/coverage.svg?branch=master)](https://codecov.io/github/populse/populse_mia) [![](https://img.shields.io/badge/license-CeCILL-blue.svg)](https://github.com/populse/populse_mia/blob/master/LICENSE) [![](https://img.shields.io/badge/python-3.5%2C%203.6%2C%203.7-yellow.svg)](#) [![](https://img.shields.io/badge/platform-Linux%2C%20OSX%2C%20Windows-orange.svg)](#)

Multiparametric Image Analysis

# Documentation

Available soon
	
# Installation

From PyPI:

    # Available soon

From source:

    # A compatible version of Python must be installed
    sudo apt-get install git
    git clone https://github.com/populse/populse_mia.git /tmp/populse_mia
    cd /tmp/populse_mia
    sudo python setup.py install # Beware that it is the good Python version (use pythonx.x to be sure)
    cd /tmp
    sudo rm -r /tmp/populse_mia

# Usage

Available soon             
	
# Tests

Unit tests written thanks to the python module unittest

Continuous integration made with Travis (Linux, OSX), and AppVeyor (Windows)

Code coverage calculated by the python module codecov

The module is ensured to work with Python >= 3.5

The module is ensured to work on the platforms Linux, OSX and Windows

The script of tests is python/populse_mia/src/scripts/test.py, so the following command launches the tests:
	
	python python/populse_mia/src/scripts/test.py (from populse_db root folder)
	
# Requirements

* SIP
* pyqt5
* pyyaml
* python-dateutil
* sqlalchemy
* lark-parser
* scipy
* nibabel
* snakeviz
* pillow
* matplotlib
* traits
* capsul
* soma_workflow
* nipype
* scikit-image


# Other packages used
  * copy
  * os
  * six
  * tempfile
  * unittest
  
# License
  
  The whole populse project is open source
  
  Populse_mia is precisely released under the CeCILL software license
  
  You can find all the details on the license [here](http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html), or refer to the license file [here](https://github.com/populse/populse_mia/blob/master/LICENSE)
