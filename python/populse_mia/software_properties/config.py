# -*- coding: utf-8 -*- #
"""Module that handle the configuration of the software

Load and save the parameters from the miniviewer and the MIA preferences
pop-up in the config.yml file.

Contains:
    Class:
    -Config

"""

##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import yaml

# Populse_MIA imports
from populse_mia.utils.utils import verCmp


class Config:
    """
    Object that handles the configuration of the software

    Methods:
        - get_clinical_mode: returns the value of "clinical mode" checkbox
        in the preferences
        - get_matlab_command: returns Matlab command
        - get_matlab_path: returns the path of Matlab's executable
        - get_matlab_standalone_path: returns the path of Matlab Compiler
        Runtime
        - get_max_projects: returns the maximum number of projects displayed in
         the "Saved projects" menu
        - get_mia_path: returns the software's install path
        - get_projects_save_path: returns the folder where the projects are
        saved
        - get_spm_path: returns the path of SPM12 (license version)
        - get_spm_standalone_path: returns the path of SPM12 (standalone
        version)
        - get_use_matlab: returns the value of "use matlab" checkbox in the
        preferences
        - get_mri_conv_path: sets the MRIManager.jar path
        - get_use_spm: returns the value of "use spm" checkbox in the
        preferences
        - get_use_spm_standalone: returns the value of "use spm standalone"
        checkbox in the preferences
        - getBackgroundColor: returns the background color
        - getChainCursors: returns if the "chain cursors" checkbox of the
        mini viewer is activated
        - getNbAllSlicesMax: returns the maximum number of slices to display in
        the mini viewer
        - get_opened_projects: returns the opened projects
        - getPathData: returns the data's path
        - getPathToProjectsDBFile: returns the already-saved projects's path
        - getPathToProjectsFolder: returns the project's path
        - getShowAllSlices: returns if the "show all slices" checkbox of the
        mini viewer is activated
        - getTextColor: return the text color
        - getThumbnailTag: returns the tag that is displayed in the mini viewer
        - isAutoSave: checks if auto-save mode is activated
        - loadConfig: reads the config in the config.yml file
        - saveConfig: saves the config to the config.yml file
        - setAutoSave: sets the auto-save mode
        - setBackgroundColor: sets the background color
        - set_clinical_mode: sets the value of "clinical mode" checkbox in
        the preferences
        - set_matlab_path: sets the path of Matlab's executable
        - set_matlab_standalone_path: sets the path of Matlab Compiler Runtime
        - set_max_projects: sets the maximum number of projects displayed in
        the "Saved projects" menu
        - set_mia_path: sets the software's install path
        - set_mri_conv_path: sets the MRIManager.jar path
        - set_projects_save_path: sets the folder where the projects are saved
        - set_spm_path: sets the path of SPM12 (license version)
        - set_spm_standalone_path: sets the path of SPM12 (standalone version)
        - set_use_matlab: sets the value of "use matlab" checkbox in the
        preferences
        - set_use_spm: sets the value of "use spm" checkbox in the preferences
        - set_use_spm_standalone: sets the value of "use spm standalone"
        checkbox in the preferences
        - setChainCursors: sets the "chain cursors" checkbox of the mini viewer
        - setNbAllSlicesMax: sets the maximum number of slices to display in
        the mini viewer
        - set_opened_projects: sets the opened projects
        - setPathToData: sets the data's path
        - setShowAllSlices: sets the "show all slices" checkbox of the mini
        viewer
        - setTextColor: sets the text color
        - setThumbnailTag: sets the tag that is displayed in the mini viewer

    """
    def __init__(self):
        self.dev_mode = False
        self.config = self.loadConfig()
        if "mia_path" not in self.config.keys():
            self.config["mia_path"] = self.get_mia_path()
            self.saveConfig()

    def get_clinical_mode(self):
        """Get if clinical mode is disabled or enabled in the preferences.

        :return: boolean

        """
        try:
            return self.config["clinical_mode"]
        except KeyError:
            return "yes"

    def get_matlab_command(self):
        """Get Matlab command.

        :return: Returns path to matlab executable or nothing if matlab
        path not specified

        """
        if self.config["use_spm_standalone"] == "yes":
            return '{0}'.format(self.config["spm_standalone"]) + os.sep + \
                   'run_spm12.sh {0}'.format(self.config[
                                                 "matlab_standalone"]) + \
                   os.sep + ' script'
        elif self.config["use_matlab"] == "yes":
            return self.config["matlab"]
        else:
            return None

    def get_matlab_path(self):
        """Get the path to the matlab executable.

        :return: String of path

        """
        try:
            return self.config["matlab"]
        except KeyError:
            return ""

    def get_matlab_standalone_path(self):
        """Get the path to matlab compiler runtime.

        :return: string of path

        """
        try:
            return self.config["matlab_standalone"]
        except KeyError:
            return ""

    def get_max_projects(self):
        """Get the maximum number of projects displayed in the "Saved
        projects" menu.

        :return: Integer

        """
        try:
            return int(self.config["max_projects"])
        except KeyError as e:
            return 5

    def get_mia_path(self):
        """Get the path to the folder containing the processes, properties
        and resources folders of mia (mia_path).

        During the mia installation, the mia_path is defined and stored in the
        configuration.yml file, located in the .populse_mia folder (himself
        located in the user's home). If mia is launched in developer mode,
        mia path is the cloned git repository. If mia is launched in user
        mode, mia path must compulsorily be returned from the mia_path
        parameter of the configuration.yml

        :return: string of path to mia folder

        """
        dot_mia_config = os.path.join(os.path.expanduser("~"),
                                      ".populse_mia", "configuration.yml")

        if os.path.isfile(dot_mia_config):

            with open(dot_mia_config, 'r') as stream:

                try:
                    if verCmp(yaml.__version__, '5.1', 'sup'):
                        mia_home_config = yaml.load(stream,
                                                    Loader=yaml.FullLoader)
                    else:    
                        mia_home_config = yaml.load(stream)

                    if "dev_mode" in mia_home_config.keys() and \
                            mia_home_config[
                        "dev_mode"] == "yes":  # Only for developer mode
                        self.dev_mode = True
                        return os.path.abspath(os.path.join(
                            os.path.realpath(__file__), '..', '..', '..',
                            '..'))
                    self.dev_mode = False
                    return mia_home_config["mia_path"]  # Only for user mode

                # except yaml.YAMLError:
                #    return os.path.abspath(os.path.join(os.path.realpath(
                #    __file__), '..', '..', '..', '..'))
                # except KeyError:
                #    return os.path.abspath(os.path.join(os.path.realpath(
                #    __file__), '..', '..', '..', '..'))

                except (yaml.YAMLError, KeyError) as e:
                    print('\nMia path (where is located the processes, '
                          'the properties and resources folders) has not '
                          'been found ...')
                    # return os.path.abspath(os.path.join(os.path.realpath(
                    # __file__), '..', '..', '..', '..'))

        else:  # Only for developer mode
            try:
                return self.config["mia_path"]
            # except KeyError:
            #    return os.path.abspath(os.path.join(os.path.realpath(
            #    __file__), '..', '..', '..', '..'))
            # except AttributeError:
            #    return os.path.abspath(os.path.join(os.path.realpath(
            #    __file__), '..', '..', '..', '..'))
            except (KeyError, AttributeError):
                return os.path.abspath(os.path.join(os.path.realpath(
                    __file__), '..', '..', '..', '..'))

    def get_mri_conv_path(self):
        """Get the MRIManager.jar path.

        :return: string of the path

        """
        try:
            return self.config["mri_conv_path"]
        except KeyError:
            return ""
        except AttributeError:
            return ""

    def get_opened_projects(self):
        """Get opened projects.

        :return: list of opened projects

        """
        return self.config["opened_projects"]

    def get_projects_save_path(self):
        """Get the path where projects are saved.

        :return: string of path

        """
        try:
            return self.config["projects_save_path"]
        except KeyError:
            if not os.path.isdir(os.path.join(self.get_mia_path(),
                                              'projects')):
                os.mkdir(os.path.join(self.get_mia_path(), 'projects'))
            return os.path.join(self.get_mia_path(), 'projects')

    def get_spm_path(self):
        """Get the path of SPM12.

        :return: string of path

        """
        try:
            return self.config["spm"]
        except KeyError:
            return ""

    def get_spm_standalone_path(self):
        """Get the path to the SPM12 (standalone version).

        :return: String of path

        """
        try:
            return self.config["spm_standalone"]
        except KeyError:
            return ""

    def get_use_matlab(self):
        """Get the value of "use matlab" checkbox in the preferences.

        :return: boolean

        """
        try:
            return self.config["use_matlab"]
        except KeyError:
            return "no"

    def get_use_spm(self):
        """Get the value of "use spm" checkbox in the preferences.

        :return: boolean

        """
        try:
            return self.config["use_spm"]
        except KeyError:
            return "no"

    def get_use_spm_standalone(self):
        """Get the value of "use spm standalone" checkbox in the preferences.

        :return: boolean

        """
        try:
            return self.config["use_spm_standalone"]
        except KeyError:
            return "no"

    def getBackgroundColor(self):
        """Get background color.

        :return: string of the background color

        """
        return self.config["background_color"]

    def getChainCursors(self):
        """Get the value of the checkbox 'chain cursor' in miniviewer.

        :return: boolean

        """
        return self.config["chain_cursors"]

    def getNbAllSlicesMax(self):
        """Get number the maximum number of slices to display in the
        miniviewer.

        :return: Integer

        """
        return self.config["nb_slices_max"]

    def getPathToProjectsFolder(self):
        """Get the project's path.

        :return: string of the path

        """
        return self.config["paths"]["projects"]

    def getShowAllSlices(self):
        """Get whether the show_all_slices parameters was enabled
        or not in the miniviewer.

        :return: boolean

        """
        #Used in MiniViewer
        return self.config["show_all_slices"]

    def getTextColor(self):
        """Get the text color.

        :return: string

        """
        return self.config["text_color"]

    def getThumbnailTag(self):
        """Get the tag of the thumbnail displayed in the miniviewer.

        :return: string

        """
        return self.config["thumbnail_tag"]

    def isAutoSave(self):
        """Get if the auto-save mode is enabled or not.

        :return: boolean

        """
        # used only in tests and when the background/text color is changed
        return self.config["auto_save"]

    def loadConfig(self):
        """Read the config in the config.yml file.

        :return: Returns a dictionary of the contents of config.yml

        """
        with open(os.path.join(self.get_mia_path(), 'properties',
                               'config.yml'), 'r') as stream:
            try:
                if verCmp(yaml.__version__, '5.1', 'sup'):
                    return yaml.load(stream, Loader=yaml.FullLoader)
                
                else:    
                    return yaml.load(stream)
                
            except yaml.YAMLError as exc:
                print(exc)

    def saveConfig(self):
        """Save the current parameters in the config.yml file."""

        with open(os.path.join(self.get_mia_path(), 'properties',
                               'config.yml'), 'w', encoding='utf8') as \
                configfile:
            yaml.dump(self.config, configfile, default_flow_style=False,
                      allow_unicode=True)

    def set_clinical_mode(self, clinical_mode):
        """Enable of disable clinical mode.

        :param: clinical_mode: boolean

        """
        self.config["clinical_mode"] = clinical_mode
        # Then save the modification
        self.saveConfig()

    def set_matlab_path(self, path):
        """Set the path of Matlab's executable.

        :param: path: string of path

        """
        self.config["matlab"] = path
        # Then save the modification
        self.saveConfig()

    def set_matlab_standalone_path(self, path):
        """Set the path of Matlab Compiler Runtime.

        :param: path: string of path

        """
        self.config["matlab_standalone"] = path
        # Then save the modification
        self.saveConfig()

    def set_max_projects(self, nb_max_projects):
        """Set the maximum number of projects displayed in
        the "Saved projects" menu.

        :param: nb_max_projects: Integer

        """
        self.config["max_projects"] = nb_max_projects
        # Then save the modification
        self.saveConfig()

    def set_mri_conv_path(self, path):
        """Set the MRIManager.jar path.

        :param: path: string of the path

        """
        self.config["mri_conv_path"] = path
        # Then save the modification
        self.saveConfig()

    def set_opened_projects(self, new_projects):
        """Set the list of opened projects and saves the modification.

        :param: new_projects: List of path

        """
        self.config["opened_projects"] = new_projects
        # Then save the modification
        self.saveConfig()

    def set_projects_save_path(self, path):
        """Set the folder where the projects are saved.

        :param: path: string of path
        """
        self.config["projects_save_path"] = path
        # Then save the modification
        self.saveConfig()

    def set_spm_path(self, path):
        """Set the path of SPM12 (license version).

        :param: path: string of path

        """
        self.config["spm"] = path
        # Then save the modification
        self.saveConfig()

    def set_spm_standalone_path(self, path):
        """Set the path of SPM12 (standalone version).

        :param: path: string of path

        """
        self.config["spm_standalone"] = path
        # Then save the modification
        self.saveConfig()

    def set_use_matlab(self, use_matlab):
        """Set the value of "use matlab" checkbox in the preferences.

        :param: use_matlab: boolean

        """
        self.config["use_matlab"] = use_matlab
        # Then save the modification
        self.saveConfig()

    def set_use_spm(self, use_spm):
        """Set the value of "use spm" checkbox in the preferences.

        :param: use_spm: boolean
        """
        self.config["use_spm"] = use_spm
        # Then save the modification
        self.saveConfig()

    def set_use_spm_standalone(self, use_spm_standalone):
        """Set the value of "use spm standalone" checkbox in the preferences.

        :param:use_spm_standalone: boolean

        """
        self.config["use_spm_standalone"] = use_spm_standalone
        # Then save the modification
        self.saveConfig()

    def setAutoSave(self, save):
        """Set auto-save mode.

        :param: save: boolean
        """
        self.config["auto_save"] = save
        # Then save the modification
        self.saveConfig()

    def setBackgroundColor(self, color):
        """Set background color and save configuration.

        :param: color: Color string ('Black', 'Blue', 'Green', 'Grey',
            'Orange', 'Red', 'Yellow', 'White')
        """
        self.config["background_color"] = color
        # Then save the modification
        self.saveConfig()

    def setChainCursors(self, chain_cursors):
        """Set the value of the checkbox 'chain cursor' in the miniviewer.

        :param: chain_cursors: Boolean
        """
        self.config["chain_cursors"] = chain_cursors
        # Then save the modification
        self.saveConfig()

    def setNbAllSlicesMax(self, nb_slices_max):
        """Set the number of slices to display in the miniviewer.

        :param: nb_slices_max: Int

        """
        self.config["nb_slices_max"] = nb_slices_max
        # Then save the modification
        self.saveConfig()

    def setShowAllSlices(self, show_all_slices):
        """Set the show_all_slides setting in miniviewer.

        :param: show_all_slices: Boolean
        """
        self.config["show_all_slices"] = show_all_slices
        # Then save the modification
        self.saveConfig()

    def setTextColor(self, color):
        """Set text color and save configuration.

        :param: color: Color string ('Black', 'Blue', 'Green', 'Grey',
            'Orange', 'Red', 'Yellow', 'White')

        """
        self.config["text_color"] = color
        # Then save the modification
        self.saveConfig()

    def setThumbnailTag(self, thumbnail_tag):
        """Set the tag that is displayed in the mini viewer.

        :param: thumbnail_tag: String

        """
        self.config["thumbnail_tag"] = thumbnail_tag
        # Then save the modification
        self.saveConfig()

    # def set_mia_path(self, path):
    #     """
    #
    #     :param:#         path:
    #
    #     :return:
    #
    #     """
    #     self.config["mia_path"] = path
    #     # Then save the modification
    #     self.saveConfig()

    # def getPathData(self):
    #     """
    #     Get the path tp the data directory
    #     :return: returns the path to the data directory
    #
    #     """
    #     return self.config["paths"]["data"]

    # def getPathToProjectsDBFile(self):
    #     """
    #
    #     :return:
    #
    #     """
    #     folder = self.getPathToProjectsFolder()
    #     return os.path.join(folder, 'projects.json')

    # def setPathToData(self,path):
    #     """
    #
    #     :param:#         path:
    #
    #     :return:
    #
    #     """
    #     if path is not None and path != '':
    #         self.config["paths"]["data"] = path
    #         # Then save the modification
    #         self.saveConfig()

