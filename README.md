<p align="center" >
	<img src="https://github.com/populse/populse_mia/blob/master/python/populse_mia/sources_images/Logo_populse_mia.jpg" alt="populse_mia logo" height="220" width="300">
	<sub><sub> ©Johan Pietras @IRMaGe </sub></sub>
</p>

[![](https://travis-ci.org/populse/populse_mia.svg?branch=master)](https://travis-ci.org/populse/populse_mia)
[![](https://ci.appveyor.com/api/projects/status/2km9ddxkpfkgra7v?svg=true)](https://ci.appveyor.com/project/populse/populse-mia)
[![](https://codecov.io/github/populse/populse_mia/coverage.svg?branch=master)](https://codecov.io/github/populse/populse_mia)
[![](https://img.shields.io/badge/license-CeCILL-blue.svg)](https://github.com/populse/populse_mia/blob/master/LICENSE)
[![](https://img.shields.io/pypi/v/populse_mia.svg)](https://pypi.org/project/populse-mia/)
[![](https://img.shields.io/badge/python-3.5%2C%203.6%2C%203.7-yellow.svg)](#)
[![](https://img.shields.io/badge/platform-Linux%2C%20OSX%2C%20Windows-orange.svg)](#)

# Documentation

The documentation is available on populse_mia's website here: [https://populse.github.io/populse_mia](https://populse.github.io/populse_mia)

# Installation

* From PyPI

  * Please, see the [Populse_MIA’s user installation](https://populse.github.io/populse_mia/html/installation/user_installation.html)

* From source, for Linux distributions
  * A compatible version of Python must be installed
  * Install a Version Control System, for example [git](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control). Depending of your distribution, [package management system](https://en.wikipedia.org/wiki/Package_manager) can be different
  
        sudo apt-get install git # Debian like
        sudo dnf install git # Fedora 22 and later
        # etc.
  * We use Git extension for versioning large files ([Git LFS](https://git-lfs.github.com/)) of the populse_mia project. We therefore recommend to [install git-lfs](https://github.com/git-lfs/git-lfs/wiki/Installation).
  * Clone the source codes

    * Get source codes from Github. Replace [mia_install_dir] with a directory of your choice

          git lfs clone https://github.com/populse/populse_mia.git [mia_install_dir]

    * Or download the zip file (populse_mia-master.zip) of the project ([green button "Clone or download"](https://github.com/populse/populse_mia)), then extract the data in the directory of your choice [mia_install_dir]

           unzip populse_mia-master.zip -d [mia_install_dir]  # In this case [mia_install_dir] becomes [mia_install_dir]/populse_mia-master
	
  * Install the Python module distribution

        cd [mia_install_dir]  
        sudo python3 setup.py install # Ensure that you use python >= 3.5 (use python3.x to be sure)  

  * To run populse_mia from the source code, don't remove it. Otherwise:

        cd ..  
        rm -r [mia_install_dir]  

# Usage

  * For Linux: launching from the source code directory via command line

    * Interprets the main.py file

          cd [mia_install_dir]/python/populse_mia  
          python3 main.py  

  * For all platforms, after a [Populse_MIA’s user installation](https://populse.github.io/populse_mia/html/installation/user_installation.html)
 
        python3 -m populse_mia

# Tests

* Unit tests written thanks to the python module unittest
* Continuous integration made with Travis (Linux, OSX), and AppVeyor (Windows)
* Code coverage calculated by the python module codecov
* The module is ensured to work with Python >= 3.5
* The module is ensured to work on the platforms Linux, OSX and Windows
* The script of tests is python/populse_mia/test.py, so the following command launches the tests:

      python3 python/populse_mia/test.py (from populse_mia root folder, for example [mia_install_dir])

# Requirements

* capsul
* lark-parser
* matplotlib
* mia-processes
* nibabel
* nipype
* pillow
* populse-db
* pyqt5
* python-dateutil
* pyyaml
* scikit-image
* scipy
* SIP
* sqlalchemy
* snakeviz
* soma_workflow
* traits

# Other packages used

* copy
* os
* six
* tempfile
* unittest

# License

* The whole populse project is open source
* Populse_mia is precisely released under the CeCILL software license
* You can find all the details on the license [here](http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html), or refer to the license file [here](https://github.com/populse/populse_mia/blob/master/LICENSE)

# Support and Communication

If you have a problem or would like to ask a question about how to do something in populse_mia please [open an issue](https://github.com/populse/populse_mia/issues).

You can even contact the developer team by using populse-support@univ-grenoble-alpes.fr.

