from capsul.api import Pipeline
import traits.api as traits


class Pipeline3(Pipeline):

    def pipeline_definition(self):
        # nodes
        self.add_process("spm_smooth1", "Processes.processes.SPM_Smooth")
        self.nodes["spm_smooth1"].process.in_files = ['../../projects/Clinique_test_0625/data/raw_data/alej170316_test24042018-IRM_Fonct._+_perfusion-2016-03-17_08-34-44-05-01-T1_3D_SENSE-T1TFE-00-04-25.000.nii']
        self.nodes["spm_smooth1"].process.fwhm = [1, 1, 1]
        self.add_process("spm_smooth2", "Processes.processes.SPM_Smooth")
        self.nodes["spm_smooth2"].process.in_files = traits.Undefined
        self.nodes["spm_smooth2"].process.out_prefix = 'SMOOTH'

        # links
        self.export_parameter("spm_smooth1", "in_files")
        self.export_parameter("spm_smooth1", "fwhm")
        self.add_link("spm_smooth1.smoothed_files->spm_smooth2.in_files")
        self.export_parameter("spm_smooth2", "smoothed_files")

        # default and initial values
        self.in_files = ['../../projects/Clinique_test_0625/data/raw_data/alej170316_test24042018-IRM_Fonct._+_perfusion-2016-03-17_08-34-44-05-01-T1_3D_SENSE-T1TFE-00-04-25.000.nii']
        self.fwhm = [1, 1, 1]

        # nodes positions
        self.node_position = {
            "inputs": (-173.0, -239.0),
            "spm_smooth2": (216.0, -250.0),
            "outputs": (437.0, -75.0),
            "spm_smooth1": (11.0, -289.0),
        }

        self.do_autoexport_nodes_parameters = False
