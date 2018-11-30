import sys

# Current version
version_major = 1
version_minor = 0
version_micro = 1
version_extra = ""

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(version_major, version_minor, version_micro)


# Expected by setup.py: the status of the project
CLASSIFIERS = ['Development Status :: 5 - Production/Stable',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
               'Topic :: Software Development :: Libraries :: Python Modules',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Scientific/Engineering',
               'Topic :: Utilities']

# project descriptions
DESCRIPTION = 'populse mia'
LONG_DESCRIPTION = """
===============
populse_mia
===============
[MIA] Multiparametric Image Analysis:
A complete image processing environment mainly targeted at 
the analysis and visualization of large amounts of MRI data
"""

# Other values used in setup.py
NAME = 'populse_mia'
ORGANISATION = 'populse'
MAINTAINER = 'Populse team'
MAINTAINER_EMAIL = ''
AUTHOR = 'Populse team'
AUTHOR_EMAIL = ''
URL = 'http://populse.github.io/populse_mia'
DOWNLOAD_URL = 'http://populse.github.io/populse_mia'
LICENSE = 'CeCILL'
VERSION = __version__
CLASSIFIERS = CLASSIFIERS
PLATFORMS = 'OS Independent'
REQUIRES = [
  'SIP',  
  'pyqt5',
  'pyyaml',
  'python-dateutil',
  'sqlalchemy',
  'lark-parser',
  'scipy',
  'nibabel',
  'snakeviz',
  'pillow',
  'matplotlib',
  'traits',
  'capsul',
  'soma_workflow',
  'nipype',
  'scikit-image',
  'populse-db'
]
EXTRA_REQUIRES = {
    'doc': [
        'sphinx>=1.0',
    ],
}

# tests to run
test_commands = ['%s -m populse_mia.test' % sys.executable]
