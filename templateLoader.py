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
import json

from distutils.dir_util import copy_tree

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAction
from PyQt5.QtXml import QDomDocument

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutItemLegend
)

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
        self.menu = self.tr("Créer une carte")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.add_profile_data()
        self.preferences = self.load_preferences()

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
        return QCoreApplication.translate('TemplateLoader', message)

    def add_profile_data(self):
        """
            Add templates and resources from plugin to user profile
        """
        # Paths to source files and qgis profile directory
        source_profile = os.path.join(self.plugin_dir, 'profile')
        profile_home = QgsApplication.qgisSettingsDirPath()

        copy_tree(source_profile, profile_home, update=1)

    def load_preferences(self):
        """
            Load preference file who are contain in resources dir
        """
        path = os.path.join(self.plugin_dir, "resources", "preferences.json")
        with open(path, 'r') as json_prefs:
            prefs = json.load(json_prefs)
        return prefs

    def layout_loader(self):
        """
            Generate the layout with form parameters
        """

        layout_name = 'Custom Map'

        # get ui results
        title_text = self.dlg.txtmainTitle.text()
        sub_title = self.dlg.txtsubTitle.text()
        template_file_name = self.dlg.cmbTemplate.currentText()
        num_carte = self.dlg.iNumCarte.value()

        scale = self.dlg.cmbScale.itemData(self.dlg.cmbScale.currentIndex())

        model = self.dlg.listViewCopyright.model()
        lcopyright = list()
        for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState():
                lcopyright.append(item.text())

        project = QgsProject.instance()
        manager = project.layoutManager()

        # test if layout already exists and remove it
        existing_layout = manager.layoutByName(layout_name)
        if existing_layout:
            manager.removeLayout(existing_layout)

        layout = QgsPrintLayout(project)

        layout.initializeDefaults()

        # Load template file and load it into the layout (l)
        tpl_path = os.path.join(
            QgsApplication.qgisSettingsDirPath(),
            "composer_templates",
            template_file_name + ".qpt"
        )
        template_file = open(
            tpl_path,
            'r+',
            encoding='utf-8'
        )
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)
        layout.loadFromTemplate(document, QgsReadWriteContext())

        # Give the layout a name (must be unique)
        layout.setName(layout_name)

        # Extent of current canvas
        if isinstance(layout.itemById('main-map'), QgsLayoutItemMap):
            my_map = layout.itemById('main-map')
            # canvas = self.iface.mapCanvas()
            # my_map.setExtent(canvas.extent())

            # Scale
            my_map.setScale(int(scale))

        # Change title QgsLayoutItemLabel
        if isinstance(
            layout.itemById('main-title'),
            QgsLayoutItemLabel
        ):
            item = layout.itemById('main-title')
            item.setText(title_text)

        if isinstance(
            layout.itemById('sub-title'),
            QgsLayoutItemLabel
        ):
            item = layout.itemById('sub-title')
            item.setText(sub_title)

        if isinstance(
            layout.itemById('num-map'),
            QgsLayoutItemLabel
        ):
            item = layout.itemById('num-map')
            item.setText(item.text().replace('{{num}}', str(num_carte)))

        if isinstance(
            layout.itemById('sources-copyright'),
            QgsLayoutItemLabel
        ):
            item = layout.itemById('sources-copyright')
            item.setText(
                item.text().replace(
                    '{{copyright}}', ",".join(lcopyright)
                )
            )

        ## Legend
        if isinstance(
            layout.itemById('main-map-legend'
        ),
            QgsLayoutItemLegend):
            legend = layout.itemById('main-map-legend')
            legend.setTitle("Légende")

            # Add only active layers
            # Checks layer tree objects and stores them in a list.
            #    This includes csv tables
            checked_layers = [
                layer.name() for layer in project.layerTreeRoot().children()
                if layer.isVisible()
            ]
            # get map layer objects of checked layers
            #   by matching their names and store those in a list
            layers_to_remove = [
                layer for layer in project.mapLayers().values()
                if layer.name() not in checked_layers
            ]

            # this line is important!!
            # without it the unchecked layers
            # will be removed not only from the layout legend,
            # but also from the table of contents panel and your project!!
            legend.setAutoUpdateModel(False)

            model = legend.model()
            root = model.rootGroup()
            for l in layers_to_remove:
                root.removeLayer(l)

            try:
                model.setRootGroup(root)
            except:
                self.iface.messageBar().pushMessage(
                    "Error",
                    "Ooops. Something went wrong. Trying to set the legend"
                )

        # # Add layout to layout manager
        layout.refresh()
        manager.addLayout(layout)

        # Open and show the layout in designer
        try:
            self.iface.openLayoutDesigner(layout)
        except Exception:
            self.iface.messageBar().pushMessage(
               "Error",
               "Ooops. Something went wrong. Trying to open the generated layout"
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
        parent=None
    ):
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
        """
            Create the menu entries and toolbar
                icons inside the QGIS GUI.
        """

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

    def loadTemplates(self):
        """
            Load template file that are contains in
            the composer_templates dir
        """
        profile_dir = QgsApplication.qgisSettingsDirPath()
        templates_dir = os.path.join(profile_dir, 'composer_templates')

        # Does the composer_templates folder exist? Otherwise create it.
        if os.path.isdir(templates_dir) == False:
            os.mkdir(templates_dir)

        # Search the templates folder
        #   and add files to templates list and sort it
        templates = [
            f.name for f in os.scandir(templates_dir) if f.is_file()
        ]
        templates.sort()

        # Add all the templates from the list to the listWidget
        #   (only add files with *.qpt extension)
        tpls = []
        for template in templates:
            filename, extension = os.path.splitext(template)
            if extension == '.qpt':
                tpls.append(filename)
        return tpls

    def initFormGui(self):
        """
            name: initFormGui
            Fonction d'initialisation de l'interface graphique
                => récupération des valeurs de paramètres
            @param
            @return
        """
        # Creation de la liste des valeurs pour le copyright
        model = QStandardItemModel(self.dlg.listViewCopyright)
        copyrights = self.preferences["copyrights"]
        for cpr in copyrights:
            # create an item with a caption
            item = QStandardItem(cpr)
            # add a checkbox to it
            item.setCheckable(True)
            # Add the item to the model
            model.appendRow(item)
        self.dlg.listViewCopyright.setModel(model)

        # Fill the combobox with available scales.
        self.dlg.cmbScale.addItem(
            "1 : " + str(int(self.iface.mapCanvas().scale())),
            int(self.iface.mapCanvas().scale())
        )
        scales = self.preferences["scales"]
        for scale in scales:
            self.dlg.cmbScale.addItem("1 : " + str(scale), scale)

        self.dlg.cmbScale.setCurrentIndex(0)

        # Load template
        templates = self.loadTemplates()
        self.dlg.cmbTemplate.clear()
        for template in templates:
            self.dlg.cmbTemplate.addItem(template)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation)
        #       and keep reference
        # Only create GUI ONCE in callback,
        #       so that it will only load when the plugin is started
        if self.first_start is True:
            self.first_start = False
            self.dlg = templateLoaderDialog()
            self.initFormGui()

        # Fill the combobox with the current scale
        self.dlg.cmbScale.removeItem(0)
        self.dlg.cmbScale.insertItem(
            0,
            "1 : " + str(int(self.iface.mapCanvas().scale())),
            int(self.iface.mapCanvas().scale())
        )
        self.dlg.cmbScale.setCurrentIndex(0)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Run layout loader
            self.layout_loader()
