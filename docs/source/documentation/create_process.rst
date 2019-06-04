.. :orphan: is used below to try to remove the following warning: checking consistency... /home/econdami/Git_Projects/populse_mia/docs/source/documentation/create_process.rst: WARNING: document isn't included in any toctree
:orphan:
.. toctree::

+-----------------------+---------------------------------------+---------------------------------------------------+--------------------------------------------------+
|`Home <../index.html>`_|`Documentation <./documentation.html>`_|`Installation <../installation/installation.html>`_|`GitHub <https://github.com/populse/populse_mia>`_|
+-----------------------+---------------------------------------+---------------------------------------------------+--------------------------------------------------+

Populse_MIA's pipeline processes
================================

This page explains how to create a process that can be used in Populse_MIA's Pipeline Manager and how to install it to Populse_MIA.

Populse_MIA uses `Capsul <http://brainvisa.info/capsul/index.html>`_ to handle Pipeline processing. During Populse_MIA installation, Nipype’s interfaces are stored in the package library and are directly available in the Process Library. However, any user can import its own processes in Populse_MIA following these next steps:


Creating a MIA process 
----------------------

MIA processes are Capsul processes made specific for Populse_MIA. They need at least three methods to work properly: __init__, list_outputs and _run_process.

    * **__init__()**
    Definition of the inputs/outputs of the process. Each input/output is typed using the `Enthought’s Traits library <https://docs.enthought.com/traits/>`_ and is either mandatory or optional.


    * **list_outputs()**

    This method is called during a pipeline initialization to generate the process outputs and their inheritances (from which input they depends). The return value of this method must at least be a dictionary of this type {‘name_of_the_output_plug’: ‘value’, …}. To improve the file tracking, antoher dictionary can be added to the return value. This dictionary called inheritance dictionary specifies for each output which input generated it: {‘output_value’: ‘input_value’, …}.


    * **run_process_mia()**

    This method is called during a pipeline run. It has to contain the desired processing and need no return value.


**Note:** if you are using a Nipype interface that need to use Matlab script. Make sure to use the "manage_matlab_launch_parameters" method in the _run_process method to set the Matlab's parameters of your Populse_MIA's config to the Nipype interface. ::

    self.process = spm.Smooth()
    self.manage_matlab_launch_parameters()

    # Then set the several inputs of the interface
    self.process.inputs.in_files = self.in_files
    self.process.inputs.fwhm = self.fwhm  # etc.


**Example:** creating a smooth process using SPM Smooth (from Nipype’s interfaces) or Scipy's gaussian filtering function. ::

    # Trait import
    from traits.api import Float
    from nipype.interfaces.base import OutputMultiPath, InputMultiPath, File, traits
    from nipype.interfaces.spm.base import ImageFileSPM

    from mia_processes.process_mia import Process_Mia

    # Other import
    import os
    from nipype.interfaces import spm
    
    
    class Smooth(Process_Mia):
    
        def __init__(self):
            super(Smooth, self).__init__()

            # Inputs description
            in_files_desc = 'List of files to smooth. A list of items which are an existing, uncompressed file (valid extensions: [.img, .nii, .hdr]).'
            fwhm_desc = 'Full-width at half maximum (FWHM) of the Gaussian smoothing kernel in mm. A list of 3 items which are a float of fwhm for each dimension.'
            data_type_desc = 'Data type of the output images (an integer [int or long]).'
            implicit_masking_desc = 'A mask implied by a particular voxel value (a boolean).'
            out_prefix_desc = 'Specify  the string to be prepended to the filenames of the smoothed image file(s) (a string).'

            # Outputs description
            smoothed_files_desc = 'The smoothed files (a list of items which are an existing file name).'

            # Input traits 
            self.add_trait("in_files",
                           InputMultiPath(ImageFileSPM(),
                                          copyfile=False,
                                          output=False,
                                          desc=in_files_desc))
            '''self.add_trait("fwhm", traits.Either(traits.Float(),
                           traits.List(traits.Float()), default_value=[6, 6, 6], output=False, optional=True))'''
            self.add_trait("fwhm",
                           traits.List([6, 6, 6],
                                       output=False,
                                       optional=True,
                                       desc= fwhm_desc))

            self.add_trait("data_type",
                           traits.Int(output=False,
                                      optional=True,
                           desc=data_type_desc))
            
            self.add_trait("implicit_masking",
                           traits.Bool(output=False,
                                       optional=True,
                                       desc=implicit_masking_desc))
            
            self.add_trait("out_prefix",
                           traits.String('s',
                                         usedefault=True,
                                         output=False,
                                         optional=True,
                                         desc=out_prefix_desc))

            # Output traits 
            self.add_trait("smoothed_files",
                           OutputMultiPath(File(),
                                           output=True,
                                           desc=smoothed_files_desc))

            self.process = spm.Smooth()
            self.change_dir = True

        def list_outputs(self):
            super(Smooth, self).list_outputs()

            if not self.in_files:
                return {}
            else:
                self.process.inputs.in_files = self.in_files

            if self.out_prefix:
                self.process.inputs.out_prefix = self.out_prefix

            outputs = self.process._list_outputs()

            inheritance_dict = {}
            for key, values in outputs.items():
                if key == "smoothed_files":
                    for fullname in values:
                        path, filename = os.path.split(fullname)
                        if self.out_prefix:
                            filename_without_prefix = filename[len(self.out_prefix):]
                        else:
                            filename_without_prefix = filename[len('s'):]

                        if os.path.join(path, filename_without_prefix) in self.in_files:
                            inheritance_dict[fullname] = os.path.join(path, filename_without_prefix)

            return outputs, inheritance_dict

        def run_process_mia(self):
            super(Smooth, self).run_process_mia()

            for idx, element in enumerate(self.in_files):
                full_path = os.path.relpath(element)
                self.in_files[idx] = full_path
            self.process.inputs.in_files = self.in_files
            self.process.inputs.fwhm = self.fwhm
            self.process.inputs.data_type = self.data_type
            self.process.inputs.implicit_masking = self.implicit_masking
            self.process.inputs.out_prefix = self.out_prefix

            self.process.run()



Creating a Python package containing the process
------------------------------------------------

Make sure that the file containing the Smooth class is contained in a Python package and add this to the __init__.py file: ::

    from .name_of_file import SmoothSpmScipy

Installing the package in Populse_MIA
-------------------------------------

In the software menu bar, go to More > Install processes > From folder and browse to the package. Click on “Install package”. The package is now stored in the process library and the Smooth process can be used to create pipelines.

