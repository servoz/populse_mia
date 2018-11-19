# To install sphinx
pip3 install sphinx

# In populse_mia's root folder
mkdir docs/
cd docs/

# To begin
sphinx-quickstart
"""
Default values, except the following ones:
 - Separate source and build directories (y/n) [n]: y
 - Project name: populse_mia
 - Author name(s): populse
 - Project version: 1
 - Project release: 1.0.0
 - autodoc: automatically insert docstrings from modules (y/n) [n]: y
 - Create Windows command file? (y/n) [y]: n
"""
"""
The following line (22) must be uncommented from docs/source/conf.py:
 - sys.path.insert(0, os.path.abspath('../..'))
The following line (8) must be modified from docs/Makefile:
 - BUILDDIR      = BUILD  =>  BUILDDIR      = .
"""

# To update the api documentation (in docs/ folder)
sphinx-apidoc -f -o source/ ../python/populse_mia/

# To generate the html pages (in docs/ folder)
make html
