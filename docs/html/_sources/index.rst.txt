.. populse_mia documentation master file, created by
   sphinx-quickstart on Thu Oct 11 16:32:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::

+----------------------+-----------------------------------------------------+--------------------------------------------------+--------------------------------------------------+
|`Home <./index.html>`_|`Documentation <./documentation/documentation.html>`_|`Installation <./installation/installation.html>`_|`GitHub <https://github.com/populse/populse_mia>`_|
+----------------------+-----------------------------------------------------+--------------------------------------------------+--------------------------------------------------+

|
|

.. image:: ./images/Logo_populse_mia.jpg
   :align: center
   :width: 400px
   :name: Logo Populse_MIA

.. raw:: html

    <embed>
      <center>
        <i>
          <font size="1">
            ©Johan Pietras @IRMaGe
          </font size>
        </i>
      </center>
    </embed>

|


Generalities
============

MIA is shorthand for "Multiparametric Image Analysis". It is intended to be a complete image processing environment mainly targeted at the analysis and visualization of large amounts of MRI data.

MRI data analysis often requires a complex succession of data processing pipelines applied to a set of data acquired in an MRI exam or over several MRI exams. This analysis may need to be repeated a large number of times in studies involving a large number of acquisition sessions. Such that manual execution of the processing modules or simple ad-hoc scripting of the process may become error-prone, cumbersome and difficult to reproduce. Data processing pipelines exist in separate heterogeneous toolboxes, developed in-house or by other researchers in the field. This heterogeneity adds to the complexity of the modules are to be invoked manually.

Populse_MIA aims to provide easy tools to perform complex data processing based on a definition of the inputs and outputs of the individual pipelines on a conceptual level, and implies identifying data with respect to their role in an analysis project: "the scan type", "the subject being scanned", "the group of this subject is part of", etc.


Main features
=============

* `Metadata enhancement <./documentation/data_browser.html>`_
* `Complex pipeline processing <./documentation/pipeline_manager.html>`_
* Data visualization (coming soon)

Installation
============

* `User installation <./installation/user_installation.html>`_
* `Developer installation <./installation/developer_installation.html>`_


Documentation
=============

* `User documentation <./documentation/user_documentation.html>`_
* `Developer documentation <./documentation/developer_documentation.html>`_
* `Create and install a pipeline process <./documentation/create_process.html>`_


License
=======
Populse_MIA is released under the `CeCILL <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>`_ software license.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

