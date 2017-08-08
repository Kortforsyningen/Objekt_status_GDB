# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Objekt_status_GDB
                                 A QGIS plugin
 find GDB objects
                             -------------------
        begin                : 2017-06-13
        copyright            : (C) 2017 by Mafa/sdfe
        email                : mafal@sdfe.dk
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
    """Load Objekt_status_GDB class from file Objekt_status_GDB.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Objekt_status_GDB import Objekt_status_GDB
    return Objekt_status_GDB(iface)
