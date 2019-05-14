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


    * **_run_process()**

    This method is called during a pipeline run. It has to contain the desired processing and need no return value.


**Note:** if you are using a Nipype interface that need to use Matlab script. Make sure to use the "manage_matlab_launch_parameters" method in the _run_process method to set the Matlab's parameters of your Populse_MIA's config to the Nipype interface. ::

    self.process = spm.Smooth()
    self.manage_matlab_launch_parameters()

    # Then set the several inputs of the interface
    self.process.inputs.in_files = self.in_files
    self.process.inputs.fwhm = self.fwhm  # etc.


**Example:** creating a smooth process using SPM Smooth (from Nipype’s interfaces) or Scipy's gaussian filtering function. ::

    import os
    import traits.api as traits  # used to declare the inputs/outputs of the process
    import nibabel as nib  # used to read and save Nifti images
    from nipype.interfaces import spm  # used to use SPM's Smooth
    from scipy.ndimage.filters import gaussian_filter  # used to apply the smoothing on an array
    from populse_mia.user_interface.pipeline_manager.process_mia import ProcessMIA  # base class that the created process has to inherit from
    
    
    class SmoothSpmScipy(ProcessMIA):
    
        def __init__(self):
            super(SmoothSpmScipy, self).__init__()
    
            # Inputs
            self.add_trait("in_file", traits.File(output=False, desc='3D input file'))  # Mandatory plug
    
            # For inputs/outputs that are lists, it is possible to specify which the type of the list element (here
            # traits.Float(). The second value ([1.0, 1.0, 1.0]) corresponds to the default value
            self.add_trait("fwhm", traits.List(traits.Float(), [1.0, 1.0, 1.0], output=False, optional=True,
                                               desc='List of fwhm for each dimension (in mm)'))
    
            self.add_trait("out_prefix", traits.String('s', output=False, optional=True, desc='Output file prefix'))
            self.add_trait("method", traits.Enum('SPM', 'Scipy', output=False, optional=True,
                                                 desc='Method used (either "SPM" or "Scipy")'))
    
            # Output
            self.add_trait("smoothed_file", traits.File(output=True, desc='Output file'))  # Mandatory plug

            self.process = spm.Smooth()
    
        def list_outputs(self):
            # Depending on the chosen method, the output dictionary will be generated differently
            if self.method in ['SPM', 'Scipy']:
                if self.method == 'SPM':
                    # Nipype interfaces have already a _list_outputs method that generates the output dictionary
                    if not self.in_file:
                        print('"in_file" plug is mandatory for a Smooth process')
                        return {}
                    else:
                        self.process.inputs.in_files = self.in_file  # The input for a SPM Smooth is "in_files"
                    self.process.inputs.out_prefix = self.out_prefix
                    nipype_dict = self.process._list_outputs()  # Generates: {'smoothed_files' : [out_filename]}
                    output_dict = {'smoothed_file': nipype_dict['smoothed_files'][0]}
                else:
                    # Generating the filename by hand
                    if not self.in_file:
                        print('"in_file" plug is mandatory for a Smooth process')
                        return {}
                    else:
                        path, filename = os.path.split(self.in_file)
                        out_filename = self.out_prefix + filename
                        output_dict = {'smoothed_file': os.path.join(path, out_filename)}
    
                # Generating the inheritance dictionary
                inheritance_dict = {output_dict['smoothed_file']: self.in_file}
    
                return output_dict, inheritance_dict
    
            else:
                print('"method" input has to be "SPM" or "Scipy" for a Smooth process')
                return {}
    
        def _run_process(self):
            # Depending on the chosen method, the output file will be generated differently
            if self.method in ['SPM', 'Scipy']:
                if self.method == 'SPM':
                    # Make sure to call the manage_matlab_launch_parameters method to set the config parameters
                    self.manage_matlab_launch_parameters()
                    if not self.in_file:
                        print('"in_file" plug is mandatory for a Smooth process')
                        return
                    else:
                        self.process.inputs.in_files = self.in_file  # The input for a SPM Smooth is "in_files"
                    self.process.inputs.fwhm = self.fwhm
                    self.process.inputs.out_prefix = self.out_prefix
    
                    self.process.run()  # Running the interface
    
                else:
                    if not self.in_file:
                        print('"in_file" plug is mandatory for a Smooth process')
                        return
                    else:
                        input_image = nib.load(self.in_file)  # Loading the nibabel image
                        input_image_header = input_image.header
                        input_array = input_image.get_data()  # Getting the 3D volume as a numpy array
    
                        # Getting the image resolution in x, y and z
                        x_resolution = abs(input_image_header['pixdim'][1])
                        y_resolution = abs(input_image_header['pixdim'][2])
                        z_resolution = abs(input_image_header['pixdim'][3])
    
                        # Convert the fwhm for each dimension from mm to pixel
                        x_fwhm = self.fwhm[0] / x_resolution
                        y_fwhm = self.fwhm[1] / y_resolution
                        z_fwhm = self.fwhm[2] / z_resolution
                        pixel_fwhm = [x_fwhm, y_fwhm, z_fwhm]
    
                        sigma = [pixel_fwhm_dim / 2.355 for pixel_fwhm_dim in pixel_fwhm]  # Converting fwmh to sigma
                        output_array = gaussian_filter(input_array, sigma)  # Filtering the array
    
                        # Creating a new Nifti image with the affine/header of the input_image
                        output_image = nib.Nifti1Image(output_array, input_image.affine, input_image.header)
    
                        # Saving the image
                        path, filename = os.path.split(self.in_file)
                        out_filename = self.out_prefix + filename
                        nib.save(output_image, os.path.join(path, out_filename))
    
            else:
                print('"method" input has to be "SPM" or "Scipy" for a Smooth process')
                return {}



Creating a Python package containing the process
------------------------------------------------

Make sure that the file containing the Smooth class is contained in a Python package and add this to the __init__.py file: ::

    from .name_of_file import SmoothSpmScipy

Installing the package in Populse_MIA
-------------------------------------

In the software menu bar, go to More > Install processes > From folder and browse to the package. Click on “Install package”. The package is now stored in the process library and the Smooth process can be used to create pipelines.

