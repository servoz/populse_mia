##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
from functools import partial
import nibabel as nib
from scipy.ndimage import rotate  # to work with NumPy arrays
import numpy as np  # a N-dimensional array object
from skimage.transform import resize

# PyQt5 imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QLabel, QScrollArea, QFrame, QSlider, QLineEdit, QSizePolicy, QCheckBox

# Populse_MIA imports
from populse_mia.utils.tools import ClickableLabel
from populse_mia.pop_ups.pop_up_select_tag import PopUpSelectTag
from populse_mia.software_properties.config import Config
from populse_mia.data_browser import data_browser
from populse_mia.project.project import COLLECTION_CURRENT


class MiniViewer(QWidget):
    """
    MiniViewer that allows to rapidly visualize scans either with a single image per scan
    with cursors to move in five dimensions or with all images of the greater dimension of the scan.

    When the latter is selected, the displayed images depends on their dimension:

        - 3D: display all the slices.
        - 4D: display the middle slice of the third dimension for each time of the fourth dimension.
        - 5D: display the middle slice of the third dimension for the first time of the fourth dimension for each time of the fifth dimension.



    Note:
        - idx corresponds to the index of the displayed image
        - idx in [0, self.max_scans]
        - most of the class's attributes are lists of 0 to self.max_scans elements

    Attributes:
        - project: current project in the software
        - img: list of the selected images (as 3, 4 or 5D arrays)
        - a1: list of the "3D" sliders
        - a2: list of the "4D" sliders
        - a3: list of the "5D" sliders
        - imageLabel: list of labels on which to set the current image as a QPixmap
        - txta1: list of labels "m/n" on the side of a1 sliders
        - txta2: list of labels "m/n" on the side of a2 sliders
        - txta3: list of labels "m/n" on the side of a3 sliders
        - label3d: list of "3D: " labels
        - label4d: list of "5D: " labels
        - label5d: list of "5D: " labels
        - im_2D: list of the current 2D images to display
        - label_description: list of the tag values to display

    Methods:
        - update_nb_slices: updates the config file and the thumbnails
        - check_box_slices_state_changed: updates the config file and the thumbnails
        - check_box_cursors_state_changed: updates the config file
        - verify_slices: verifies the number of selected documents
        - show_slices: creates the thumbnails from the selected file paths
        - setThumbnail: sets the thumbnail tag value under the image frame
        - clearLayouts: clears the final layout
        - createLayouts: creates the layouts
        - image_to_pixmap: creates a 2D pixmap from a N-D Nifti image
        - createSlider: creates a slider
        - enableSliders: enables each slider of the selected index
        - boxSlider: creates sliders, their connections and thumbnail labels for a selected index
        - displayPosValue: displays the position of each cursor for the selected index
        - createFieldValue: creates a field where will be displayed the position of a cursor
        - createDimensionLabels: creates the dimension labels for the selected index
        - changePosValue: changes the value of a cursor for the selected index
        - navigImage: displays the 2D image for the selected index
        - indexImage: updates the sliders values depending on the size of the selected image
        - openTagsPopUp: opens a pop-up to select the legend of the thumbnails
        - image2DModifications: applies modifications to the image to display it correctly

    """

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.first_time = True

        # The MiniViewer is set hidden to give more space to the data_browser
        self.setHidden(True)

        # When multiple selection, limiting the number of thumbnails to max_scans
        self.max_scans = 4

        # Config that allows to read the software preferences
        self.config = Config()

        # Initializing some components of the MiniViewer
        self.labels = QWidget()
        self.frame = QFrame()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.frame)
        self.frame_final = QFrame()

        self.label_nb_slices = QLabel()
        self.label_nb_slices.setText("Maximum number of slices: ")

        self.line_edit_nb_slices = QLineEdit()
        self.line_edit_nb_slices.setText(str(self.config.getNbAllSlicesMax()))
        self.line_edit_nb_slices.returnPressed.connect(self.update_nb_slices)

        # All these objects are depending on the number of scans to visualize
        self.im_2D = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.txta1 = []
        self.txta2 = []
        self.txta3 = []
        self.label3D = []
        self.label4D = []
        self.label5D = []
        self.imageLabel = []
        self.img = []
        self.label_description = []

        # Layouts
        self.createLayouts()
        self.setLayout(self.v_box_final)

        # Checkboxes
        self.check_box_slices = QCheckBox('Show all slices (no cursors)')
        if self.config.getShowAllSlices() == 'yes':
            self.check_box_slices.setCheckState(Qt.Checked)
        else:
            self.check_box_slices.setCheckState(Qt.Unchecked)
        self.check_box_slices.stateChanged.connect(self.check_box_slices_state_changed)

        self.check_box_cursors = QCheckBox('Chain cursors')
        if self.config.getChainCursors() == 'yes':
            self.check_box_cursors.setCheckState(Qt.Checked)
        else:
            self.check_box_cursors.setCheckState(Qt.Unchecked)
        self.check_box_cursors.stateChanged.connect(self.check_box_cursors_state_changed)

        self.file_paths = ""

    def update_nb_slices(self):
        """
        Updates the config file and the thumbnails

        Called when the number of slices to visualize changes.
        """
        nb_slices = self.line_edit_nb_slices.text()
        self.config.setNbAllSlicesMax(nb_slices)
        self.verify_slices(self.file_paths)

    def check_box_slices_state_changed(self):
        """
        Updates the config file and the thumbnails

        Called when the state of the checkbox of the visualization method changes.
        """
        if self.check_box_slices.checkState() == Qt.Checked:
            self.config.setShowAllSlices('yes')
        elif self.check_box_slices.checkState() == Qt.Unchecked:
            self.config.setShowAllSlices('no')
        self.verify_slices(self.file_paths)

    def check_box_cursors_state_changed(self):
        """
        Updates the config file

        Called when the state of the checkbox to chain the cursors changes.
        """
        if self.check_box_cursors.checkState() == Qt.Checked:
            self.config.setChainCursors('yes')
        elif self.check_box_cursors.checkState() == Qt.Unchecked:
            self.config.setChainCursors('no')

    def verify_slices(self, file_paths):
        """
        Verifies the number of selected documents

        :param file_paths: the selected documents
        """
        # Updating the config
        self.config = Config()
        if len(file_paths) > 1:
            self.config.setShowAllSlices('no')
            self.check_box_slices.setCheckState(Qt.Unchecked)
            self.check_box_slices.setCheckable(False)
        else:
            self.check_box_slices.setCheckable(True)
        self.show_slices(file_paths)

    def show_slices(self, file_paths):
        """
        Creates the thumbnails from the selected file paths

        :param file_paths: the selected file paths
        """

        # If it's the first time that this function is called, the MiniViewer has
        # to be shown
        if self.first_time:
            self.setHidden(False)
            self.first_time = False

        # If the user has willingly hidden the MiniViewer, the Processes are not made
        if self.isHidden():
            pass
        else:
            self.do_nothing = [False] * len(file_paths)

            self.file_paths = file_paths
            self.setMinimumHeight(220)

            self.clearLayouts()

            self.frame = QFrame(self)
            self.frame_final = QFrame(self)

            # Limiting the legend of the thumbnails
            self.nb_char_max = 60

            font = QFont()
            font.setPointSize(9)

            # Reading the images from the file paths
            for idx, file_path in enumerate(self.file_paths.copy()):
                try:
                    self.img.insert(idx, nib.load(file_path))
                except nib.filebasedimages.ImageFileError:
                    print("Error while trying to display the image " + file_path)
                    self.file_paths.remove(file_path)
                except FileNotFoundError:
                    print("File " + file_path + " not existing")
                    self.file_paths.remove(file_path)

            # If we are in the "cursors" display mode
            if self.check_box_slices.checkState() == Qt.Unchecked:

                # Layout to aligne each thumbnail (image + cursors)
                self.h_box_thumb = QHBoxLayout()

                # idx represents the index of the selected image
                for idx in range(min(self.max_scans, len(self.file_paths))):
                    if not self.do_nothing[idx]:

                        # Creating sliders and labels
                        self.boxSlider(idx)
                        self.enableSliders(idx)
                        self.createDimensionLabels(idx)

                        # Getting the sliders value and reading the image data
                        self.indexImage(idx)

                        # Making some pixel modification to display the image correctly
                        self.image2DModifications(idx)

                    self.displayPosValue(idx)

                    w, h = self.im_2D[idx].shape

                    im_Qt = QImage(self.im_2D[idx].data, w, h, QImage.Format_Indexed8)
                    pixm = QPixmap.fromImage(im_Qt)

                    file_path_base_name = os.path.basename(self.file_paths[idx])

                    # imageLabel is the label where the image is displayed (as a pixmap)
                    self.imageLabel.insert(idx, QLabel(self))
                    self.imageLabel[idx].setPixmap(pixm)
                    self.imageLabel[idx].setToolTip(file_path_base_name)

                    self.label_description.insert(idx, ClickableLabel())
                    self.label_description[idx].setFont(font)
                    self.label_description[idx].clicked.connect(self.openTagsPopUp)

                    # Looking for the tag value to display as a legend of the thumbnail
                    file_path_base_name = os.path.relpath(self.file_paths[idx], self.project.folder)
                    self.setThumbnail(file_path_base_name, idx)

                    # Layout that corresponds to the third dimension
                    self.h_box_slider_1 = QHBoxLayout()
                    self.h_box_slider_1.addWidget(self.label3D[idx])
                    self.h_box_slider_1.addWidget(self.txta1[idx])
                    self.h_box_slider_1.addWidget(self.a1[idx])

                    # Layout that corresponds to the fourth dimension
                    self.h_box_slider_2 = QHBoxLayout()
                    self.h_box_slider_2.addWidget(self.label4D[idx])
                    self.h_box_slider_2.addWidget(self.txta2[idx])
                    self.h_box_slider_2.addWidget(self.a2[idx])

                    # Layout that corresponds to the fifth dimension
                    self.h_box_slider_3 = QHBoxLayout()
                    self.h_box_slider_3.addWidget(self.label5D[idx])
                    self.h_box_slider_3.addWidget(self.txta3[idx])
                    self.h_box_slider_3.addWidget(self.a3[idx])

                    # Layout for the three sliders
                    self.v_box_sliders = QVBoxLayout()
                    self.v_box_sliders.addLayout(self.h_box_slider_1)
                    self.v_box_sliders.addLayout(self.h_box_slider_2)
                    self.v_box_sliders.addLayout(self.h_box_slider_3)

                    # Layout that corresponds to the image + the sliders
                    self.h_box = QHBoxLayout()
                    self.h_box.addWidget(self.imageLabel[idx])
                    self.h_box.addLayout(self.v_box_sliders)

                    # Layout that corresponds to the image and sliders + the description
                    self.v_box_thumb = QVBoxLayout()
                    self.v_box_thumb.addLayout(self.h_box)
                    self.v_box_thumb.addWidget(self.label_description[idx])

                    # Layout that will contain all the thumbnails
                    self.h_box_thumb.addLayout(self.v_box_thumb)

                self.frame.setLayout(self.h_box_thumb)

            # If we are in the "all slices" display mode
            else:

                self.h_box_images = QHBoxLayout()
                self.h_box_images.setSpacing(10)
                self.v_box_scans = QVBoxLayout()

                # idx represents the index of the selected image
                for idx in range(len(self.file_paths)):
                    file_path_base_name = os.path.relpath(self.file_paths[idx], self.project.folder)

                    self.label_description.insert(idx, ClickableLabel())
                    self.label_description[idx].setFont(font)
                    self.label_description[idx].clicked.connect(self.openTagsPopUp)

                    # Looking for the tag value to display as a legend of the thumbnail
                    self.setThumbnail(file_path_base_name, idx)

                    # Depending of the dimension of the image, the legend of each image
                    # and the number of images to display will change
                    if not self.do_nothing[idx]:
                        if len(self.img[idx].shape) == 3:
                            nb_slices = self.img[idx].shape[2]
                            txt = "Slice n°"
                        elif len(self.img[idx].shape) == 4:
                            nb_slices = self.img[idx].shape[3]
                            txt = "Time n°"
                        elif len(self.img[idx].shape) == 5:
                            nb_slices = self.img[idx].shape[4]
                            txt = "Study n°"
                        else:
                            nb_slices = 0

                        # Limiting the number of images to the number chosen by the user
                        for i in range(min(nb_slices, int(self.line_edit_nb_slices.text()))):
                            pixm = self.image_to_pixmap(self.img[idx], i)

                            self.v_box = QVBoxLayout()

                            # label corresponds to the label where one image is displayed
                            label = QLabel(self)
                            label.setPixmap(pixm)
                            label.setToolTip(os.path.basename(self.file_paths[idx]))

                            # Legend of the image (depends on the number of dimensions)
                            label_info = QLabel()
                            label_info.setFont(font)
                            label_info.setText(txt + str(i + 1))
                            label_info.setAlignment(QtCore.Qt.AlignCenter)

                            self.v_box.addWidget(label)
                            self.v_box.addWidget(label_info)

                            # This layout allows to chain each image
                            self.h_box_images.addLayout(self.v_box)
                        self.v_box_scans.addLayout(self.h_box_images)
                        self.v_box_scans.addWidget(self.label_description[idx])
                self.frame.setLayout(self.v_box_scans)

            # Adding a scroll area if the thumbnails are too large
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidget(self.frame)

            self.h_box_check_box = QHBoxLayout()

            if self.check_box_slices.isChecked():
                self.h_box_check_box.addStretch(1)
                self.label_nb_slices.setHidden(False)
                self.line_edit_nb_slices.setHidden(False)
                self.h_box_check_box.addWidget(self.label_nb_slices)
                self.h_box_check_box.addWidget(self.line_edit_nb_slices)
                self.check_box_cursors.setHidden(True)
            else:
                self.check_box_cursors.setHidden(False)
                self.h_box_check_box.addWidget(self.check_box_cursors)
                self.h_box_check_box.addStretch(1)
                self.label_nb_slices.setHidden(True)
                self.line_edit_nb_slices.setHidden(True)

            self.h_box_check_box.addWidget(self.check_box_slices)

            self.v_box_final.addLayout(self.h_box_check_box)
            self.v_box_final.addWidget(self.scroll_area)

    """def check_differences(self, file_paths):
        old_to_new = []
        self.do_nothing = [False, False, False]
        for idx_old, file_path in enumerate(self.file_paths):
            if file_path in file_paths:
                idx_new = file_paths.index(file_path)
                old_to_new.append((idx_old, idx_new))
                #if idx_new == idx_old:
                self.do_nothing[idx_new] = True

        for tp in old_to_new:
            idx_old = tp[0]
            idx_new = tp[1]
            self.shift_thumbnail(idx_old, idx_new)

    def shift_thumbnail(self, idx_old, idx_new):

        self.im_2D[idx_new] = self.im_2D[idx_old]

        self.a1[idx_new].setMaximum(self.a1[idx_old].maximum())
        self.a2[idx_new].setMaximum(self.a2[idx_old].maximum())
        self.a3[idx_new].setMaximum(self.a3[idx_old].maximum())

        self.a1[idx_new].setValue(self.a1[idx_old].value())
        self.a2[idx_new].setValue(self.a2[idx_old].value())
        self.a3[idx_new].setValue(self.a3[idx_old].value())"""

    """def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()"""

    def setThumbnail(self, file_path_base_name, idx):
        """
        Sets the thumbnail tag value under the image frame

        :param file_path_base_name: basename of the selected path
        :param idx: index of the image
        :return:
        """
        # Looking for the tag value to display as a legend of the thumbnail
        for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
            if scan == file_path_base_name:
                value = self.project.session.get_value(COLLECTION_CURRENT, scan, self.config.getThumbnailTag())
                if value is not None:
                    self.label_description[idx].setText(str(value)[:self.nb_char_max])
                else:
                    self.label_description[idx].setText(data_browser.not_defined_value[:self.nb_char_max])
                self.label_description[idx].setToolTip(os.path.basename(self.config.getThumbnailTag()))

    def clearLayouts(self):
        """
        Clears the final layout
        """

        for i in reversed(range(self.v_box_final.count())):
            if self.v_box_final.itemAt(i).widget() is not None:
                self.v_box_final.itemAt(i).widget().setParent(None)

    def createLayouts(self):
        """
        Creates the layouts
        """

        self.h_box_images = QHBoxLayout()
        self.h_box_images.setSpacing(10)
        self.v_box = QVBoxLayout()
        self.v_box_final = QVBoxLayout()
        self.h_box_slider_1 = QHBoxLayout()
        self.h_box_slider_2 = QHBoxLayout()
        self.h_box_slider_3 = QHBoxLayout()
        self.v_box_sliders = QVBoxLayout()
        self.h_box = QHBoxLayout()
        self.h_box_check_box = QHBoxLayout()
        self.v_box_thumb = QVBoxLayout()
        self.h_box_thumb = QHBoxLayout()

    def image_to_pixmap(self, im, i):
        """
        Creates a 2D pixmap from a N-D Nifti image

        :param im: Nifti image
        :param i: index of the slide
        :return: the corresponding pixmap
        """

        # The image to display depends on the dimension of the image
        # In the 3D case, each slice is displayed
        if len(im.shape) == 3:
            im_2D = im.get_data()[:, :, i].copy()

        # In the 4D case, each middle slice of the third dimension is displayed
        # for each time in the fourth dimension
        elif len(im.shape) == 4:
            im_3D = im.get_data()[:, :, :, i].copy()
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        # In the 5D case, each first time of the fourth dimension and its middle
        # slice of the third dimension is displayed
        elif len(im.shape) == 5:
            im_4D = im.get_data()[:, :, :, :, i].copy()
            im_3D = im_4D[:, :, :, 1]
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        else:
            im_2D = [0]

        # Making some pixel modification to display the image correctly
        im_2D = self.image2DModifications(0, im_2D)

        w, h = im_2D.shape

        im_Qt = QImage(im_2D.data, w, h, QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(im_Qt)

        return pixm

    def createSlider(self, maxm=0, minm=0, pos=0):
        """
        Creates a slider

        :param maxm: slider's maximum
        :param minm: slider's minimum
        :param pos: slider's initial value
        :return: the slider object
        """
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickInterval(1)
        slider.setMaximum(maxm)
        slider.setMinimum(minm)
        slider.setValue(pos)
        slider.setEnabled(False)
        return slider

    def enableSliders(self, idx):
        """
        Enables each slider of the selected index

        :param idx: the selected index
        """
        self.a1[idx].setEnabled(True)
        self.a2[idx].setEnabled(True)
        self.a3[idx].setEnabled(True)

    def boxSlider(self, idx):
        """
        Creates sliders, their connections and thumbnail labels for a selected index

        :param idx: the selected index
        """
        self.a1.insert(idx, self.createSlider(0, 0, 0))
        self.a2.insert(idx, self.createSlider(0, 0, 0))
        self.a3.insert(idx, self.createSlider(0, 0, 0))

        self.a1[idx].valueChanged.connect(partial(self.changePosValue, idx, 1))
        self.a2[idx].valueChanged.connect(partial(self.changePosValue, idx, 2))
        self.a3[idx].valueChanged.connect(partial(self.changePosValue, idx, 3))

        self.txta1.insert(idx, self.createFieldValue())
        self.txta2.insert(idx, self.createFieldValue())
        self.txta3.insert(idx, self.createFieldValue())

    def displayPosValue(self, idx):
        """
        Displays the position of each cursor for the selected index

        :param idx: the selected index
        """
        self.txta1[idx].setText(str(self.a1[idx].value() + 1) + ' / ' + str(self.a1[idx].maximum() + 1))
        self.txta2[idx].setText(str(self.a2[idx].value() + 1) + ' / ' + str(self.a2[idx].maximum() + 1))
        self.txta3[idx].setText(str(self.a3[idx].value() + 1) + ' / ' + str(self.a3[idx].maximum() + 1))

    def createFieldValue(self):
        """
        Creates a field where will be displayed the position of a cursor

        :return: the corresponding field
        """
        fieldValue = QLineEdit()
        fieldValue.setEnabled(False)
        fieldValue.setFixedWidth(50)
        fieldValue.setAlignment(Qt.AlignCenter)
        fieldValue.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        font = QFont()
        font.setPointSize(9)
        fieldValue.setFont(font)
        return fieldValue

    def createDimensionLabels(self, idx):
        """
        Creates the dimension labels for the selected index

        :param idx: the selected index
        """
        font = QFont()
        font.setPointSize(9)

        self.label3D.insert(idx, QLabel())
        self.label4D.insert(idx, QLabel())
        self.label5D.insert(idx, QLabel())

        self.label3D[idx].setFont(font)
        self.label4D[idx].setFont(font)
        self.label5D[idx].setFont(font)

        self.label3D[idx].setText('3D: ')
        self.label4D[idx].setText('4D: ')
        self.label5D[idx].setText('5D: ')

    def changePosValue(self, idx, cursor_to_change):
        """
        Changes the value of a cursor for the selected index

        :param idx: the selected index
        :param cursor_to_change: the cursor to change (1, 2 or 3)
        """
        # If the "Chain cursors" mode is not selected, there is nothing to do
        if self.check_box_cursors.checkState() == Qt.Unchecked:
            self.navigImage(idx)
        else:
            # Checking with cursor has been modified
            if cursor_to_change == 1:
                cursor = self.a1
            elif cursor_to_change == 2:
                cursor = self.a2
            else:
                cursor = self.a3

            # Loop on the thumbnails
            for idx_loop in range(min(self.max_scans, len(self.file_paths))):
                # Disconnecting the connection when changing other cursors values
                cursor[idx_loop].valueChanged.disconnect()
                # Do something only when the cursor is not the one that has been changed by the user
                if idx_loop != idx:
                    if cursor[idx].value() == cursor[idx].maximum():
                        value = cursor[idx_loop].maximum()

                    elif cursor[idx].value() == cursor[idx].minimum():
                        value = cursor[idx_loop].minimum()

                    else:
                        # Updating the new value as the value of the cursor that has been changed by the user
                        value = round((cursor[idx_loop].maximum() + 1) * (cursor[idx].value() + 1) /
                                      max(1, cursor[idx].maximum() + 1))
                        value = min(cursor[idx_loop].maximum(), value - 1)
                        value = max(0, int(value))
                    cursor[idx_loop].setValue(value)

                # Changing the image to show
                self.navigImage(idx_loop)
                # Reconnecting
                cursor[idx_loop].valueChanged.connect(partial(self.changePosValue, idx_loop, cursor_to_change))

    def navigImage(self, idx):
        """
        Displays the 2D image for the selected index

        :param idx: the selected index
        """
        self.indexImage(idx)
        self.displayPosValue(idx)

        self.image2DModifications(idx)
        w, h = self.im_2D[idx].shape

        image = QImage(self.im_2D[idx].data, w, h, QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(image)
        self.imageLabel[idx].setPixmap(pixm)

    def indexImage(self, idx):
        """
        Updates the sliders values depending on the size of the selected image

        :param idx: the selected index
        """
        # Getting the sliders value
        sl1 = self.a1[idx].value()
        sl2 = self.a2[idx].value()
        sl3 = self.a3[idx].value()

        # Depending on the dimension, reading the image data and changing the cursors maximum
        if len(self.img[idx].shape) == 3:
            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1].copy())
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(0)
            self.a3[idx].setMaximum(0)
        if len(self.img[idx].shape) == 4:
            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1, sl2].copy())
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
            self.a3[idx].setMaximum(0)
        if len(self.img[idx].shape) == 5:
            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1, sl2, sl3].copy())
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
            self.a3[idx].setMaximum(self.img[idx].shape[4] - 1)

    def openTagsPopUp(self):
        """
        Opens a pop-up to select the legend of the thumbnails
        """
        self.popUp = PopUpSelectTag(self.project)
        self.popUp.setWindowTitle("Select the image viewer tag")
        if self.popUp.exec_():

            self.verify_slices(self.file_paths)

    def image2DModifications(self, idx, im2D=None):
        """
        Applies modifications to the image to display it correctly

        :param idx: the selected index
        :param im2D: image to modify
        """
        if im2D is not None:
            im2D = rotate(im2D, -90, reshape=False)
            im2D = np.uint8((im2D - im2D.min()) / im2D.ptp() * 255.0)
            im2D = resize(im2D, (128, 128))
            im2D = (im2D * 255).astype(np.uint8)
            return im2D
        else:
            self.im_2D[idx] = rotate(self.im_2D[idx], -90, reshape=False)
            self.im_2D[idx] = np.uint8((self.im_2D[idx] - self.im_2D[idx].min())
                                       / self.im_2D[idx].ptp() * 255.0)
            self.im_2D[idx] = resize(self.im_2D[idx], (128, 128))
            self.im_2D[idx] = (self.im_2D[idx] * 255).astype(np.uint8)
