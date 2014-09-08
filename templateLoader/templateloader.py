# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TemplateLoader
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4 import QtXml

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from templateloaderdialog import TemplateLoaderDialog
import os.path
import time


class TemplateLoader:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'templateloader_{}.qm'.format(locale))
        
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TemplateLoaderDialog()
        self.initFormGui()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/templateloader/icon.png"),
            u"Create map", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&PnxTemplateLoader", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&PnxTemplateLoader", self.action)
        self.iface.removeToolBarIcon(self.action)

    #  
    #  name: run
    #  run method that performs all the real work
    #  @param
    #  @return
    def run(self):
      # initialize and show the dialog
      self.dlg.ui.cmbScale.removeItem(0)
      self.dlg.ui.cmbScale.insertItem(0, "1 : "+str(int(self.iface.mapCanvas().scale())),str(int(self.iface.mapCanvas().scale())))
      self.dlg.ui.cmbScale.setCurrentIndex(0)
      ## Prefill the source textbox
      self.dlg.ui.txtSource.setPlainText(u"Édition : " + self.edition + " " + QFileInfo(QgsProject.instance().fileName()).fileName() + " " + time.strftime("%d/%m/%Y"))
      self.dlg.show()
      # Run the dialog event loop
      result = self.dlg.exec_()
      # See if OK was pressed
      if result == 1:
          self.openMapComposer()
          # do something useful (delete the line containing pass and
          # substitute with your code)
          pass
    
    #  
    #  name: openMapComposer
    #  Fonction principal qui permet de lancer le map composer et de préremplir les templates avec les données du formulaire
    #  @param
    #  @return          
    def openMapComposer(self):
      try:
        # Create the composition
        canvas = self.iface.mapCanvas() 
        renderer = canvas.mapRenderer() 
        self.composition = QgsComposition(renderer)

        #Nettoyage des composeurs de façon a évité la multiplication
        for projectComposer in self.iface.activeComposers():
          if projectComposer.composerWindow().windowTitle() == 'Easy map' :
            self.iface.deleteComposer(projectComposer)
        
        composer = self.iface.createNewComposer('Easy map') 
        composer.setComposition(self.composition)
        
        #Get the template 
        preffilename = QDir.convertSeparators(QDir.cleanPath(QDir.cleanPath(self.plugin_dir + "/resources/templates/" + self.dlg.ui.cmbTemplate.itemData( self.dlg.ui.cmbTemplate.currentIndex()))))
        template_file = QFile(preffilename)
        template_file.open(QIODevice.ReadOnly | QIODevice.Text) 
        template_content = template_file.readAll() 
        template_file.close()

        document = QtXml.QDomDocument() 
        document.setContent(template_content) 
        status_load = self.composition.loadFromTemplate(document)
        
        #Mise à jour du chemin de l'image
        if type(self.composition.getComposerItemById('img-logo')) is QgsComposerPicture :
          logofile = self.preferences("logo",  False)
          ilogo = self.composition.getComposerItemById('img-logo')
          ilogo.setPictureFile(QDir.convertSeparators(QDir.cleanPath(self.plugin_dir + "/resources/logos/" + logofile[0][0])))

        #Mise a jour du titre
        if type(self.composition.getComposerItemById('main-title')) is QgsComposerLabel :
          tmaintitle = self.dlg.ui.txtmainTitle.toPlainText()
          self.composition.getComposerItemById('main-title').setText(tmaintitle)
          
        #Mise a jour du sous-titre
        if type(self.composition.getComposerItemById('sub-title')) is QgsComposerLabel :
          tsubtitle = self.dlg.ui.txtsubTitle.toPlainText()
          self.composition.getComposerItemById('sub-title').setText(tsubtitle)
          
        #Mise a jour du numéro de la carte
        if type(self.composition.getComposerItemById('num-map')) is QgsComposerLabel :
          if self.dlg.ui.iNumCarte.value() == 0 :
            self.composition.getComposerItemById('num-map').hide()
          else :
            self.composition.getComposerItemById('num-map').setText("CARTE " + str(self.dlg.ui.iNumCarte.value()))
    
        #Mise a jour de la legende
        if type(self.composition.getComposerItemById('main-map-legend')) is QgsComposerLegend :
          legend = self.composition.getComposerItemById('main-map-legend')
          legend.updateLegend()
          #Cache les rasters si le paramètre hide_raster est égale à true dans le fichier de param
          if (len(self.hideraster) > 0) and (self.hideraster[0][1] == 'true') :
            layers = QgsMapLayerRegistry.instance().mapLayers()
            for name, layer in layers.iteritems():
              if layer.type() == 1: 
                legend.model().removeLayer(name) 

              
        #Mise a jour de l'etendu de l'échelle
        if type(self.composition.getComposerItemById('main-map')) is QgsComposerMap :  
          mapcomposer = self.composition.getComposerItemById('main-map')
          box = mapcomposer.rectWithFrame()
          xy = mapcomposer.pagePos()
          mapcomposer.setNewExtent(canvas.extent())
          mapcomposer.setNewScale(float(self.dlg.ui.cmbScale.itemData( self.dlg.ui.cmbScale.currentIndex())))
          #Force la position et la taille de l'élément qui est modifiée lors de l'appel à la méthode setNewExtent
          mapcomposer.setItemPosition(xy.x() ,xy.y() , box.width(), box.height())
          mapcomposer.updateItem()
          
        #Mise a jour de la source de la données
        if type(self.composition.getComposerItemById('sources-copyright')) is QgsComposerLabel :
          model = self.dlg.ui.listViewCopyright.model()
          lcopyright = list()
          for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState() == Qt.Checked:
              lcopyright.append(item.text())
          tsource = "Sources : " + ",".join(lcopyright) 
          tsource = tsource + u"\n"+ self.dlg.ui.txtSource.toPlainText()
          self.composition.getComposerItemById('sources-copyright').setText(tsource )
          
      except:
        print "Unexpected error:"
        raise
    
    #  
    #  name: initFormGui
    #  Fonction d'initialisation de l'interface graphique => récupération des valeurs de paramètres
    #  @param
    #  @return
    def initFormGui(self):
      # Creation de la liste des valeurs pour le copyright
      model = QStandardItemModel(self.dlg.ui.listViewCopyright)
      copyrights = self.preferences("copyright",  False)
      for cpr in copyrights:
          # create an item with a caption
          item = QStandardItem(cpr[1])
          # add a checkbox to it
          item.setCheckable(True)       
          # Add the item to the model
          model.appendRow(item)
      self.dlg.ui.listViewCopyright.setModel(model)
      
      #Global vars
      self.hideraster = self.preferences("hide_raster",  False)
      e = self.preferences("edition",  False)
      self.edition = ' '
      for ed in e:
        self.edition = ed[1]

      ## Fill the combobox with available scales.
      scales = self.preferences("scale",  False)
      for scale in scales:
        self.dlg.ui.cmbScale.addItem("1 : "+scale[1], scale[1] )
      
      templates = self.preferences("template",  False)
      for template in templates:
        self.dlg.ui.cmbTemplate.addItem(template[1], template[0] )      
       
    #  name: preferences
    #  Fonction de récupération des paramètres définis dans le fichier preferences.xml
    #  @param pref (text) = nom de la variable d'intéret
    #  @return array[x][2] => liste des clés / valeurs pour la variable d'intéret
    def preferences(self,  pref,  text):
        prefs = []
        preffilename = QDir.convertSeparators(QDir.cleanPath(self.plugin_dir + "/resources/preferences.xml"))
        try:
            preffile = open(preffilename,"r")
            prefxml = preffile.read()

            doc = QtXml.QDomDocument()
            doc.setContent(prefxml,  True)  

            root = doc.documentElement()
            if root.tagName() != "preferences":
                return

            n = root.firstChild()
            while not n.isNull():
                e = n.toElement()
                sube = e.firstChild()
                while not sube.isNull():
                  if sube.toElement().tagName() == pref:
                    elvalue = unicode(sube.toElement().text())
                    elid = sube.toElement().attribute("id",  elvalue)
                    prefs.append([elid,elvalue])
                  sube = sube.nextSibling()
                n = n.nextSibling()

        except IOError:
            print "error opening preferences.xml"        
        
        return prefs
