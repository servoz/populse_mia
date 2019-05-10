import sys

# Current version
version_major = 1
version_minor = 1
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
MAINTAINER_EMAIL = 'populse-support@univ-grenoble-alpes.fr'
AUTHOR = 'Populse team'
AUTHOR_EMAIL = 'populse-support@univ-grenoble-alpes.fr'
URL = 'http://populse.github.io/populse_mia'
DOWNLOAD_URL = 'http://populse.github.io/populse_mia'
LICENSE = 'CeCILL'
VERSION = __version__
CLASSIFIERS = CLASSIFIERS
PLATFORMS = 'OS Independent'

if sys.version_info < (3 , 6) and sys.version_info >= (3 , 5):
    REQUIRES = [
        'capsul',
        'lark-parser',
        'matplotlib<3.1',
        'mia-processes',
        'nibabel',
        'nipype',
        'pillow',
        'populse-db',
        'pyqt5',
        'python-dateutil',
        'pyyaml',
        'scikit-image',
        'scipy',
        'SIP',
        'sqlalchemy',
        'snakeviz',
        'soma_workflow',
        'traits',
]

elif sys.version_info >= (3 , 6):
    REQUIRES = [
        'capsul',
        'lark-parser',
        'matplotlib',
        'mia-processes',
        'nibabel',
        'nipype',
        'pillow',
        'populse-db',
        'pyqt5',
        'python-dateutil',
        'pyyaml',
        'scikit-image',
        'scipy',
        'SIP',  
        'sqlalchemy',
        'snakeviz',
        'soma_workflow',
        'traits',
]

else:
    sys.exit("The populse_mia is ensured to work with Python >= 3.5")

EXTRA_REQUIRES = {
    'doc': [
        'sphinx>=1.0',
    ],
}

brainvisa_build_model = 'pure_python'

# tests to run
test_commands = ['%s -m populse_mia.test' % sys.executable]
