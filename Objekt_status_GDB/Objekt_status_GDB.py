# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Objekt_status_GDB
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from shapely.geometry import MultiPolygon, Polygon, LineString, Point
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
import cx_Oracle
import ogr
# Initialize Qt resources from file resources.py
import resources
import re, os, sys, time
# Import the code for the dialog
import kommuner
from Objekt_status_GDB_dialog import Objekt_status_GDBDialog, Objekt_status_GDBDialogII
import os.path
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT


#class QProgBar(QProgressBar):
#    value = 0
#    @pyqtSlot()
#    def increaseValue(progressBar):
#        progressBar.setValue(progressBar.value)
#        progressBar.value = progressBar.value + 1

class Objekt_status_GDB:
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
            'Objekt_status_GDB_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = Objekt_status_GDBDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Objekt_status_GDB')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Objekt_status_GDB')
        self.toolbar.setObjectName(u'Objekt_status_GDB')

        self.DBname, self.DBhost, self.DBport, self.DBuser, self.DBpass = self.readSettings

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
        return QCoreApplication.translate('Objekt_status_GDB', message)

        #QObject.connect(self.dlg.comboBox_kommune, SIGNAL("currentIndexChanged(QString)" ), self.checkA )

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

        # Create the dialog (after translation) and keep reference
        self.dlg = Objekt_status_GDBDialog()
        self.dlg.pushButton_Save_dir.clicked.connect(self.showFileSelectDialogSaveDir)
        self.dlg.db_name.setText(self.DBname)
        self.dlg.db_host.setText(self.DBhost)
        self.dlg.db_port.setText(self.DBport)
        self.dlg.db_user.setText(self.DBuser)
        self.dlg.db_password.setText(self.DBpass)
        self.pgr = Objekt_status_GDBDialogII()
        # add funcionallity to pushbutton
        self.dlg.pushButton_run.clicked.connect(self.progress)

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Objekt_status_GDB/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Objekt_status_GDB'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Objekt_status_GDB'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    @property
    def readSettings(self):
        settingsFile = os.path.dirname(__file__)+"\\settings.txt"
        with open(settingsFile) as openfileobject:
            for line in openfileobject:
                SplitLine = line.split(" ")
                if SplitLine[0] == "DB_n:":
                    DBname = SplitLine[1].rstrip('\r\n')
                elif SplitLine [0] == "DB_h:":
                    DBhost = SplitLine[1].rstrip('\r\n')
                elif SplitLine [0] == "DB_po:":
                    DBport = SplitLine[1].rstrip('\r\n')
                elif SplitLine [0] == "DB_u:":
                    DBuser = SplitLine[1].rstrip('\r\n')
                elif SplitLine [0] == "DB_pa:":
                    DBpass = SplitLine[1].rstrip('\r\n')
        return (DBname,DBhost,DBport,DBuser,DBpass)

    def progress(self):
        # DB_name = "GDB_kf_read"
        DB_host = self.dlg.db_host.text()
        DB_port = self.dlg.db_port.text()
        DB_user = self.dlg.db_user.text()
        DB_pass = self.dlg.db_password.text()
        # Herunder opsttes tabellen der skal bruges. Findes tabellen ikke allerede opretts den
        DB_SID = 'geobank.prod.sitad.dk'
        DB_table = self.dlg.db_name.text()
        # Objekter i DB
        DB_list = self.DataBaseList()
        obj_list1 = ['BYGVAERK', 'BADEBAADEBRO', 'VINDMOELLE']
        obj_list2 = ['BYGNING', 'HAVN', 'SOE', 'VANDLOEBSMIDTEBRUDT']
        obj_list3 = ['JERNBANEBRUDT', 'TELEMAST', 'VEJKANT']
        DB_chk = []
        for d in DB_list:
            DB_chk.append("%s=%s" % (d, self.is_DB_alive(d)))

        rap = self.rapport(DB_chk)
        #QMessageBox.information(None, "DB status", DB_chk[0])
        QMessageBox.information(None, "DB status",rap)

        komm = self.dlg.comboBox_kommune.currentText()
        stat = self.dlg.comboBox_obj_status.currentText()
        gmtry = self.dlg.comboBox_geom_status.currentText()
        uni_str = komm.encode("ascii", "ignore")

        rs = kommuner.kommune(uni_str)
        vl = QgsVectorLayer(rs, str(uni_str), 'ogr')
        feat = vl.getFeatures()
        g = ''
        for f in feat:
            geom = f.geometry()
        if geom.wkbType() == QGis.WKBMultiPolygon:
            geometry1 = geom.asMultiPolygon()
            g = 'multi'
        elif geom.wkbType() == QGis.WKBPolygon:
            geometry1 = geom.asPolygon()
            g = 'poly'
        else:
            QMessageBox.information(None, 'Error', 'Geometry error')

        for obj in DB_list:
            try:
                self.pgr.label.setText(str(obj))
                self.pgr.show()
                self.pgr.show()
                self.completed = 0
                #time.sleep(5)
                con = cx_Oracle.connect(DB_user + '/' + DB_pass + '@' + DB_host + ':' + DB_port + '/' + DB_SID)
                cur = con.cursor()

                if stat == 'Forskellig fra \"Taget i brug\"':
                    if gmtry == 'Forskellig fra \"Endelig\"':
                        cur.execute(str(
                            'select * from ' + DB_table + "." + obj + ' where objektstatus != \'Taget i brug\'and geometristatus != \'Endelig\''))
                        columns = [i[0] for i in cur.description]
                        res = cur.fetchall()
                        cur.execute(str(
                            'select Geometri from ' + DB_table + "." + obj + ' where objektstatus != \'Taget i brug\'and geometristatus != \'Endelig\''))
                        res_geo = cur.fetchall()
                        cur.close()
                    elif gmtry == 'Endelig':
                        cur.execute(str(
                            'select * from ' + DB_table + "." + obj + ' where objektstatus != \'Taget i brug\'and geometristatus = \'Endelig\''))
                        columns = [i[0] for i in cur.description]
                        res = cur.fetchall()
                        cur.execute(str(
                            'select Geometri from ' + DB_table + "." + obj + ' where objektstatus != \'Taget i brug\'and geometristatus = \'Endelig\''))
                        res_geo = cur.fetchall()
                        cur.close()
                elif stat == 'Taget i brug':
                    if gmtry == 'Endelig':
                        cur.execute(str(
                            'select * from ' + DB_table + "." + obj + ' where objektstatus = \'Taget i brug\'and geometristatus = \'Endelig\''))
                        columns = [i[0] for i in cur.description]
                        res = cur.fetchall()
                        cur.execute(str(
                            'select Geometri from ' + DB_table + "." + obj + ' where objektstatus = \'Taget i brug\' and geometristatus = \'Endelig\''))
                        res_geo = cur.fetchall()
                        cur.close()
                    elif gmtry == 'Forskellig fra \"Endelig\"':
                        cur.execute(str(
                            'select * from ' + DB_table + "." + obj + ' where objektstatus = \'Taget i brug\'and geometristatus != \'Endelig\''))
                        columns = [i[0] for i in cur.description]
                        res = cur.fetchall()
                        cur.execute(str(
                            'select Geometri from ' + DB_table + "." + obj + ' where objektstatus = \'Taget i brug\' and geometristatus != \'Endelig\''))
                        res_geo = cur.fetchall()
                        cur.close()
                if len(res)==0:
                    self.completed=100
                    self.pgr.progressBar.setValue(self.completed)
                    self.pgr.label.setText('No objects found for object: '+str(obj))
                while self.completed < 100:
                    self.pgr.progressBar.setValue(self.completed)

                    # create vector layer
                    if obj == 'VINDMOELLE':
                        vl = QgsVectorLayer('Point?crs=epsg:25832', "Objekt_Status: " + str(obj), "memory")
                    elif obj == 'TELEMAST':
                        vl = QgsVectorLayer('Point?crs=epsg:25832', "Objekt_Status: " + str(obj), "memory")
                    else:
                        vl = QgsVectorLayer('MultiPolygon?crs=epsg:25832', "Objekt_Status polygon: " + str(obj), "memory")
                        vl1 = QgsVectorLayer('MultiLineString?crs=epsg:25832', "Objekt_Status linestring: " + str(obj),"memory")
                        pr1 = vl1.dataProvider()
                    pr = vl.dataProvider()

                    if obj == 'TEKNISKAREAL':
                        n = 0
                        # add fields
                        pr.addAttributes([QgsField("ID", QVariant.String),
                                          QgsField("Objekt_status", QVariant.String),
                                          QgsField(columns[16], QVariant.String), ])
                        # add a feature
                        for item in res:
                            n = n + 1
                            points = []
                            polybyg = res_geo[int(n - 1)][0].SDO_ORDINATES
                            Px = polybyg[::3]
                            Py = polybyg[1::3]
                            for i in range(0, len(Px)):
                                points.append(QgsPoint(Px[i], Py[i]))
                            intsect2 = Polygon(points)
                            wkt2 = str(intsect2)
                            intersect2 = ogr.CreateGeometryFromWkt(wkt2)
                            for i in range(0, len(geometry1)):
                                if g == 'multi':
                                    intsect1 = Polygon(geometry1[i][0])
                                elif g == 'poly':
                                    intsect1 = Polygon(geometry1[0])
                                wkt1 = str(intsect1)
                                intersect1 = ogr.CreateGeometryFromWkt(wkt1)
                                if intersect1.Intersects(intersect2):
                                    newfeat = QgsFeature()
                                    newfeat.setGeometry(QgsGeometry.fromWkt(wkt2))
                                    newfeat.setAttributes([n, item[12], item[16]])
                                    pr.addFeatures([newfeat])
                                else:
                                    pass
                            vl.updateExtents()
                            vl.updateFields()
                            if str(vl.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl])
                            else:
                                pass
                            self.completed = float((n * 100) / len(res))
                            self.pgr.progressBar.setValue(self.completed)
                            if int(self.completed) == 100:
                                self.pgr.close()

                    elif obj == 'VEJMIDTEBRUDT':
                        n = 0
                        # add fields
                        pr.addAttributes([QgsField("ID", QVariant.String),
                                          QgsField("Objekt_status", QVariant.String),
                                          QgsField("Vejmidte_type", QVariant.String),
                                          QgsField("Kommunekode", QVariant.String),
                                          QgsField("Vejkode", QVariant.String)])
                        pr1.addAttributes([QgsField("ID", QVariant.String),
                                           QgsField("Objekt_status", QVariant.String),
                                           QgsField("Vejmidte_type", QVariant.String),
                                           QgsField("Kommunekode", QVariant.String),
                                           QgsField("Vejkode", QVariant.String)])
                        # add a feature
                        for item in res:
                            n = n + 1
                            points = []
                            polybyg = res_geo[int(n - 1)][0].SDO_ORDINATES
                            Px = polybyg[::3]
                            Py = polybyg[1::3]
                            for i in range(0, len(Px)):
                                points.append(QgsPoint(Px[i], Py[i]))
                            if len(points) == 2:
                                intsect2 = LineString(points)
                                vlyr = 'LineString'
                            elif len(points) == 1:
                                intsect2 = Point(points[0])
                                vlyr = 'Point'
                            else:
                                intsect2 = Polygon(points)
                                vlyr = 'Polygon'
                            wkt2 = str(intsect2)
                            intersect2 = ogr.CreateGeometryFromWkt(wkt2)

                            for i in range(0, len(geometry1)):
                                if g == 'multi':
                                    intsect1 = Polygon(geometry1[i][0])
                                elif g == 'poly':
                                    intsect1 = Polygon(geometry1[0])
                                wkt1 = str(intsect1)
                                intersect1 = ogr.CreateGeometryFromWkt(wkt1)
                                if intersect1.Intersects(intersect2):
                                    poly = QgsFeature()
                                    poly.setGeometry(QgsGeometry.fromWkt(wkt2))
                                    poly.setAttributes([n, item[12], item[21], item[16], item[17]])
                                    if vlyr == 'LineString':
                                        pr1.addFeatures([poly])
                                    else:
                                        pr.addFeatures([poly])
                                else:
                                    pass
                            vl.updateExtents()
                            vl.updateFields()
                            vl1.updateExtents()
                            vl1.updateFields()
                            if str(vl.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl])
                            else:
                                pass
                            if str(vl1.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl1])
                            else:
                                pass
                            self.completed = float((n * 100) / len(res))
                            self.pgr.progressBar.setValue(self.completed)
                            if int(self.completed) == 100:
                                self.pgr.close()

                    elif obj in obj_list3:
                        n = 0
                        for item in res:
                            # add fields
                            pr.addAttributes([QgsField("ID", QVariant.String),
                                              QgsField("Objekt_status", QVariant.String),
                                              QgsField(columns[18], QVariant.String), ])
                            if obj != "TELEMAST":
                                # add fields
                                pr1.addAttributes([QgsField("ID", QVariant.String),
                                                   QgsField("Objekt_status", QVariant.String),
                                                   QgsField(columns[18], QVariant.String), ])
                            n = n + 1
                            points = []
                            polybyg = res_geo[int(n - 1)][0].SDO_ORDINATES
                            Px = polybyg[::3]
                            Py = polybyg[1::3]
                            for i in range(0, len(Px)):
                                points.append(QgsPoint(Px[i], Py[i]))
                            if len(points) == 2:
                                intsect2 = LineString(points)
                                vlyr = 'LineString'
                            elif len(points) == 1:
                                intsect2 = Point(points[0])
                                vlyr = 'Point'
                            else:
                                intsect2 = Polygon(points)
                                vlyr = 'Polygon'

                            wkt2 = str(intsect2)
                            intersect2 = ogr.CreateGeometryFromWkt(wkt2)
                            for i in range(0, len(geometry1)):
                                if g == 'multi':
                                    intsect1 = Polygon(geometry1[i][0])
                                elif g == 'poly':
                                    intsect1 = Polygon(geometry1[0])
                                wkt1 = str(intsect1)
                                intersect1 = ogr.CreateGeometryFromWkt(wkt1)

                                if intersect1.Intersects(intersect2):
                                    poly = QgsFeature()
                                    poly.setAttributes([n, item[12], item[18]])
                                    poly.setGeometry(QgsGeometry.fromWkt(wkt2))
                                    if vlyr == 'LineString':
                                        pr1.addFeatures([poly])
                                    else:
                                        pr.addFeatures([poly])
                            vl.updateExtents()
                            vl.updateFields()
                            if str(vl.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl])
                            else:
                                pass
                            if obj != "TELEMAST":
                                vl1.updateExtents()
                                vl1.updateFields()
                                if str(vl1.featureCount()) != '0':
                                    QgsMapLayerRegistry.instance().addMapLayers([vl1])
                                else:
                                    pass
                            self.completed = float((n * 100) / len(res))
                            self.pgr.progressBar.setValue(self.completed)
                            if int(self.completed) == 100:
                                self.pgr.close()

                    elif obj in obj_list2:
                        n = 0
                        # add fields
                        pr.addAttributes([QgsField("ID", QVariant.String),
                                          QgsField("Objekt_status", QVariant.String),
                                          QgsField(columns[17], QVariant.String), ])
                        pr1.addAttributes([QgsField("ID", QVariant.String),
                                           QgsField("Objekt_status", QVariant.String),
                                           QgsField(columns[17], QVariant.String), ])

                        for item in res:
                            n = n + 1
                            points = []
                            polybyg = res_geo[int(n - 1)][0].SDO_ORDINATES
                            Px = polybyg[::3]
                            Py = polybyg[1::3]
                            for i in range(0, len(Px)):
                                points.append(QgsPoint(Px[i], Py[i]))
                            if len(points) == 2:
                                intsect2 = LineString(points)
                                vlyr = 'LineString'
                            elif len(points) == 1:
                                intsect2 = Point(points[0])
                                vlyr = 'Point'
                            else:
                                intsect2 = Polygon(points)
                                vlyr = 'Polygon'

                            wkt2 = str(intsect2)
                            intersect2 = ogr.CreateGeometryFromWkt(wkt2)
                            for i in range(0, len(geometry1)):
                                if g == 'multi':
                                    intsect1 = Polygon(geometry1[i][0])
                                    wkt1 = str(intsect1)
                                    wkt11 = str(intsect1)
                                    intersect1 = ogr.CreateGeometryFromWkt(wkt1)
                                    intersect3 = ogr.CreateGeometryFromWkt(wkt11)
                                    intersect4 = intersect3.Buffer(500)
                                elif g == 'poly':
                                    intsect1 = Polygon(geometry1[0])
                                    wkt1 = str(intsect1)
                                    wkt11 = str(intsect1)
                                    intersect1 = ogr.CreateGeometryFromWkt(wkt1)
                                    intersect3 = ogr.CreateGeometryFromWkt(wkt11)
                                    intersect4 = intersect3.Buffer(500)

                                if intersect1.Intersects(intersect2):
                                    poly = QgsFeature()
                                    poly.setAttributes([n, item[12], item[17]])
                                    poly.setGeometry(QgsGeometry.fromWkt(str(wkt2)))
                                    if vlyr == 'LineString':
                                        pr1.addFeatures([poly])
                                    else:
                                        pr.addFeatures([poly])
                            if obj == 'HAVN':
                                if intersect4.Intersects(intersect2):
                                    poly = QgsFeature()
                                    poly.setAttributes([n, item[12], item[17]])
                                    poly.setGeometry(QgsGeometry.fromWkt(str(wkt2)))
                                    pr.addFeatures([poly])

                            vl.updateExtents()
                            vl.updateFields()
                            vl1.updateExtents()
                            vl1.updateFields()
                            if str(vl.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl])
                            else:
                                pass
                            if str(vl1.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl1])
                            else:
                                pass
                            self.completed = float((n * 100) / len(res))
                            self.pgr.progressBar.setValue(self.completed)
                            if int(self.completed) == 100:
                                self.pgr.close()

                    elif obj in obj_list1:
                        n = 0
                        # add fields
                        pr.addAttributes([QgsField("ID", QVariant.String),
                                          QgsField("Objekt_status", QVariant.String), ])
                        if obj != "VINDMOELLE":
                            # add fields
                            pr1.addAttributes([QgsField("ID", QVariant.String),
                                               QgsField("Objekt_status", QVariant.String),
                                               QgsField(columns[18], QVariant.String), ])
                        for item in res:
                            n = n + 1
                            points = []
                            polybyg = res_geo[int(n - 1)][0].SDO_ORDINATES
                            Px = polybyg[::3]
                            Py = polybyg[1::3]
                            for i in range(0, len(Px)):
                                points.append(QgsPoint(Px[i], Py[i]))
                            if len(points) == 2:
                                intsect2 = LineString(points)
                                vlyr = 'LineString'
                            elif len(points) == 1:
                                intsect2 = Point(points[0])
                                vlyr = 'Point'
                            else:
                                intsect2 = Polygon(points)
                                vlyr = 'Polygon'

                            wkt2 = str(intsect2)
                            intersect2 = ogr.CreateGeometryFromWkt(wkt2)
                            for i in range(0, len(geometry1)):
                                if g == 'multi':
                                    intsect1 = Polygon(geometry1[i][0])
                                elif g == 'poly':
                                    intsect1 = Polygon(geometry1[0])
                                wkt1 = str(intsect1)
                                intersect1 = ogr.CreateGeometryFromWkt(wkt1)

                                if intersect1.Intersects(intersect2):
                                    poly = QgsFeature()
                                    poly.setAttributes([n, item[12]])
                                    poly.setGeometry(QgsGeometry.fromWkt(wkt2))
                                    if vlyr == 'LineString':
                                        pr1.addFeatures([poly])
                                    else:
                                        pr.addFeatures([poly])
                            vl.updateExtents()
                            vl.updateFields()
                            if str(vl.featureCount()) != '0':
                                QgsMapLayerRegistry.instance().addMapLayers([vl])
                            else:
                                pass
                            if obj != "VINDMOELLE":
                                vl1.updateExtents()
                                vl1.updateFields()
                                if str(vl1.featureCount()) != '0':
                                    QgsMapLayerRegistry.instance().addMapLayers([vl1])
                                else:
                                    pass
                            self.completed = float((n * 100) / len(res))
                            self.pgr.progressBar.setValue(self.completed)
                            if int(self.completed) == 100:
                                self.pgr.close()

            except Exception, e:  # (RuntimeError, TypeError, NameError, ValueError):
                QMessageBox.information(None, 'Error', str(e))  #  "fail"

            try:
                if str(vl1.featureCount()) != '0':
                    if str(vl.featureCount()) != '0':
                        _writer = QgsVectorFileWriter.writeAsVectorFormat(vl, str(
                            self.dlg.lineEdit_Save_dir.text()) + '\\' + 'FOR_poly_' + obj + ".shp", "utf-8", None,
                                                                          "ESRI Shapefile")
                        _writer = QgsVectorFileWriter.writeAsVectorFormat(vl1, str(
                            self.dlg.lineEdit_Save_dir.text()) + '\\' + 'FOR_line_' + obj + ".shp", "utf-8", None,
                                                                          "ESRI Shapefile")
                    elif str(vl.featureCount()) == '0':
                        if obj == "VINDMOELLE":
                            pass
                        else:
                            _writer = QgsVectorFileWriter.writeAsVectorFormat(vl1, str(
                                self.dlg.lineEdit_Save_dir.text()) + '\\' + 'FOR_line_' + obj + ".shp", "utf-8", None,
                                                                              "ESRI Shapefile")
                elif str(vl1.featureCount()) == '0':
                    if str(vl.featureCount()) != '0':
                        _writer = QgsVectorFileWriter.writeAsVectorFormat(vl, str(
                            self.dlg.lineEdit_Save_dir.text()) + '\\' + 'FOR_' + obj + ".shp", "utf-8", None,
                                                                          "ESRI Shapefile")
                    else:
                        pass
                else:
                    pass
            except Exception:
                pass
                #if str(vl.featureCount()) == '0':
                #    _writer = QgsVectorFileWriter.writeAsVectorFormat(vl, str(
                #        self.dlg.lineEdit_Save_dir.text()) + '\\' + 'FOR_' + obj + ".shp", "utf-8", None,
                #                                                      "ESRI Shapefile")
        #cur.close
        #con.close()

    def showFileSelectDialogSaveDir(self):
        fname = QFileDialog.getExistingDirectory( None, 'Open directory', os.path.dirname(__file__))
        self.dlg.lineEdit_Save_dir.setText(fname)

    def DataBaseList(self):
        DB_l = []
        if self.dlg.checkBox_1.isChecked():
            DB_l.append('BYGNING')
        if self.dlg.checkBox_2.isChecked():
            DB_l.append('BYGVAERK')
        if self.dlg.checkBox_3.isChecked():
            DB_l.append('BAADEBAADEBRO')
        if self.dlg.checkBox_4.isChecked():
            DB_l.append('HAVN')
        if self.dlg.checkBox_5.isChecked():
            DB_l.append('JERNBANEBRUDT')
        if self.dlg.checkBox_6.isChecked():
            DB_l.append('SOE')
        if self.dlg.checkBox_7.isChecked():
            DB_l.append('TEKNISKAREAL')
        if self.dlg.checkBox_8.isChecked():
            DB_l.append('TELEMAST')
        if self.dlg.checkBox_9.isChecked():
            DB_l.append('VANDLOEBSMIDTEBRUDT')
        if self.dlg.checkBox_10.isChecked():
            DB_l.append('VEJKANT')
        if self.dlg.checkBox_11.isChecked():
            DB_l.append('VEJMIDTEBRUDT')
        if self.dlg.checkBox_12.isChecked():
            DB_l.append('VINDMOELLE')
        return DB_l

    def rapport(self,DB_chk):
        tt=len(DB_chk)
        if tt==0:
            rap = 'No DataBase chosen!'
        elif tt==1:
            rap = DB_chk[0]
        elif tt==2:
            rap = DB_chk[0] + '\n' + DB_chk[1]
        elif tt==3:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2]
        elif tt==4:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3]
        elif tt==5:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4]
        elif tt==6:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5]
        elif tt==7:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6]
        elif tt==8:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6] + '\n' + DB_chk[7]
        elif tt==9:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6] + '\n' + DB_chk[7] + '\n' + DB_chk[8]
        elif tt==10:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6] + '\n' + DB_chk[7] + '\n' + DB_chk[8] + '\n' + DB_chk[9]
        elif tt==11:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6] + '\n' + DB_chk[7] + '\n' + DB_chk[8] + '\n' + DB_chk[9] + '\n' + DB_chk[10]
        elif tt==12:
            rap = DB_chk[0] + '\n' + DB_chk[1] + '\n' + DB_chk[2] + '\n' + DB_chk[3] + '\n' + DB_chk[4] + '\n' + DB_chk[5] + '\n' + DB_chk[6] + '\n' + DB_chk[7] + '\n' + DB_chk[8] + '\n' + DB_chk[9] + '\n' + DB_chk[10] + '\n' + DB_chk[11]
        return rap

    def is_DB_alive(self, db_name):
        # DB_name = "GDB_kf_read"
        DB_host = self.dlg.db_host.text()
        DB_port = self.dlg.db_port.text()
        DB_user = self.dlg.db_user.text()
        DB_pass = self.dlg.db_password.text()
        # Herunder opsttes tabellen der skal bruges. Findes tabellen ikke allerede opretts den
        DB_SID = 'geobank.prod.sitad.dk'
        DB_table = self.dlg.db_name.text()
        is_alive = 'False'
        try:
            con = cx_Oracle.connect(DB_user + '/' + DB_pass + '@' + DB_host + ':' + DB_port + '/' + DB_SID)
            cur = con.cursor()
            cur.execute('select * from ' + DB_table + "." + db_name)
        except:
            is_alive = 'Failed to connect to table'
        else:
            is_alive = 'Working'
        return is_alive

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        # Liste med DK kommuner  fra DAGI kommuneindeling
        kommune_list = ['Hele_DK','Albertslund', 'Aller\xf8d', 'Assens', 'Ballerup', 'Billund', 'Bornholm', 'Br\xf8ndby', 'Br\xf8nderslev',
                        'Christians\xf8', 'Drag\xf8r', 'Egedal', 'Esbjerg', 'Fan\xf8', 'Favrskov', 'Faxe', 'Fredensborg', 'Fredericia', 'Frederiksberg',
                        'Frederikshavn', 'Frederikssund', 'Fures\xf8', 'Faaborg-Midtfyn', 'Gentofte', 'Gladsaxe', 'Glostrup', 'Greve', 'Gribskov',
                        'Guldborgsund', 'Haderslev', 'Halsn\xe6s', 'Hedensted', 'Helsing\xf8r', 'Herlev', 'Herning', 'Hiller\xf8d', 'Hj\xf8rring',
                        'Holb\xe6k', 'Holstebro', 'Horsens', 'Hvidovre', 'H\xf8je Taastrup', 'H\xf8rsholm', 'Ikast-Brande', 'Ish\xf8j', 'Jammerbugt',
                        'Kalundborg', 'Kerteminde', 'Kolding', 'K\xf8benhavn', 'K\xf8ge', 'Langeland', 'Lejre', 'Lemvig', 'Lolland',
                        'Lyngby-Taarb\xe6k', 'L\xe6s\xf8', 'Mariagerfjord', 'Middelfart', 'Mors\xf8', 'Norddjurs', 'Nordfyns', 'Nyborg',
                        'N\xe6stved', 'Odder', 'Odense', 'Odsherred', 'Randers', 'Rebild', 'Ringk\xf8bing-Skjern', 'Ringsted', 'Roskilde',
                        'Rudersdal', 'R\xf8dovre', 'Sams\xf8', 'Silkeborg', 'Skanderborg', 'Skive', 'Slagelse', 'Solr\xf8d', 'Sor\xf8', 'Stevns',
                        'Struer', 'Svendborg', 'Syddjurs', 'S\xf8nderborg', 'Thisted', 'T\xf8nder', 'T\xe5rnby', 'Vallensb\xe6k', 'Varde', 'Vejen',
                        'Vejle', 'Vesthimmerlands', 'Viborg', 'Vordingborg', '\xc6r\xf8', 'Aabenraa', 'Aalborg', 'Aarhus']
        self.dlg.comboBox_kommune.clear()
        self.dlg.comboBox_kommune.addItems(kommune_list)
        obj_sts = ['Forskellig fra \"Taget i brug\"','Taget i brug']
        self.dlg.comboBox_obj_status.clear()
        self.dlg.comboBox_obj_status.addItems(obj_sts)
        geom_sts = ['Forskellig fra \"Endelig\"', 'Endelig']
        self.dlg.comboBox_geom_status.clear()
        self.dlg.comboBox_geom_status.addItems(geom_sts)
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            pass

