# -*- coding: utf-8 -*-
"""
/***************************************************************************
 templateLoader
                                 A QGIS plugin
 Build map from template
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-09-04
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Parc national des Cévennes
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

import os.path

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from distutils.dir_util import copy_tree


from qgis.core import QgsApplication, QgsProject

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .templateLoader_dialog import templateLoaderDialog


class templateLoader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'templateLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&template Loader')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.add_profile_data()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('templateLoader', message)


    def add_profile_data(self):
        """
            Add templates and resources from plugin to user profile
        """
        # Paths to source files and qgis profile directory
        source_profile = os.path.join(self.plugin_dir, 'profile')
        profile_home = QgsApplication.qgisSettingsDirPath()

        copy_tree(source_profile, profile_home, update=1)


    def layout_loader(self, template_file_name, layout_name, title_text):
        """ Generate the layout """
        from qgis.core import (
            QgsProject,
            QgsPrintLayout,
            QgsReadWriteContext,
            QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayerTree
        )
        from qgis.gui import QgsMessageBar
        from PyQt5.QtXml import QDomDocument

        template_file_name = '/home/sahl/dev/plugins_qgis/qgis3/test_template.qpt'
        layout_name = 'Custom Map'
        title_text = 'New Title'


        project = QgsProject.instance()
        manager = project.layoutManager()

        # test if layout already exists and remove it
        existing_layout = manager.layoutByName(layout_name)
        if existing_layout:
            manager.removeLayout(existing_layout)

        layout = QgsPrintLayout(project)

        layout.initializeDefaults()

        # Load template file and load it into the layout (l)

        template_file = open(template_file_name, 'r+', encoding='utf-8')
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)
        layout.loadFromTemplate(document, QgsReadWriteContext())


        self.iface.messageBar().pushMessage(
            "Template load", template_file_name
        )
        # Give the layout a name (must be unique)
        layout.setName(layout_name)

        ## Extent of current canvas
        if type(layout.itemById('main-map')) is QgsLayoutItemMap:
            canvas = self.iface.mapCanvas()
            my_map = layout.itemById('main-map')

            my_map.setExtent(canvas.extent())

            # Scale
            # TODO get from interface
            # my_map.setScale(1000.0)


        ## Change title QgsLayoutItemLabel
        if type(layout.itemById('main-title')) is QgsLayoutItemLabel:
            my_title = layout.itemById('main-title')
            my_title.setText("Subtitle Her COCOe")
        else:
            print('no title')

        ## Legend
        if type(layout.itemById('main-legend')) is QgsLayoutItemLegend:
            legend = layout.itemById('main-legend')
            legend.setTitle("Légende")
            ## Add only active layers
            # Checks layer tree objects and stores them in a list. This includes csv tables
            checked_layers = [
                layer.name() for layer in project.layerTreeRoot().children()
                if layer.isVisible()
            ]
            # get map layer objects of checked layers by matching their names and store those in a list
            layersToAdd = [
                layer for layer in project.mapLayers().values()
                if layer.name() in checked_layers
            ]
            layers_to_remove = [layer for layer in project.mapLayers().values() if layer.name() not in checked_layers]

            legend.setAutoUpdateModel(False) #this line is important!! without it the unchecked layers
            #will be removed not only from the layout legend, but also from the table of contents panel and your project!!
            m = legend.model()
            g = m.rootGroup()
            for l in layers_to_remove:
                g.removeLayer(l)

            try:
                legend.model().setRootGroup(root)
            except Exception as e:
                self.iface.messageBar().pushMessage(
                "Error", "Ooops. Something went wrong. Trying to open the generated layout"
                )

        # # Add layout to layout manager
        layout.refresh()
        manager.addLayout(layout)

        # Open and show the layout in designer
        try:
           self.iface.openLayoutDesigner(layout)
        except Exception as e:
            self.iface.messageBar().pushMessage(
               "Error", "Ooops. Something went wrong. Trying to open the generated layout"
            )

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/templateLoader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EasyMap'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&template Loader'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = templateLoaderDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.layout_loader( "template_file_name", "layout_name", "title_text")
