![alt text](https://raw.githubusercontent.com/PnCevennes/Qgis-plugin-templateLoader/master/templateLoader/icon.png "Logo") Qgis-plugin-templateLoader
======================

Extension python permettant de générer un composer de carte à partir de templates prédéfinis.


![alt text](https://raw.githubusercontent.com/PnCevennes/Qgis-plugin-templateLoader/master/docs/images/main_windows_dialog.png "Fenetre principal du plugin")

Versions Qgis
-------------------
Plugin testé avec Qgis 3.4



Fonctionnement du plugin
-------------------------
Le plugin récupère les templates contenus dans le dossier `composer_templates` du profil de l'utilisateur. Puis se base sur les identifiant des blocks des templates pour remplir les informations contenues dans le formulaire.


Un ensemble de templates et icone sont initialement présentes dans le répertoire profile. Ce répertoire est copié lors de l'installation du plugin dans le profil de l'utilisateur dans les répertoires standards de Qgis:
* composer_templates
* svg


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

Une fois un template créé, il faut l'enregistrer dans le dossier `composer_templates` du profil de l'utilisateur.
Pour rajouter des icones, il est également conseillé de les placer dans le répertoire `svg` du profil de l'utilisateur

Configuration
-------------------
Les paramètres du plugins sont contenus dans le fichier preferences.json (répertoire resources).
Ils permettent de spécifier : 
 - La liste des échelles possibles pour la carte

  ````json
 "scales": [
            100,
            250,
            500,
            1000,
            2000,
            5000,
            10000,
            25000,
            50000,
            100000,
            200000,
            300000,
            500000,
            1000000
    ],
  ````
 - La liste des checkboxs permettant d'ajouter des copyrights prédéfinis

  ````json
  "copyrights": [
        "IGN SCAN25®",
        "IGN BD ORTHO®",
        "IGN BD ORTHO®",
        "© OpenStreetMap contributors"
    ]
  
  ````

