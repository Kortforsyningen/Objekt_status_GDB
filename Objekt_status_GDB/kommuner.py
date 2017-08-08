# -*- coding: utf-8 -*-
import qgis
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import os

def kommune(str10):
    global kom_vl
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

    kom_ind = str(str10)
    for i in kommune_list:
        ii = i.decode("ascii","ignore")
        if kom_ind == ii:
            kom_vl = str(os.path.dirname(os.path.realpath(__file__)) + '\\Kom_polygons\\Kommuner_test_kom_navn_'+i+'.shp')
        else:
            pass
    return kom_vl