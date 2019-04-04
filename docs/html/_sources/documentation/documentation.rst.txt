.. :orphan: is used below to try to remove the following warning: checking consistency... /home/econdami/Git_Projects/populse_mia/docs/source/documentation/documentation.rst: WARNING: document isn't included in any toctree
:orphan:
.. toctree::

+-----------------------+---------------------------------------+---------------------------------------------------+--------------------------------------------------+
|`Home <../index.html>`_|`Documentation <./documentation.html>`_|`Installation <../installation/installation.html>`_|`GitHub <https://github.com/populse/populse_mia>`_|
+-----------------------+---------------------------------------+---------------------------------------------------+--------------------------------------------------+


Populse_MIA's documentation
===========================

* `User documentation <./user_documentation.html>`_
* `Developer documentation <./developer_documentation.html>`_
* `Create and install a pipeline process <./create_process.html>`_

Operating mode
--------------

Populse_MIA has two operating modes: 
  * Clinical mode
      * When creating a project, more default tags are stored in the database
      * Process library disabled (no pipeline creation)
  * Research mode
      * When creating a project, MIA default tags are stored in the database
      * Process library enabled

To modify it, go to the software preferences (File > MIA preferences) and disable/enable “Clinical mode”.
