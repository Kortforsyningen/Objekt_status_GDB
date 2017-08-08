# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Objekt_status_GDBDialog
                                 A QGIS plugin
 find GDB objects
                             -------------------
        begin                : 2017-06-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Mafa/sdfe
        email                : mafal@sdfe.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Objekt_status_GDB_dialog_base.ui'))
FORM_CLASSII, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'progressbar.ui'))

class Objekt_status_GDBDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Objekt_status_GDBDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

class Objekt_status_GDBDialogII(QtGui.QDialog, FORM_CLASSII):
    def __init__(self, parent=None):
        """Constructor."""
        super(Objekt_status_GDBDialogII, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)