from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QLabel, QScrollArea, QFrame, QSlider, QLineEdit, QSizePolicy, QCheckBox
import os

from Utils.Tools import ClickableLabel

from PopUps.Ui_Select_Tag import Ui_Select_Tag

from SoftwareProperties import Config
import scipy.misc as misc

import nibabel as nib
from scipy.ndimage import rotate  # to work with NumPy arrays
import numpy as np  # a N-dimensional array object
from SoftwareProperties.Config import Config


class MiniViewer(QWidget):
    # TODO: IF THE CHECKBOX TO SHOW ALL SLICES IS CHECKED OR UNCHECKED IN THE PREFERENCES POP-UP, IT DOES NOT UPDATE THE
    # TODO: CHECKBOX OF THE MINIVIEWER : EVEN WITH SIGNALS IT DOES NOT WORK BECAUSE WE NEED TO CREATE TWO SEVERAL OBJECTS

    # TODO: HANDLE THE MULTI SELECTION

    def __init__(self, database):

        super().__init__()

        self.database = database
        self.first_time = True

        self.setHidden(True)
        self.nb_labels = 6

        self.config = Config()
        # Updating the check_box if the preferences are changed

        self.labels = QWidget()
        self.scroll_area = QScrollArea()
        self.frame = QFrame()
        self.scroll_area.setWidget(self.frame)
        self.frame_final = QFrame()

        self.im_2D = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.txta1 = []
        self.txta2 = []
        self.txta3 = []
        self.imageLabel = []
        self.img = []
        self.label_description = []

        self.createLayouts()

        self.setLayout(self.v_box_final)

        self.check_box = QCheckBox('Show all slices (no cursors)')
        if self.config.getShowAllSlices() == 'yes':
            self.check_box.setCheckState(Qt.Checked)
        else:
            self.check_box.setCheckState(Qt.Unchecked)
        self.check_box.stateChanged.connect(self.check_box_state_changed)

        self.label_nb_slices = QLabel()
        self.label_nb_slices.setText("Maximum number of slices: ")

        self.line_edit_nb_slices = QLineEdit()
        self.line_edit_nb_slices.setText(str(self.config.getNbAllSlicesMax()))
        self.line_edit_nb_slices.returnPressed.connect(self.update_nb_slices)

        self.file_paths = ""

    def update_nb_slices(self):
        nb_slices = self.line_edit_nb_slices.text()
        self.config.setNbAllSlicesMax(nb_slices)
        self.verify_slices(self.file_paths)

    def check_box_state_changed(self):
        if self.check_box.checkState() == Qt.Checked:
            self.config.setShowAllSlices('yes')
        elif self.check_box.checkState() == Qt.Unchecked:
            self.config.setShowAllSlices('no')
        self.verify_slices(self.file_paths)

    def verify_slices(self, file_paths):
        """ For a multi-selection of scans, the 'Show all slices' check box cannot be checked. """
        self.config = Config()
        if len(file_paths) > 1:
            self.config.setShowAllSlices('no')
            self.check_box.setCheckState(Qt.Unchecked)
            self.check_box.setCheckable(False)
        else:
            self.check_box.setCheckable(True)
        self.show_slices(file_paths)

    def show_slices(self, file_paths):

        if self.first_time:
            self.setHidden(False)
            self.first_time = False

        if self.isHidden():
            pass
        else:
            self.do_nothing = [False] * len(file_paths)

            self.file_paths = file_paths
            self.setMinimumHeight(220)

            self.clearLayouts()

            self.frame = QFrame(self)
            self.frame_final = QFrame(self)
            max_scans = 5
            nb_char_max = 60
            font = QFont()
            font.setPointSize(9)

            for idx, file_path in enumerate(self.file_paths):
                self.img.insert(idx, nib.load(file_path))

            if self.check_box.checkState() == Qt.Unchecked:

                self.h_box_thumb = QHBoxLayout()

                for idx in range(min(max_scans, len(self.file_paths))):
                    if not self.do_nothing[idx]:

                        self.boxSlider(idx)
                        self.enableSliders(idx)

                        sl1 = self.a1[idx].value()
                        sl2 = self.a2[idx].value()
                        sl3 = self.a3[idx].value()

                        if (len(self.img[idx].shape) == 3):
                            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1].copy())
                            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
                            self.a2[idx].setMaximum(0)
                            self.a3[idx].setMaximum(0)
                        if (len(self.img[idx].shape) == 4):
                            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1, sl2].copy())
                            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
                            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
                            self.a3[idx].setMaximum(0)
                        if (len(self.img[idx].shape) == 5):
                            self.im_2D.insert(idx, self.img[idx].get_data()[:, :, sl1, sl2, sl3].copy())
                            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
                            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
                            self.a3[idx].setMaximum(self.img[idx].shape[4] - 1)

                        self.im_2D[idx] = rotate(self.im_2D[idx], -90, reshape=False)
                        self.im_2D[idx] = np.uint8(
                            (self.im_2D[idx] - self.im_2D[idx].min()) / self.im_2D[idx].ptp() * 255.0)
                        self.im_2D[idx] = misc.imresize(self.im_2D[idx], (128, 128))

                    ############################
                    self.displayPosValue(idx)

                    w, h = self.im_2D[idx].shape

                    im_Qt = QImage(self.im_2D[idx].data, w, h, QImage.Format_Indexed8)
                    pixm = QPixmap.fromImage(im_Qt)

                    file_path_base_name = os.path.basename(self.file_paths[idx])[:-4 or None]

                    self.imageLabel.insert(idx, QLabel(self))
                    self.imageLabel[idx].setPixmap(pixm)
                    self.imageLabel[idx].setToolTip(file_path_base_name)

                    self.label_description.insert(idx, ClickableLabel())
                    self.label_description[idx].setFont(font)
                    self.label_description[idx].clicked.connect(self.openTagsPopUp)

                    for scan in self.database.getScans():
                        if scan.scan == file_path_base_name:
                            for tag in self.database.getTags():
                                if tag.tag == self.config.getThumbnailTag():
                                    self.label_description[idx].setText \
                                        (str(self.database.getValue(scan.scan, tag.tag).current_value)[:nb_char_max])
                                    self.label_description[idx].setToolTip \
                                        (os.path.basename(self.config.getThumbnailTag()))

                    self.h_box_slider_1 = QHBoxLayout()
                    self.h_box_slider_1.addWidget(self.txta1[idx])
                    self.h_box_slider_1.addWidget(self.a1[idx])

                    self.h_box_slider_2 = QHBoxLayout()
                    self.h_box_slider_2.addWidget(self.txta2[idx])
                    self.h_box_slider_2.addWidget(self.a2[idx])

                    self.h_box_slider_3 = QHBoxLayout()
                    self.h_box_slider_3.addWidget(self.txta3[idx])
                    self.h_box_slider_3.addWidget(self.a3[idx])

                    self.v_box_sliders = QVBoxLayout()
                    self.v_box_sliders.addLayout(self.h_box_slider_1)
                    self.v_box_sliders.addLayout(self.h_box_slider_2)
                    self.v_box_sliders.addLayout(self.h_box_slider_3)

                    self.h_box = QHBoxLayout()
                    self.h_box.addWidget(self.imageLabel[idx])
                    self.h_box.addLayout(self.v_box_sliders)

                    self.v_box_thumb = QVBoxLayout()
                    self.v_box_thumb.addLayout(self.h_box)
                    self.v_box_thumb.addWidget(self.label_description[idx])

                    self.h_box_thumb.addLayout(self.v_box_thumb)


                # self.h_box.addStretch(1)
                self.frame.setLayout(self.h_box_thumb)

            else:
                self.h_box_images = QHBoxLayout()
                self.h_box_images.setSpacing(10)
                self.v_box_scans = QVBoxLayout()

                for idx in range(len(self.file_paths)):
                    file_path_base_name = os.path.basename(self.file_paths[idx])[:-4 or None]

                    self.label_description.insert(idx, ClickableLabel())
                    self.label_description[idx].setFont(font)
                    self.label_description[idx].clicked.connect(self.openTagsPopUp)
                    for scan in self.database.getScans():
                        if scan.scan == file_path_base_name:
                            for tag in self.database.getTags():
                                if tag.tag == self.config.getThumbnailTag():
                                    self.label_description[idx].setText \
                                        (str(self.database.getValue(scan.scan, tag.tag).current_value)[:nb_char_max])
                                    self.label_description[idx].setToolTip \
                                        (os.path.basename(self.config.getThumbnailTag()))

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

                        for i in range(min(nb_slices, int(self.line_edit_nb_slices.text()))):
                            pixm = self.image_to_pixmap(self.img[idx], i)

                            self.v_box = QVBoxLayout()

                            label = QLabel(self)
                            label.setPixmap(pixm)
                            label.setToolTip(os.path.basename(self.file_paths[idx]))

                            label_info = QLabel()
                            label_info.setFont(font)
                            label_info.setText(txt + str(i + 1))
                            label_info.setAlignment(QtCore.Qt.AlignCenter)

                            self.v_box.addWidget(label)
                            self.v_box.addWidget(label_info)

                            self.h_box_images.addLayout(self.v_box)
                        self.v_box_scans.addLayout(self.h_box_images)
                        self.v_box_scans.addWidget(self.label_description[idx])
                self.frame.setLayout(self.v_box_scans)

            self.scroll_area = QScrollArea()
            self.scroll_area.setWidget(self.frame)

            self.h_box_check_box = QHBoxLayout()
            self.h_box_check_box.addStretch(1)

            if self.check_box.isChecked():
                self.label_nb_slices.setHidden(False)
                self.line_edit_nb_slices.setHidden(False)
                self.h_box_check_box.addWidget(self.label_nb_slices)
                self.h_box_check_box.addWidget(self.line_edit_nb_slices)
            else:
                self.label_nb_slices.setHidden(True)
                self.line_edit_nb_slices.setHidden(True)

            self.h_box_check_box.addWidget(self.check_box)

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

    def clearLayouts(self):

        for i in reversed(range(self.v_box_final.count())):
            if self.v_box_final.itemAt(i).widget() is not None:
                self.v_box_final.itemAt(i).widget().setParent(None)

    def createLayouts(self):

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
        # The image to show depends on the dimension of the image
        if len(im.shape) == 3:
            im_2D = im.get_data()[:, :, i].copy()

        elif len(im.shape) == 4:
            im_3D = im.get_data()[:, :, :, i].copy()
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        elif len(im.shape) == 5:
            im_4D = im.get_data()[:, :, :, :, i].copy()
            im_3D = im_4D[:, :, :, 1]
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        else:
            im_2D = [0]

        im_2D = rotate(im_2D, -90, reshape=False)
        im_2D = np.uint8((im_2D - im_2D.min()) / im_2D.ptp() * 255.0)
        im_2D = misc.imresize(im_2D, (128, 128))

        w, h = im_2D.shape

        im_Qt = QImage(im_2D.data, w, h, QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(im_Qt)

        return pixm

    def createSlider(self ,maxm=0 ,minm=0 ,pos=0):
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickInterval(1)
        slider.setMaximum(maxm)
        slider.setMinimum(minm)
        slider.setValue(pos)
        slider.setEnabled(False)
        return slider

    def enableSliders(self, idx):
        self.a1[idx].setEnabled(True)
        self.a2[idx].setEnabled(True)
        self.a3[idx].setEnabled(True)

    def boxSlider(self, idx):

        self.a1.insert(idx, self.createSlider(0, 0, 0))
        self.a2.insert(idx, self.createSlider(0, 0, 0))
        self.a3.insert(idx, self.createSlider(0, 0, 0))

        self.a1[idx].valueChanged.connect(lambda: self.changePosValue(idx))
        self.a2[idx].valueChanged.connect(lambda: self.changePosValue(idx))
        self.a3[idx].valueChanged.connect(lambda: self.changePosValue(idx))

        self.txta1.insert(idx, self.createFieldValue())
        self.txta2.insert(idx, self.createFieldValue())
        self.txta3.insert(idx, self.createFieldValue())


    def displayPosValue(self, idx):
        self.txta1[idx].setText(str(self.a1[idx].value( ) +1 ) +' /  ' +str(self.a1[idx].maximum( ) +1))
        self.txta2[idx].setText(str(self.a2[idx].value( ) +1 ) +' /  ' +str(self.a2[idx].maximum( ) +1))
        self.txta3[idx].setText(str(self.a3[idx].value( ) +1 ) +' /  ' +str(self.a3[idx].maximum( ) +1))

    def createFieldValue(self):
        fieldValue = QLineEdit()
        fieldValue.setEnabled(False)
        fieldValue.setFixedWidth(50)
        fieldValue.setAlignment(Qt.AlignCenter)
        fieldValue.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        font = QFont()
        font.setPointSize(9)
        fieldValue.setFont(font)
        return fieldValue

    def changePosValue(self, idx):
        self.navigImage(idx)

    def navigImage(self, idx):
        self.indexImage(idx)
        self.displayPosValue(idx)

        self.im_2D[idx] = rotate(self.im_2D[idx], -90, reshape=False)
        self.im_2D[idx] = np.uint8((self.im_2D[idx] - self.im_2D[idx].min()) / self.im_2D[idx].ptp() * 255.0)
        self.im_2D[idx] = misc.imresize(self.im_2D[idx], (128, 128))

        w, h = self.im_2D[idx].shape

        image = QImage(self.im_2D[idx].data ,w ,h ,QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(image)
        self.imageLabel[idx].setPixmap(pixm)

    def indexImage(self, idx):
        sl1 = self.a1[idx].value()
        sl2 = self.a2[idx].value()
        sl3 = self.a3[idx].value()
        if (len(self.img[idx].shape) == 3):
            self.im_2D[idx] = self.img[idx].get_data()[:, :, sl1].copy()
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(0)
            self.a3[idx].setMaximum(0)
        if (len(self.img[idx].shape) == 4):
            self.im_2D[idx] = self.img[idx].get_data()[:, :, sl1, sl2].copy()
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
            self.a3[idx].setMaximum(0)
        if (len(self.img[idx].shape) == 5):
            self.im_2D[idx] = self.img[idx].get_data()[:, :, sl1, sl2, sl3].copy()
            self.a1[idx].setMaximum(self.img[idx].shape[2] - 1)
            self.a2[idx].setMaximum(self.img[idx].shape[3] - 1)
            self.a3[idx].setMaximum(self.img[idx].shape[4] - 1)

    def openTagsPopUp(self):
        self.popUp = Ui_Select_Tag(self.database)
        if self.popUp.exec_() == QDialog.Accepted:
            self.verify_slices(self.file_paths)
