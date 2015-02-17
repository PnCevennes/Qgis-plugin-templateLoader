![alt text](https://raw.githubusercontent.com/PnCevennes/Qgis-plugin-templateLoader/master/templateLoader/icon.png "Logo") Qgis-plugin-templateLoader
======================

Extension python permettant de générer un composer de carte à partir de templates prédéfinies.


![alt text](https://raw.githubusercontent.com/PnCevennes/Qgis-plugin-templateLoader/master/docs/images/main_windows_dialog.png "Fenetre principal du plugin")


Configuration
-------------------

Les paramètres du plugins sont contenus dans le fichier preferences.xml (répertoire resources).
Ils permettent de spécifier : 
 - La listes des échelles possible pour la carte

  ````XML
  <scales>
    <scale>2000</scale>
      ..
    <scale>300000</scale>
    <scale>500000</scale>
    <scale>1000000</scale>
  </scales>
  ````
 - La liste des templates accéssibles à l'utilisateur.

  ````XML
  <templates>
    <template id="nom_du_fichier.qpt">Nom à afficher</template>
    ....
  </templates>
  ````
 - La liste des checkboxs permettant d'ajouter des copyrights prédéfinis

  ````XML
  <copyrights>
    <copyright>© IGN SCAN25 2012</copyright>
      ...
  </copyrights> 
  ````
 - Un texte s'affichant par défaut dans la source (en plus du nom du projet et de la date de création de la carte)

  ````XML
  <editions>
    <edition>I love Maps</edition>    
  </editions>
  ````
 - Le nom du fichier logo à afficher

  ````XML
  <logos>
    <logo>logo_pnc_orange.tif</logo>
  </logos>
  ````
 - Un paramètre permettant de spécifier si la légende des fichiers raster doit ou non figurer sur la carte

  ````XML
  <params>
    <hide_raster>true</hide_raster>
  </params>
  ````
 


Création de template
-------------------

Pour que le plugin fonctionne correctement les templates doivent respecter des conventions. Les éléments du template doivent avoir les ids suivants : 
 - Carte = main-map
 - Légende = main-map-legend
 - Logo = img-logo
 - Titre = main-title
 - Sous-titre = sub-title
 - Source = sources-copyright
 - Numéro de la carte = num-map

