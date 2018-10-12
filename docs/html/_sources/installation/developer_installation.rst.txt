.. toctree::

+-----------------------+------------------------------------------------------+-------------------------------------+--------------------------------------------------+
|`Home <../index.html>`_|`Documentation <../documentation/documentation.html>`_|`Installation <./installation.html>`_|`GitHub <https://github.com/populse/populse_mia>`_|
+-----------------------+------------------------------------------------------+-------------------------------------+--------------------------------------------------+


Populse_MIA's developer installation
====================================

This page explains how to install Populse_MIA to use it as a developer. Note: A compatible version of Python must be installed (Python > 3.5)


Non-Populse member
------------------

* `Fork <https://help.github.com/articles/fork-a-repo/>`_ Populse_MIA on GitHub and clone your Populse_MIA repository

    * Make sure to have git installed (`git documentation <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`_)

    * If not, install it (depending of your distribution, `package management system <https://en.wikipedia.org/wiki/Package_manager>`_ can be different): ::

        sudo apt-get install git # Debian like
        sudo dnf install git # Fedora 22 and later etc.

    * Get source code from Github using HTTPS or SSH. Replace [mia_install_dir] with a directory of your choice::

        git clone https://github.com/your_user_name/populse_mia.git [mia_install_dir] # using HTTPS
        git clone git@github.com:your_user_name/populse_mia.git [mia_install_dir] # using SSH

    * Then, install the Python module distribution::

        cd [mia_install_dir]  
        sudo python3 setup.py install # Ensure that you use python >= 3.5 (use python3.x to be sure)  

    * Add the module directory to the python path

        * Depending of your command-line interpreter and the environment you are working in, `the environment variables management <https://en.wikipedia.org/wiki/Unix_shell>`_ can be different ::

            export PYTHONPATH=$PYTHONPATH:[mia_install_dir]/python/populse_mia/src/modules # bash  
            setenv PYTHONPATH ${PYTHONPATH}:[mia_install_dir]/python/populse_mia/src/modules # tcsh / csh  etc.  

    * Then interprets the main.py file to run Populse_MIA ::

        cd [mia_install_dir]/python/populse_mia/src/scripts  
        python3 main.py

    * If you have made some changes to improve the code and want to share them, feel free to open pull requests:

        * Commit and push your changes to your personal repository

        * Open a `pull request <https://help.github.com/articles/creating-a-pull-request/>`_ on GitHub


Populse member
--------------

* Install Populse_MIA from source (for Linux distributions)

    * Make sure to have git installed (`git documentation <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`_)

    * If not, install it (depending of your distribution, `package management system <https://en.wikipedia.org/wiki/Package_manager>`_ can be different): ::

        sudo apt-get install git # Debian like
        sudo dnf install git # Fedora 22 and later etc.

    * Get source code from Github using HTTPS or SSH. Replace [mia_install_dir] with a directory of your choice::

        git clone https://github.com/populse/populse_mia.git [mia_install_dir] # using HTTPS
        git clone git@github.com:populse/populse_mia.git [mia_install_dir] # using SSH

    * Then, install the Python module distribution::

        cd [mia_install_dir]  
        sudo python3 setup.py install # Ensure that you use python >= 3.5 (use python3.x to be sure)  

    * Add the module directory to the python path

        * Depending of your command-line interpreter and the environment you are working in, `the environment variables management <https://en.wikipedia.org/wiki/Unix_shell>`_ can be different ::

            export PYTHONPATH=$PYTHONPATH:[mia_install_dir]/python/populse_mia/src/modules # bash  
            setenv PYTHONPATH ${PYTHONPATH}:[mia_install_dir]/python/populse_mia/src/modules # tcsh / csh  etc.  

    * Then interprets the main.py file to run Populse_MIA ::

        cd [mia_install_dir]/python/populse_mia/src/scripts  
        python3 main.py  

    * Make sure to work on your own branch ::
        
        git checkout -b your_branch_name # creates your own branch locally
        git push -u origin your_branch_name # creates your own branch remotely

