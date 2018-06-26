import datetime

from capsul.process.process import Process
from traits.trait_handlers import TraitListObject

from Project.Project import COLLECTION_BRICK, BRICK_EXEC, BRICK_EXEC_TIME, TAG_BRICKS, COLLECTION_INITIAL, \
    COLLECTION_CURRENT, BRICK_OUTPUTS


class Process_mia(Process):
    """
    Class overriding the default capsul Process class, in order to personalize the run in MIA
    """

    def __init__(self, project):
        super(Process_mia, self).__init__()
        self.project = project

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
            if type(output_value) in [list, TraitListObject]:
                for single_value in output_value:
                    self.manage_brick_output_before_run(single_value)
            else:
                self.manage_brick_output_before_run(output_value)

        self.project.saveModifications()

    def manage_brick_after_run(self):
        """
        Manages the brick history after the run (Done status)
        """
        outputs = self.get_outputs()
        for output_name in outputs:
            output_value = outputs[output_name]
            if type(output_value) in [list, TraitListObject]:
                for single_value in output_value:
                    self.manage_brick_output_after_run(single_value)
            else:
                self.manage_brick_output_after_run(output_value)

        self.project.saveModifications()

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

    def manage_brick_output_after_run(self, output_value):
        """
        Manages the bricks history before the run
        :param output_value: output value
        """

        scan_bricks_history = self.get_scan_bricks(output_value)
        brick_to_update = self.get_brick_to_update(scan_bricks_history)
        if brick_to_update is not None:
            self.project.session.set_value(COLLECTION_BRICK, brick_to_update, BRICK_EXEC, "Done")