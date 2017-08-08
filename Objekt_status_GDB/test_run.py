import kommuner
#from Objekt_status_GDB import *
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from shapely.geometry import Polygon
#from PyQt4.QtGui import *
#from PyQt4.QtCore import *
#from qgis.core import *
#import cx_Oracle
# Initialize Qt resources from file resources.py
#import resources
#import re, os
# Import the code for the dialog
#from Objekt_status_GDB_dialog import Objekt_status_GDBDialog
#import os.path
#global geom

rs = kommuner.kommune('Rudersdal')

vl = QgsVectorLayer(rs,'Rudersdal','ogr')
feat = vl.getFeatures()
for f in feat:
    geom = f.geometry()
geometry1 = geom.asPolygon()
intsect1 = Polygon(geometry1[0])
print intsect1
