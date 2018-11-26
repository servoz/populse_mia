##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import datetime
from traits.trait_base import Undefined
from traits.trait_handlers import TraitListObject

# Capsul imports
from capsul.process.process import Process

# Populse_MIA imports
from populse_mia.project.project import COLLECTION_BRICK, BRICK_EXEC, BRICK_EXEC_TIME, TAG_BRICKS, COLLECTION_INITIAL, \
    COLLECTION_CURRENT, BRICK_OUTPUTS


class ProcessMIA(Process):
    """
    Class overriding the default capsul Process class, in order to personalize the run in MIA

    Methods:
        - manage_matlab_launch_parameters: sets the Matlab's config parameters when a Nipype process is used
        - list_outputs: generates the outputs of the process (need to be overridden)
        - _before_run_process: method called before running the process
        - _after_run_process: method called after the process being run
        - manage_brick_before_run: updates process history, before running the process
        - manage_brick_after_run: manages the brick history after the run (Done status)
        - get_scan_bricks: gives the list of bricks, given an output value
        - get_brick_to_update: gives the brick to update, given the scan list of bricks
        - remove_brick_output: removes the bricks from the outputs
        - manage_brick_output_before_run: manages the bricks history before the run
        - manage_brick_output_after_run: manages the bricks history before the run
    """

    def __init__(self):
        super(ProcessMIA, self).__init__()
        # self.filters = {}  # use if the filters are set on plugs

    def manage_matlab_launch_parameters(self):
        """
        Sets the Matlab's config parameters when a Nipype process is used
        """

        if hasattr(self, "process"):
            self.process.inputs.use_mcr = self.use_mcr
            self.process.inputs.paths = self.paths
            self.process.inputs.matlab_cmd = self.matlab_cmd
            self.process.inputs.mfile = self.mfile

    def list_outputs(self):
        """
        Generates the outputs of the process (need to be overridden)
        """
        pass

    def _before_run_process(self):
        """
        Method called before running the process
        It adds the exec status Not Done and exec time to the process history
        """

        self.manage_brick_before_run()

    def _after_run_process(self, run_process_result):
        """
        Method called after the process being run

        :param run_process_result: Result of the run process
        :return: the result of the run process
        """

        self.manage_brick_after_run()
        return run_process_result

    def manage_brick_before_run(self):
        """
        Updates process history, before running the process
        """

        outputs = self.get_outputs()
        for output_name in outputs:
            output_value = outputs[output_name]
            if output_value not in ["<undefined>", Undefined]:
                if type(output_value) in [list, TraitListObject]:
                    for single_value in output_value:
                        self.manage_brick_output_before_run(single_value)
                else:
                    self.manage_brick_output_before_run(output_value)

    def manage_brick_after_run(self):
        """
        Manages the brick history after the run (Done status)
        """
        outputs = self.get_outputs()
        for output_name in outputs:
            output_value = outputs[output_name]
            if output_value not in ["<undefined>", Undefined]:
                if type(output_value) in [list, TraitListObject]:
                    for single_value in output_value:
                        self.manage_brick_output_after_run(single_value)
                else:
                    self.manage_brick_output_after_run(output_value)

    def get_scan_bricks(self, output_value):
        """
        Gives the list of bricks, given an output value

        :param output_value: output value
        :return: list of bricks related to the output
        """
        for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
            if scan in str(output_value):
                return self.project.session.get_value(COLLECTION_CURRENT, scan, TAG_BRICKS)
        return []

    def get_brick_to_update(self, bricks):
        """
        Gives the brick to update, given the scan list of bricks

        :param bricks: list of scan bricks
        :return: Brick to update
        """

        if bricks is None:
            return

        if len(bricks) == 0:
            return None
        if len(bricks) == 1:
            return bricks[0]
        else:
            brick_to_keep = bricks[len(bricks) - 1]
            for brick in bricks:
                exec_status = self.project.session.get_value(COLLECTION_BRICK, brick, BRICK_EXEC)
                exec_time = self.project.session.get_value(COLLECTION_BRICK, brick, BRICK_EXEC_TIME)
                if exec_time is None and exec_status is None and brick != brick_to_keep:
                    # The other bricks not run are removed
                    outputs = self.project.session.get_value(COLLECTION_BRICK, brick, BRICK_OUTPUTS)
                    for output_name in outputs:
                        output_value = outputs[output_name]
                        self.remove_brick_output(brick, output_value)
                    self.project.session.remove_document(COLLECTION_BRICK, brick)
                    self.project.saveModifications()
            return brick_to_keep

    def remove_brick_output(self, brick, output):
        """
        Removes the bricks from the outputs

        :param output: output
        :param brick: brick
        """

        if type(output) in [list, TraitListObject]:
            for single_value in output:
                self.remove_brick_output(brick, single_value)
            return

        for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
            if scan in output:
                output_bricks = self.project.session.get_value(COLLECTION_CURRENT, scan, TAG_BRICKS)
                output_bricks.remove(brick)
                self.project.session.set_value(COLLECTION_CURRENT, scan, TAG_BRICKS, output_bricks)
                self.project.session.set_value(COLLECTION_INITIAL, scan, TAG_BRICKS, output_bricks)
                self.project.saveModifications()

    def manage_brick_output_before_run(self, output_value):
        """
        Manages the bricks history before the run

        :param output_value: output value
        """

        scan_bricks_history = self.get_scan_bricks(output_value)
        brick_to_update = self.get_brick_to_update(scan_bricks_history)
        if brick_to_update is not None:
            self.project.session.set_value(COLLECTION_BRICK, brick_to_update, BRICK_EXEC_TIME,
                                      datetime.datetime.now())
            self.project.session.set_value(COLLECTION_BRICK, brick_to_update, BRICK_EXEC, "Not Done")
            self.project.saveModifications()

    def manage_brick_output_after_run(self, output_value):
        """
        Manages the bricks history before the run

        :param output_value: output value
        """

        scan_bricks_history = self.get_scan_bricks(output_value)
        brick_to_update = self.get_brick_to_update(scan_bricks_history)
        if brick_to_update is not None:
            self.project.session.set_value(COLLECTION_BRICK, brick_to_update, BRICK_EXEC, "Done")
            self.project.saveModifications()
