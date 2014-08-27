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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load TemplateLoader class from file TemplateLoader
    from templateloader import TemplateLoader
    return TemplateLoader(iface)
