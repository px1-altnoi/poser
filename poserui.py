"""
Project Name: Trigger
File name: alt_poser.py
Licence: MIT LICENCE
Author : altnoi
Last update: 2020_09_22
INFORMATION:
This code is PoC. It is subject to change from the production version specifications.
"""
# todo: [ADD] JSON data check application factor
# todo: [Refactor]
import poser_lib
# this reload should be removed before release
reload(poser_lib)
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui

# global
DEFAULT_DIR = cmds.workspace(q=True, active=True)
DIRECTORY = os.path.join(DEFAULT_DIR, 'pose_lib')

def maya_main_window():
    main_wnd_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_wnd_ptr), QtWidgets.QWidget)


class alt_poser(QtWidgets.QDialog):
    FILE_FILTERS = "Json files(*.json);;All files(*.*)"
    selected_filter = "Json files(*.json)"
    FILE_IFILTERS = "image files(*.png, *.jpg);;All files(*.*)"
    selected_Ifilter = "image files(*.png, *.jpg)"

    WINDOW_TITLE = "Alt_poser"
    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = alt_poser()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(alt_poser, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(100)

        self.library = poser_lib.PoserLibrary()

        self.geometry = None
        self.file_path = cmds.workspace(q=True, active=True)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.reload_act()

    def create_widgets(self):
        self.save_label = QtWidgets.QLabel("name")
        self.save_le = QtWidgets.QLineEdit()
        self.save_btn = QtWidgets.QPushButton("save")

        SIZE = 64
        BUFFER = 12
        self.main_list_wgt = QtWidgets.QListWidget()
        self.main_list_wgt.setViewMode(QtWidgets.QListWidget.IconMode)
        self.main_list_wgt.setIconSize(QtCore.QSize(SIZE, SIZE))
        self.main_list_wgt.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.main_list_wgt.setGridSize(QtCore.QSize(SIZE + BUFFER, SIZE + BUFFER))
        self.main_list_wgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_list_wgt.customContextMenuRequested.connect(self.on_right_click)

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.chosefld_btn = QtWidgets.QPushButton("Choose folder")
        self.adv_mode_btn = QtWidgets.QPushButton("Advance Mode")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        save_grp = QtWidgets.QVBoxLayout()
        save_grp.addWidget(self.save_label)
        save_textbox_grp = QtWidgets.QHBoxLayout()
        save_textbox_grp.addWidget(self.save_le)
        save_textbox_grp.addWidget(self.save_btn)
        save_grp.addLayout(save_textbox_grp)
        main_layout.addLayout(save_grp)

        main_layout.addWidget(self.main_list_wgt)

        btn_grp = QtWidgets.QHBoxLayout()
        btn_grp.addStretch()
        btn_grp.addWidget(self.refresh_btn)
        btn_grp.addWidget(self.chosefld_btn)
        btn_grp.addWidget(self.adv_mode_btn)
        main_layout.addLayout(btn_grp)

    def create_connections(self):
        self.main_list_wgt.doubleClicked.connect(self.load_data)
        self.save_btn.clicked.connect(self.save_act)
        self.adv_mode_btn.clicked.connect(self.advance_mode)
        self.refresh_btn.clicked.connect(self.reload_act)
        self.chosefld_btn.clicked.connect(self.change_folder)

    def save_act(self):
        self.library.save(DIRECTORY, name=self.save_le.text())
        self.save_le.setText("")
        self.reload_act()

    def reload_act(self):
        self.main_list_wgt.clear()
        self.library.find(DIRECTORY)
        # print self.library.items()

        for name, info in self.library.items():
            item = QtWidgets.QListWidgetItem(name)

            img_path = info.get('imagepath')
            if os.path.exists(img_path):
                icon = QtGui.QIcon(img_path)
            else:
                icon = QtGui.QIcon(os.path.join("C:\Users\kenta\Documents\maya\controllerLibrary", 'noimage.jpg'))
            item.setIcon(icon)
            self.main_list_wgt.addItem(item)

    def on_right_click(self, pos):
        menu = QtWidgets.QMenu(self)
        rename = QtWidgets.QAction('Rename', self, triggered=self.rename)
        menu.addAction(rename)
        change_image = QtWidgets.QAction('Change image', self, triggered=self.change_image)
        menu.addAction(change_image)
        remove = QtWidgets.QAction('remove', self, triggered=self.remove)
        menu.addAction(remove)
        menu.exec_(self.main_list_wgt.mapToGlobal(pos))

    def rename(self):
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            text, status = QtWidgets.QInputDialog.getText(self, "new name", "name:")
            if status:
                item = self.main_list_wgt.itemFromIndex(index)
                old_name = item.text()
                item.setText(text)
                new_name = item.text()
                status = self.library.rename(old_name, new_name, DIRECTORY)
                if status == 1:
                    item.setText(old_name)
                    QtWidgets.QMessageBox.warning(self, "Warning", "file already exists! cannot overwrite.")
                self.reload_act()

    def change_image(self):
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            item = self.main_list_wgt.itemFromIndex(index)
            tgt_name = item.text()
            tgt_path = os.path.join(DIRECTORY, '%s.json' % tgt_name)
            ipath, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Open image", "", self.FILE_IFILTERS, self.selected_Ifilter)
            self.library.change_image(tgt_path, ipath)
            self.reload_act()

    def remove(self):
        button_pressed = QtWidgets.QMessageBox.question(self, "Question", "Would you like to DELETE this file(This operation is irrevocable)?")
        if button_pressed == QtWidgets.QMessageBox.Yes:
            index = self.main_list_wgt.currentIndex()
            item = self.main_list_wgt.itemFromIndex(index)
            name = item.text()
            full_path = os.path.join(DIRECTORY, '%s.json' % name)
            if os.path.exists(full_path):
                os.remove(full_path)
        else:
            print("Cancelled")

        self.reload_act()

    def advance_mode(self):
        # todo: create advance mode
        QtWidgets.QMessageBox.information(self, "Info", "place holder. function under construction")

    def change_folder(self):
        global DIRECTORY
        new_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dir", DIRECTORY)
        if new_dir:
            DIRECTORY = new_dir
        self.reload_act()

    def load_data(self):
        index = self.main_list_wgt.currentIndex()
        if index.isValid():
            item = self.main_list_wgt.itemFromIndex(index)
            tgt_name = item.text()
            tgt_path = os.path.join(DIRECTORY, '%s.json' % tgt_name)
            self.library.load(tgt_path)
            
    # Main Window Events
    def showEvent(self, e):
        super(alt_poser, self).showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, alt_poser):
            super(alt_poser, self).closeEvent(e)
            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    try:
        altpos_ui.close()
        altpos_ui.deleteLater()
    except:
        pass

    altpos_ui = alt_poser()
    altpos_ui.show()