# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TemplateLoaderDialog
                                 A QGIS plugin
 Build map from template
                             -------------------
        begin                : 2014-08-20
        copyright            : (C) 2014 by PnC
        email                : amandine.sahl@cevennes-parcnational.fr
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

from PyQt4 import QtCore, QtGui
from ui_templateloader import Ui_TemplateLoader
# create the dialog for zoom to point


class TemplateLoaderDialog(QtGui.QDialog, Ui_TemplateLoader):
    def __init__(self):
        #super(ZoomToCoordinatesDialog,self).__init__(parent)
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_TemplateLoader()      
      
        self.ui.setupUi(self)
        
