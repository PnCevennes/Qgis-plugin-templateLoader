# -*- coding: utf-8 -*-
"""
/***************************************************************************
 templateLoader
                                 A QGIS plugin
 Build map from template
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-09-04
        copyright            : (C) 2019 by Parc national des Cévennes
        email                : amandine.sahl@cevennes-parcnational.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load templateLoader class from file templateLoader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .templateLoader import templateLoader
    return templateLoader(iface)
