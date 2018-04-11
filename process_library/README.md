- Two files for this first draft:
    - process_library.py, containing four classes:
        - ProcessLibrary (with its associated ProcessLibraryWidget class for displaying) allows to visualize the selected "processes" as a tree. Dragging the processes is enabled and its "path" is associated to a MIME data with a '/name/component' id.

        - PackageLibrary (with its associated PackageLibraryWidget class for displaying) allows to add/remove packages and/or modify the processes visualized in the ProcessLibrary. For the moment, the method to find a package is to write it in a pythonnic way in the line edit, e.g. "nipype.interfaces.spm". A file dialog is also added to add user packages. Note: to use the file dialog, a package has to be selected, after that its path is added to the system path that can then allow to find all the processes in the package. 

    - process_config.yml, config file that describes the tree of the processes

Note: I've forked the populse_sandbox at the beginning of the week because we couldn't push directly. Now that we can push and once this pull request will be accepted, I will continue by pushing directly on the populse/populse_sandbox.
