# -*- coding: utf-8 -*-
"""
uebertragung.py   v0.4 (2020-09)
"""

# Copyright 2020 Dominik Zobel.
# All rights reserved.
#
# This file is part of the abapys library.
# abapys is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# abapys is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with abapys. If not, see <http://www.gnu.org/licenses/>.


# -------------------------------------------------------------------------------------------------
class FieldOutputValue(object):
   """Mini-Klasse zur Erstellung von FieldOutputValues.
   """
   def __init__(self, precision, data=None, dataDouble=None, type=None, elementLabel=None,
      nodeLabel=None):
      self.data = data;
      self.dataDouble = dataDouble;
      self.elementLabel = elementLabel;
      self.nodeLabel = nodeLabel;
      self.precision = precision;
      self.type = type;
   def __repr__(self):
      return 'FieldOutputValue (abapys)';
#


# -------------------------------------------------------------------------------------------------
def _ErzeugeAbapysAnfangsbedingungenEintrag(modell):
   """Erzeuge in den Keywordeintraegen des uebergebenen Modells modell einen Block mit den
   Anfangsbedingungen durch abapys (falls er nicht schon vorhanden ist). Falls noch kein abapys-
   Block vorhanden ist, fuege ihn vor dem ersten Step ein (oder am Ende, falls noch kein Step
   existiert). Gibt den Index nach dem letzten Eintrag zurueck, um weitere
   Anfangsbedingungen an der richtigen Stelle einfuegen zu koennen.
   """
   idx_abapys = -1;
   modell.keywordBlock.synchVersions(storeNodesAndElements=False);
   for idx, text in enumerate(modell.keywordBlock.sieBlocks):
      if (text == '** Initial conditions added with abapys'):
         idx_abapys = idx;
         break;
      #
      if ('** STEP' in text):
         idx_abapys = idx - 1;
         modell.keywordBlock.insert(idx_abapys, '** Initial conditions added with abapys');
         break;
   #
   if (idx_abapys == -1):
      idx_abapys = len(modell.keywordBlock.sieBlocks)-1;
      modell.keywordBlock.insert(idx_abapys, '** Initial conditions added with abapys');
   #
   return idx_abapys+1;
#


# -------------------------------------------------------------------------------------------------
def KonstanteAnfangsloesungFuerSet(modell, instname, setname, ausgabewerte):
   """Erstelle einen Initial Condition Solution Eintrag im Keyword Block des Modells namens mdbname.
   In diesem Block werden allen Elementen aus dem Set setname des Instanz instname die uebergebenen
   Werte ausgabewerte als Anfangsloesung zugewiesen. Im Keyword Block wird dazu ein Verweis auf eine
   Datei <mdbname>_sdv_init.add verwiesen, die angelegt und mit den Werten beschrieben wird.
   """
   from hilfen import BlockAusgabe
   #
   laenge_ausgabewerte = len(ausgabewerte);
   #
   ausgabedatei = modell.name + '_sdv_init_' + setname.lower().replace('_', '-').replace('.', '') \
      + '.add';
   ausgabetext = '*Initial Conditions, type=SOLUTION, input=' + ausgabedatei;
   #
   elements = modell.rootAssembly.instances[instname].sets[setname].elements;
   with open(ausgabedatei, 'w') as ausgabe:
      for elem in elements:
         temp_ergebnis = [instname + '.' + str(elem.label)] + list(ausgabewerte);
         ausgabe.write(BlockAusgabe(temp_ergebnis));
   #
   idx_naechstereintrag = _ErzeugeAbapysAnfangsbedingungenEintrag(modell=modell);
   modell.keywordBlock.insert(idx_naechstereintrag, ausgabetext);
#


# --------------------------------------------------------------------------------------------------
def ZielwertquaderErstellen(dateiname, xwerte, ywerte, zwerte, ergebnisfunktion):
   """Erstelle eine Ausgabedatei namens dateiname mit Ausgabegroessen fuer alle uebergebenen Werte.
   Dabei werden xwerte, ywerte und zwerte Listen mit streng monoton zunehmende oder abnehmende
   Punktkoordinaten erwartet. Fuer jede Kombination von Koordinaten aus den drei Vektoren wird mit
   der uebergebenen ergebnisfunktion eine Ausgabe berechnet.
   
   ergebnisfunktion kann eine beliebige Funktion sein, die jedoch ein Argument punktkoordinaten als
   Liste mit drei Eintraegen akzeptieren und eine Liste zurueckgeben muss
   
   Jede Kombination von Punktkoordinaten und deren Rueckgabewerte von ergebnisfunktion werden in
   eine Zeile der Ausgabedatei geschrieben.
   """
   with open(dateiname, 'w', encoding='utf-8') as ausgabe:
      for zKoord in zwerte:
         for yKoord in ywerte:
            for xKoord in xwerte:
               auswertung = ergebnisfunktion(punktkoordinaten=(xKoord, yKoord, zKoord));
               ausgabe.write(', '.join([str(wert) for wert in [xKoord, yKoord, zKoord] + auswertung]) + '\n');
#


# -------------------------------------------------------------------------------------------------
def _ZielwertquaderKnotenEinlesen(dateiname, numKoordinaten, numVar):
   """Liest aus einer csv-Datei namens dateiname alle Zeilen ein. In jeder Zeile werden
   numKoordinaten Eintraege als Koordinaten erwartet (d.h. 2 oder 3) und die restlichen Werte werden
   als Ergebnisse an diesen Koordinaten betrachtet. Mit 2 Koordinaten werden Elemente aus vier
   Knoten angenommen, mit 3 Koordinaten aus acht.
   Die Koordinaten stehen fuer die Knotenkoordinaten und die Ergebnisse sind an den
   Knotenkoordinaten definiert.
   """
   from hilfen import Log
   import csv
   #
   tol = 1e-6;
   reihenfolge = [];
   numwerte = [];
   punkte = [];
   werte = [];
   with open(dateiname, 'r') as eingabe:
      eingelesen = csv.reader(eingabe, delimiter=',');
      for idx_zeile, zeile in enumerate(eingelesen):
         punkte += [[float(wert) for wert in zeile[:numKoordinaten]]];
         if (len(punkte) > 1):
            diff = [x-y for x, y in zip(punkte[-1], punkte[-2])];
            indizes = [idx for idx, zahl in enumerate(diff) if abs(zahl) > tol];
            for idx in indizes:
               if (idx not in reihenfolge):
                  reihenfolge += [idx];
                  numwerte += [idx_zeile];
         #
         wertzeile = [0 for idx in range(numVar)];
         tempwerte = [float(wert) for wert in zeile[numKoordinaten:]];
         wertzeile[:len(tempwerte)] = tempwerte;
         werte += [wertzeile];
   #
   elemente = [];
   if (len(reihenfolge) == 2):
      a, b = [numwerte[idx] for idx in reihenfolge];
      numA = numwerte[1] - 1;
      numB = int(len(punkte)/numwerte[1]) - 1;
      for a_idx in range(numA):
         for b_idx in range(numB):
            basispunkt = + a_idx*a + b_idx*b;
            elemente += [(basispunkt, basispunkt+a, basispunkt+a+b, basispunkt+b), ];
      #
   elif (len(reihenfolge) == 3):
      a, b, c = [numwerte[idx] for idx in reihenfolge];
      numA = numwerte[1] - 1;
      numB = int(numwerte[2]/numwerte[1]) - 1;
      numC = int(len(punkte)/numwerte[2]) - 1;
      for a_idx in range(numA):
         for b_idx in range(numB):
            for c_idx in range(numC):
               basispunkt = + a_idx*a + b_idx*b + c_idx*c;
               elemente += [(basispunkt, basispunkt+a, basispunkt+a+b, basispunkt+b,
                  basispunkt+c, basispunkt+a+c, basispunkt+a+b+c, basispunkt+b+c), ];
   else:
      Log('# Warnung: Fuer Elementbestimmung nur zwei oder drei Koordinaten erlaubt');
   #
   return [punkte, elemente, werte];
#


# -------------------------------------------------------------------------------------------------
def _ZielwertquaderElementeEinlesen(dateiname, numKoordinaten, numVar):
   """Liest aus einer csv-Datei namens dateiname alle Zeilen ein. In jeder Zeile werden
   numKoordinaten Eintraege als Koordinaten erwartet (d.h. 2 oder 3) und die restlichen Werte werden
   als Ergebnisse an diesen Koordinaten betrachtet. Mit 2 Koordinaten werden Elemente aus vier
   Knoten angenommen, mit 3 Koordinaten aus acht.
   Die Koordinaten stehen fuer Punkte in den Elementen an denen die Ergebnisse fuer das ganze
   Element definiert sind. Nur wenn die Koordinaten pro Koordinatenrichtung die gleichen Abstaende
   haben, entsprechen die Punkte auch den tatsaechlichen Elementmittelpunkten.
   """
   from hilfen import Log
   import csv
   #
   tol = 1e-6;
   reihenfolge = [];
   numwerte = [];
   elementpunkte = [];
   elementwerte = [];
   with open(dateiname, 'r') as eingabe:
      eingelesen = csv.reader(eingabe, delimiter=',');
      for idx_zeile, zeile in enumerate(eingelesen):
         elementpunkte += [[float(wert) for wert in zeile[:numKoordinaten]]];
         if (len(elementpunkte) > 1):
            diff = [x-y for x, y in zip(elementpunkte[-1], elementpunkte[-2])];
            indizes = [idx for idx, zahl in enumerate(diff) if abs(zahl) > tol];
            for idx in indizes:
               if (idx not in reihenfolge):
                  reihenfolge += [idx];
                  numwerte += [idx_zeile];
         #
         wertzeile = [0 for idx in range(numVar)];
         tempwerte = [float(wert) for wert in zeile[numKoordinaten:]];
         wertzeile[:len(tempwerte)] = tempwerte;
         elementwerte += [wertzeile];
   #
   punkte = [];
   elemente = [];
   if (len(reihenfolge) == 2):
      elem_a = [elementpunkte[idx][reihenfolge[0]] for idx in range(numwerte[1])];
      elem_b = [elementpunkte[int(numwerte[1]*idx)][reihenfolge[1]] for idx in range(int(len(elementpunkte)/numwerte[1]))];
      #
      punkte_a = [0.5*(elem_a[idx] + elem_a[idx-1]) for idx in range(1, len(elem_a))];
      punkte_a = [2.0*elem_a[0] - punkte_a[0]] + punkte_a + [2.0*elem_a[-1] - punkte_a[-1]];
      #
      punkte_b = [0.5*(elem_b[idx] + elem_b[idx-1]) for idx in range(1, len(elem_b))];
      punkte_b = [2.0*elem_b[0] - punkte_b[0]] + punkte_b + [2.0*elem_b[-1] - punkte_b[-1]];
      #
      a = 1;
      b = len(punkte_a);
      for b_idx, bKoord in enumerate(punkte_b):
         for a_idx, aKoord in enumerate(punkte_a):
            punkte += [(aKoord, bKoord)];
            if ((a_idx == len(punkte_a)-1) or (b_idx == len(punkte_b)-1)):
               continue;
            #
            basispunkt = + a_idx*a + b_idx*b;
            elemente += [(basispunkt, basispunkt+a, basispunkt+a+b, basispunkt+b), ];
   #
   elif (len(reihenfolge) == 3):
      elem_a = [elementpunkte[idx][reihenfolge[0]] for idx in range(numwerte[1])];
      elem_b = [elementpunkte[int(numwerte[1]*idx)][reihenfolge[1]] for idx in range(int(numwerte[2]/numwerte[1]))];
      elem_c = [elementpunkte[int(numwerte[2]*idx)][reihenfolge[2]] for idx in range(int(len(elementpunkte)/numwerte[2]))];
      #
      punkte_a = [0.5*(elem_a[idx] + elem_a[idx-1]) for idx in range(1, len(elem_a))];
      punkte_a = [2.0*elem_a[0] - punkte_a[0]] + punkte_a + [2.0*elem_a[-1] - punkte_a[-1]];
      #
      punkte_b = [0.5*(elem_b[idx] + elem_b[idx-1]) for idx in range(1, len(elem_b))];
      punkte_b = [2.0*elem_b[0] - punkte_b[0]] + punkte_b + [2.0*elem_b[-1] - punkte_b[-1]];
      #
      punkte_c = [0.5*(elem_c[idx] + elem_c[idx-1]) for idx in range(1, len(elem_c))];
      punkte_c = [2.0*elem_c[0] - punkte_c[0]] + punkte_c + [2.0*elem_c[-1] - punkte_c[-1]];
      #
      a = 1;
      b = len(punkte_a);
      c = len(punkte_a)*len(punkte_b)
      for c_idx, cKoord in enumerate(punkte_c):
         for b_idx, bKoord in enumerate(punkte_b):
            for a_idx, aKoord in enumerate(punkte_a):
               punkte += [(aKoord, bKoord, cKoord)];
               if ((a_idx == len(punkte_a)-1) or (b_idx == len(punkte_b)-1) or (c_idx == len(punkte_c)-1)):
                  continue;
               #
               basispunkt = + a_idx*a + b_idx*b + c_idx*c;
               elemente += [(basispunkt, basispunkt+a, basispunkt+a+b, basispunkt+b,
                  basispunkt+c, basispunkt+a+c, basispunkt+a+b+c, basispunkt+b+c), ];
   else:
      Log('# Warnung: Fuer Elementbestimmung nur zwei oder drei Koordinaten erlaubt');
   #
   return [punkte, elemente, elementwerte];
#


# -------------------------------------------------------------------------------------------------
def ZielwertquaderEinlesen(dateiname, numKoordinaten, numVar, knotenwerte=False):
   """Liest aus einer csv-Datei namens dateiname alle Zeilen ein. In jeder Zeile werden
   numKoordinaten Eintraege als Koordinaten erwartet (d.h. 2 oder 3) und die restlichen Werte werden
   als Ergebnisse an diesen Koordinaten betrachtet. Mit 2 Koordinaten werden Elemente aus vier
   Knoten angenommen, mit 3 Koordinaten aus acht.

   Falls knotenwerte=True werden die Koordinaten als Knotenkoordinaten und die Ergebnisse an den
   Knotenkoordinaten interpretiert. Andernfalls werden die Koordinaten als Elementpunkte betrachtet,
   um die mithilfe der Nachbarelementpunkte die Elementgrenzen (Knotenkoordinaten) bestimmt werden.

   Erwartet jeweils die gleiche Anzahl an Werten fuer jeden Vektor einer Koordinatenrichtung, um
   daraus ohne weitere Informationen quaderfoermige Elemente zu generieren (fuer knotenweise=True).
   Fuer knotenweise=False sollte zusaetzlich jeweils ein konstanter Abstand zwischen den Werten pro
   Koordinatenrichtung vorliegen, da ansonsten die Ergebnisse nicht am tatsaechlichen Mittelpunkt
   definiert sind (aber so interpretiert werden).

   Gibt [Koordinaten, Elemente, Ergebnisse] zurueck.
   """
   if (knotenwerte):
      return _ZielwertquaderKnotenEinlesen(dateiname=dateiname, numKoordinaten=numKoordinaten,
         numVar=numVar);
   else:
      return _ZielwertquaderElementeEinlesen(dateiname=dateiname, numKoordinaten=numKoordinaten,
         numVar=numVar);
#

   
# -------------------------------------------------------------------------------------------------
def _FieldOutputVariablenliste(bezugsframe, variablenliste):
   """Erstelle anhand der uebergebenen variablenliste mit ggfs. nicht exakten Namen von FieldOutputs
   eine modifizierte Liste mit den exakten Namen vorhandener FieldOutputs, die weiter verwendet
   werden. Gibt die ueberarbeitete variablenliste zurueck.
   
   Falls der Eintrag in variablenliste mehreren FieldOutputs entspricht (bspw. "SDV", die alle als
   einzelne FieldOutputs gespeichert werden), dann erstelle eine Unterliste mit allen FieldOutputs,
   in deren Namen Eintrag vorkommt.
   """
   from hilfen import Log
   #
   exakte_variablenliste = [];
   for variable in variablenliste:
      if (bezugsframe.fieldOutputs.has_key(variable)):
         exakte_variablenliste += [variable];
      else:         
         unterliste = [];
         for outputvariable in bezugsframe.fieldOutputs.keys():
            if (variable in outputvariable):
               if (not (variable == 'SDV')):
                  Log('# Warnung: Angeforderte Variable >' + variable + '< nicht einzeln vorhanden aber im Namen von : ' + outputvariable);
               #
               unterliste += [outputvariable];
         #
         if (unterliste == []):
            Log('# Abbruch: Angeforderte Variable >' + variable + '< nicht im angegebenen Schritt/Frame der odb verfuegbar');
            return [];
         else:
            exakte_variablenliste += [unterliste];
   #
   return exakte_variablenliste;
#


# -------------------------------------------------------------------------------------------------
def _ZustandsuebertragungDatenVorbereiten(dimensionen, odbknoten, odbelemente, mdbknoten,
   mdbelemente, odbAbaqus=True):
   """Formatiere den Input fuer die externe Bibliothek zur Zustandsuebertragung. Wenn entweder
   odbelemente oder mdbelemente None ist, werden die Daten fuer diesen Typ nicht bearbeitet und
   die Rueckgabewerte (cpp_###knoten sowie cpp_###elemente) sind fuer diesen Typ None.
   Gibt [cpp_odbknoten, cpp_odbelemente, cpp_mdbknoten, cpp_mdbelemente] zurueck.
   """
   if (odbAbaqus):
      cpp_odbknoten, cpp_odbelemente = _ZustandsuebertragungOdbVorbereiten(dimensionen=dimensionen,
         odbknoten=odbknoten, odbelemente=odbelemente);
   else:
      cpp_odbknoten, cpp_odbelemente = _ZustandszuweisungVorbereiten(knoten=odbknoten,
         elemente=odbelemente);
   #
   cpp_mdbknoten, cpp_mdbelemente = _ZustandsuebertragungMdbVorbereiten(dimensionen=dimensionen,
      mdbknoten=mdbknoten, mdbelemente=mdbelemente);
   #
   return [cpp_odbknoten, cpp_odbelemente, cpp_mdbknoten, cpp_mdbelemente];
#


# -------------------------------------------------------------------------------------------------
def _ZustandszuweisungVorbereiten(knoten, elemente):
   """Formatiere eingelesene Daten (knoten und elemente) fuer die externe Bibliothek zur
   Zustandsuebertragung. Erwartet eine Matrix bzw. Liste von Tupeln fuer knoten und fuer elemente,
   wobei in knoten jeweils die (i.A. drei) Koordinaten des Punktes sind und ind elemente die
   (oftmals acht) Indizes der dazugehoerigen Punkte in knoten.
   Gibt [cpp_knoten, cpp_elemente] zurueck.
   """
   from ctypes import c_double, c_int
   #
   mod_mdbknoten = [punkt for gruppe in knoten for punkt in gruppe];
   DoubleArray_mdbknoten = c_double * len(mod_mdbknoten);
   cpp_mdbknoten = DoubleArray_mdbknoten(*list(mod_mdbknoten));
   #
   knoten_pro_element = len(elemente[0]);
   mod_mdbelemente = [-1 for idx in range(knoten_pro_element*len(elemente))];
   for idx_gruppe, gruppe in enumerate(elemente):
      #mod_mdbelemente[knoten_pro_element*idx_gruppe:knoten_pro_element*(idx_gruppe+1)] = [int(elem) for elem in gruppe];
      for idx_elem, elem in enumerate(gruppe):
         mod_mdbelemente[knoten_pro_element*idx_gruppe + idx_elem] = int(elem);
   #mod_mdbelemente = [elem for gruppe in elemente for elem in gruppe];
   IntArray_mdbelemente = c_int * len(mod_mdbelemente);
   cpp_mdbelemente = IntArray_mdbelemente(*list(mod_mdbelemente));
   # Quelle: https://coderwall.com/p/rcmaea/flatten-a-list-of-lists-in-one-line-in-python
   return [cpp_mdbknoten, cpp_mdbelemente];
#


# -------------------------------------------------------------------------------------------------
def _ZustandsuebertragungOdbVorbereiten(dimensionen, odbknoten, odbelemente):
   """Formatiere Ausgabedaten (odbknoten, odbelemente) fuer die externe Bibliothek zur
   Zustandsuebertragung. Gibt [cpp_odbknoten, cpp_odbelemente] zurueck.
   """
   from ctypes import c_double, c_int
   from hilfen import ErstelleLabelsortierteGeomlist
   #
   # Von der externen Bibliothek werden die Knoten-Daten als Array im folgenden Format erwartet:
   # [P0x, P0y, (P0z, ) P1x, P1y, (P1z, ), ...]
   # also sortiert nach den Punkten und fuer jeden Punkt alle Koordianten beginnend mit der
   # x-Koordinate. Die Anzahl an Koordinaten entspricht dimensionen und die Anzahl an Eckpunkten
   # ist in den knoten_pro_...element-Variablen gespeichert
   # Die Element-Daten werden als Array im folgenden Format erwartet:
   # [L0_P0, L0_P1, L0_P2, (L0_P3, L0_P4, L0_P5, L0_P6, L0_P7),   L1_P0, L1_P1, L1_P2, ...]
   # also sortiert nach den Elementen und fuer jedes Element die Labels aller Eckpunkte (fuer
   # Vierecke und Hexahedrons in der passenden Reihenfolge).
   #
   # Fuer odbknoten und odbelemente kann die Sortierung der Label relativ beliebig sein.
   # Deshalb wird ein labelsortiertes Dict erstellt, um von den Labels auf die dazugehoerigen
   # Indizes zuweisen zu koennen. Die Labels starten zusaetzlich bei 1 statt bei 0.
   knoten_pro_odbelement = len(odbelemente[0].connectivity);
   label_zu_idx_odbknoten = ErstelleLabelsortierteGeomlist(geomliste=odbknoten);
   mod_odbknoten = [0.0 for idx in range(int(dimensionen*len(odbknoten)))];
   for label_knoten in range(0, len(odbknoten)):
      zielKnoten = odbknoten[label_zu_idx_odbknoten[label_knoten+1]];
      for achse in range(dimensionen):
         mod_odbknoten[dimensionen*label_knoten+achse] = zielKnoten.coordinates[achse];
   #
   DoubleArray_odbknoten = c_double * len(mod_odbknoten);
   cpp_odbknoten = DoubleArray_odbknoten(*list(mod_odbknoten));
   #
   label_zu_idx_odbelemente = ErstelleLabelsortierteGeomlist(geomliste=odbelemente);
   mod_odbelemente = [0 for idx in range(int(knoten_pro_odbelement*len(odbelemente)))];
   for label_elemente in range(len(odbelemente)):
      zielElement = odbelemente[label_zu_idx_odbelemente[label_elemente+1]];
      for idx_eckpunkt in range(knoten_pro_odbelement):
         # Da im Folgenden die Indizes und nicht die Label betrachtet werden,
         # und die Labels mit 1 statt Null starten, ziehe Eins ab
         mod_odbelemente[knoten_pro_odbelement*label_elemente+idx_eckpunkt] = zielElement.connectivity[idx_eckpunkt]-1;
   #
   IntArray_odbelemente = c_int * len(mod_odbelemente);
   cpp_odbelemente = IntArray_odbelemente(*list(mod_odbelemente));
   #
   return [cpp_odbknoten, cpp_odbelemente];
#


# -------------------------------------------------------------------------------------------------
def _ZustandsuebertragungMdbVorbereiten(dimensionen, mdbknoten, mdbelemente):
   """Formatiere Modelldaten (mdbknoten, mdbelemente) fuer die externe Bibliothek zur
   Zustandsuebertragung. Gibt [cpp_mdbknoten, cpp_mdbelemente] zurueck.
   """
   from ctypes import c_double, c_int
   #
   # Fuer mdbknoten und mdbelemente entspricht der Index eines Knotens dem Label
   # Bei mdbelemente sind die unter connectivity gelisteten Werte die Indizes.
   knoten_pro_mdbelement = len(mdbelemente[0].connectivity);
   mod_mdbknoten = [0.0 for idx in range(int(dimensionen*len(mdbknoten)))];
   for idx_knoten in range(0, len(mdbknoten)):
      for achse in range(dimensionen):
         mod_mdbknoten[dimensionen*idx_knoten+achse] = mdbknoten[idx_knoten].coordinates[achse];
   #
   DoubleArray_mdbknoten = c_double * len(mod_mdbknoten);
   cpp_mdbknoten = DoubleArray_mdbknoten(*list(mod_mdbknoten));
   #
   mod_mdbelemente = [-1 for idx in range(int(knoten_pro_mdbelement*len(mdbelemente)))];
   for idx_elemente in range(len(mdbelemente)):
      for idx_eckpunkt in range(knoten_pro_mdbelement):
         mod_mdbelemente[knoten_pro_mdbelement*idx_elemente+idx_eckpunkt] = mdbelemente[idx_elemente].connectivity[idx_eckpunkt];
   #
   IntArray_mdbelemente = c_int * len(mod_mdbelemente);
   cpp_mdbelemente = IntArray_mdbelemente(*list(mod_mdbelemente));
   #
   return [cpp_mdbknoten, cpp_mdbelemente];
#


# -------------------------------------------------------------------------------------------------
def _ZustandsuebertragungAusgabeVorbereiten(mdbname, ausgabevariable, bezugsframe=None):
   rueckgabe = [None, None, None];
   """Je nach ausgabevariable entsprechende Dateinamen und keywordBlock-Eintraege vorbereiten. Falls
   ein bezugsframe uebergeben wird werden die entsprechenden odbergebnisse ermittelt, ansonsten
   wird dafuer None angenommen. Gibt [ausgabedatei, ausgabetext, odbergebnisse] zurueck.
   """
   from abaqusConstants import DOUBLE_PRECISION
   from hilfen import Log
   #
   odbergebnisse = None;
   if (isinstance(ausgabevariable, list)):
      if ('SDV' in ausgabevariable[0]):
         ausgabedatei = mdbname + '_sdv.add';
         ausgabetext = '*Initial Conditions, type=SOLUTION, input=' + ausgabedatei;
      else:
         Log('Warnung: Variablenliste ausser SDV nicht unterstuetzt');
         return rueckgabe;
      #
      if (bezugsframe is not None):
         # Da nicht nur ein FieldOutput sondern eine Liste an FieldOutputs betrachtet werden soll
         # (d.h. SDVs sollen zusammengefasst werden), erzeuge eine kuenstliche odbergebnisse-Struktur
         odbergebnisse = [];
         num_values = len(bezugsframe.fieldOutputs[ausgabevariable[0]].values);
         for idx_val in range(num_values):
            tempdata = None;
            tempdataDouble = None;
            tempergebnis = bezugsframe.fieldOutputs[ausgabevariable[0]].values[idx_val];
            if (tempergebnis.precision == DOUBLE_PRECISION):
               tempdataDouble = [bezugsframe.fieldOutputs[einzelvar].values[idx_val].dataDouble for einzelvar in ausgabevariable];
            else:
               tempdata = [bezugsframe.fieldOutputs[einzelvar].values[idx_val].data for einzelvar in ausgabevariable];
            #
            odbergebnisse += [FieldOutputValue(precision=tempergebnis.precision, data=tempdata,
               dataDouble=tempdataDouble, elementLabel=tempergebnis.elementLabel,
               nodeLabel=tempergebnis.nodeLabel)];
   else:
      if (ausgabevariable == 'S'):
         ausgabedatei = mdbname + '_s.add';
         ausgabetext = '*Initial Conditions, type=STRESS, input=' + ausgabedatei;
      elif (ausgabevariable == 'SVAVG'):
         ausgabedatei = mdbname + '_svavg.add';
         ausgabetext = '*Initial Conditions, type=STRESS, input=' + ausgabedatei;
      elif (ausgabevariable == 'EVF'): # FIXME: ungetestet
         ausgabedatei = mdbname + '_evf.add';
         ausgabetext = '*Initial Conditions, type=VOLUME FRACTION, input=' + ausgabedatei;
      else:
         Log('Warnung: Uebertragung von ' + ausgabevariable + ' nicht getestet - sorgfaeltig pruefen');
         ausgabedatei = mdbname + '_' + ausgabevariable.lower() + '.add';
         ausgabetext = '*Initial Conditions, type=FIELD, Variable=' + ausgabevariable + ', input=' + ausgabedatei;
      #
      if (bezugsframe is not None):
         odbergebnisse = bezugsframe.fieldOutputs[ausgabevariable].values;
   #
   return [ausgabedatei, ausgabetext, odbergebnisse];
#


# -------------------------------------------------------------------------------------------------
def _ZustandszuweisungErgebnisdateiSchreiben(ausgabedatei, ergebnisse, mdbinstname,
   gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente, mdbknoten, knoten_pro_mdbelement,
   knotenweise):
   """Schreibe den zugewiesenen Zustand aus ergebnisse und bezugsElemente (elementweise Ergebnisse
   mit knotenweise=False) oder ergebnisse und gewichtungKnotenWerte sowie gewichtungKnotenLabels
   (fuer knotenweise Ergebnisse mit knotenweise=True) in eine Datei namens ausgabedatei. Bei
   knotenweisen Ergebnissen ist auch die Anzahl an knoten_pro_mdbelement noetig.
   """
   from hilfen import BlockAusgabe
   #
   laenge_ausgabewerte = len(ergebnisse[0]);
   if (not knotenweise):
      with open(ausgabedatei, 'w') as ausgabe:
         for idx_elem, label_odbelem in enumerate(bezugsElemente):
            # Nur bearbeiten, wenn auch tatsaechlich ein Wert zugewiesen werden soll
            if (label_odbelem == 0):
               continue;
            #
            elemLabel = idx_elem + 1; # Die Labels der mdb-Elemente sind immer sortiert
            try:
               # Da die Anzahl an Elementen in mdb und odb i.d.R. nicht uebereinstimmen, sollen
               # alle mdbElemente ohne Ergebnisse uebersprungen werden.
               temp_data = ergebnisse[label_odbelem];
            except:
               continue;
            #
            temp_ergebnis = [mdbinstname + '.' + str(elemLabel)] + list(temp_data);
            ausgabe.write(BlockAusgabe(temp_ergebnis));
   else:
      with open(ausgabedatei, 'w') as ausgabe:
         for idx_knoten in range(len(mdbknoten)):
            nodeLabel = idx_knoten + 1; # Die Labels der mdb-Elemente sind immer sortiert
            ausgabewerte = [0.0 for idx in range(laenge_ausgabewerte)];
            labeltemp = -1;
            # FIXME: Die Umrechnung von knoten_pro_odbelement auf knoten_pro_mdbelement ist hier
            #        scheinbar noch nicht implementiert -> nachholen
            for idx_punkt in range(knoten_pro_mdbelement):
               idxtemp = gewichtungKnotenLabels[knoten_pro_mdbelement*idx_knoten+idx_punkt];
               labeltemp = idxtemp + 1;
               try:
                  # Da die Anzahl an Knoten in mdb und odb i.d.R. nicht uebereinstimmen, sollen
                  # alle mdbKnoten ohne Ergebnisse uebersprungen werden.
                  temp_data = ergebnisse[labeltemp];
               except:
                  continue;
               #
               ausgabewerte = [ausgabewerte[idx] + gewichtungKnotenWerte[knoten_pro_mdbelement*idx_knoten+idx_punkt]*temp_data[idx] for idx in range(laenge_ausgabewerte)];
            #
            temp_ergebnis = [mdbinstname + '.' + str(nodeLabel)] + ausgabewerte;
            ausgabe.write(BlockAusgabe(temp_ergebnis));
#


# -------------------------------------------------------------------------------------------------
def _ZustandsuebertragungErgebnisdateiSchreiben(ausgabedatei, mdbinstname, odbergebnisse,
   gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente, mdbknoten, knoten_pro_mdbelement):
   """Schreibe den berechneten Zustand aus odbergebnisse und bezugsElemente (fuer elementweise
   Ergebnisse) oder odbergebnisse und gewichtungKnotenWerte sowie gewichtungKnotenLabels (fuer
   knotenweise Ergebnisse) in eine Datei namens ausgabedatei. Bei knotenweisen Ergebnissen ist auch
   die Anzahl an knoten_pro_mdbelement noetig.
   """
   from abaqusConstants import SCALAR, DOUBLE_PRECISION
   from hilfen import BlockAusgabe
   from hilfen import ErstelleElementLabelsortierteGeomlist, ErstelleNodeLabelsortierteGeomlist
   #
   einzelergebnis = odbergebnisse[0];
   if (einzelergebnis.type == SCALAR):
      laenge_ausgabewerte = 1;
   else:
      if (einzelergebnis.precision == DOUBLE_PRECISION):
         laenge_ausgabewerte = len(einzelergebnis.dataDouble);
      else:
         laenge_ausgabewerte = len(einzelergebnis.data);
   #
   if (not (einzelergebnis.elementLabel is None)):
      elementlabel_zu_idx_output = ErstelleElementLabelsortierteGeomlist(geomliste=odbergebnisse);
      with open(ausgabedatei, 'w') as ausgabe:
         for idx_elem, label_odbelem in enumerate(bezugsElemente):
            # Nur bearbeiten, wenn auch tatsaechlich ein Wert zugewiesen werden soll
            if (label_odbelem == 0):
               continue;
            #
            elemLabel = idx_elem + 1; # Die Labels der mdb-Elemente sind immer sortiert
            try:
               # Da die Anzahl an Elementen in mdb und odb i.d.R. nicht uebereinstimmen, sollen
               # alle mdbElemente ohne Ergebnisse uebersprungen werden.
               zielElement = odbergebnisse[elementlabel_zu_idx_output[label_odbelem]];
            except:
               continue;
            #
            if (zielElement.precision == DOUBLE_PRECISION):
               temp_data = zielElement.dataDouble;
            else:
               temp_data = zielElement.data;
            #
            if (einzelergebnis.type == SCALAR):
               temp_ergebnis = [mdbinstname + '.' + str(elemLabel)] + [str(temp_data)];
            else:
               temp_ergebnis = [mdbinstname + '.' + str(elemLabel)] + list(temp_data);
            #
            ausgabe.write(BlockAusgabe(temp_ergebnis));
   #
   if (not (einzelergebnis.nodeLabel is None)):
      nodelabel_zu_idx_output = ErstelleNodeLabelsortierteGeomlist(geomliste=odbergebnisse);
      with open(ausgabedatei, 'w') as ausgabe:
         for idx_knoten in range(len(mdbknoten)):
            nodeLabel = idx_knoten + 1; # Die Labels der mdb-Elemente sind immer sortiert
            ausgabewerte = [0.0 for idx in range(laenge_ausgabewerte)];
            labeltemp = -1;
            # FIXME: Die Umrechnung von knoten_pro_odbelement auf knoten_pro_mdbelement ist hier
            #        scheinbar noch nicht implementiert -> nachholen
            for idx_punkt in range(knoten_pro_mdbelement):
               idxtemp = gewichtungKnotenLabels[knoten_pro_mdbelement*idx_knoten+idx_punkt];
               labeltemp = idxtemp + 1;
               try:
                  # Da die Anzahl an Knoten in mdb und odb i.d.R. nicht uebereinstimmen, sollen
                  # alle mdbKnoten ohne Ergebnisse uebersprungen werden.
                  zielKnoten = odbergebnisse[nodelabel_zu_idx_output[labeltemp]];
               except:
                  continue;
               #
               if (zielKnoten.precision == DOUBLE_PRECISION):
                  temp_data = zielKnoten.dataDouble;
               else:
                  temp_data = zielKnoten.data;
               #
               if (einzelergebnis.type == SCALAR):
                  ausgabewerte[0] += gewichtungKnotenWerte[knoten_pro_mdbelement*idx_knoten+idx_punkt]*temp_data;
               else:
                  ausgabewerte = [ausgabewerte[idx] + gewichtungKnotenWerte[knoten_pro_mdbelement*idx_knoten+idx_punkt]*temp_data[idx] for idx in range(laenge_ausgabewerte)];
            #
            temp_ergebnis = [mdbinstname + '.' + str(nodeLabel)] + ausgabewerte;
            ausgabe.write(BlockAusgabe(temp_ergebnis));
#


# -------------------------------------------------------------------------------------------------
def _UebertragungGueltigeElementeCheck(dimensionen, ecken):
   """Pruefe, ob einer der unterstuetzten Elementtypen verwendet wird. Fuer zweidimensionale
   Elemente sind das Dreieck und Viereck, fuer dreidimensionale Elemente Tetraeder und Hexahedron.
   Gibt Wahrheitswert fuer die Gueltigkeit zurueck.
   """
   gueltigkeit = False;
   if (dimensionen == 2):
      if ((ecken == 3) or (ecken == 4)):
         gueltigkeit = True;
   #
   if (dimensionen == 3):
      if ((ecken == 4) or (ecken == 8)):
         gueltigkeit = True;
   #
   return gueltigkeit;
#


# -------------------------------------------------------------------------------------------------
def Zustandsuebertragung(session, odbname, odbinstname, variablenliste, modell, mdbinstname,
   mdbknoten=[], odbknoten=[], step=-1, frame=-1):
   """Uebertrage den Zustand aus einer odb namens odbname auf ein in der aktuellen session geladenes
   Modell modell. Dazu wird jeden in variablenliste uebergebene Variable an jedem Knoten bzw.
   Element (je nach Typ) der odbinstname aus dem angegebenen step und frame ausgelesen und als
   Anfangsloesungen von den Koordinaten der odbelemente oder odbknoten auf die Koordinaten der
   mdbknoten in der Assembly-Instanz namens mdbinstname übertragen. Da die Position der Knoten nicht
   uebereinstimmen muss, wird eine lineare Interpolation der Werte aus der odb-Datei auf die Knoten
   des neuen Modells vorgenommen.
   
   Fuer eine Zustandsuebertragung auf ein gleichartiges Modell (gleiche Offsets und Geometrien) ist
   es nicht noetig, mdbknoten und odbknoten zusaetzlich zu uebergeben. Wenn die Geometrieen aber
   verschoben sind (anderes Nulloffset o.ae.), dann bietet sich eine Transformation der Koordinaten
   an (bspw. mit der Funktion Knotentransformation). Die aktualisierten mdbknoten oder/und odbknoten
   muessen dann entsprechend uebergeben werden.
   
   Gibt [gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente] zurueck.
   
   Es wird 2D -> 2D und 3D -> 3D unterstuetzt, aber nicht gemischt. Fuer 2D-Elemente sind Dreiecke
   und Vierecke zulaessig, fuer 3D-Elemente Tetraeder und Hexahedrons. Die Unterscheidung wird am
   Elementnamen getroffen: Alle Elemente mit 3D im Namen zaehlen zu den 3D-Elementen (bspw. C3D8R).
      
   Wichtig: Alle Elemente des parts muessen den gleichen Elementyp haben.
   """
   from ctypes import c_double, c_int
   import odbAccess
   from hilfen import Log, BibliothekLaden
   # Odb-Datei oeffnen, falls nicht schon offen
   if session.odbData.has_key(odbname):
      odb = session.odbs[odbname];
   else:
      odb = session.openOdb(name=odbname);
   #
   if (odbknoten == []):
      odbknoten = odb.rootAssembly.instances[odbinstname.upper()].nodes;
   #
   if (mdbknoten == []):
      mdbknoten = modell.rootAssembly.instances[mdbinstname].nodes;
   #
   mySteps = session.odbData[odbname].steps.keys();
   # Variablen pruefen
   try:
      bezugsframe = odb.steps[mySteps[step]].frames[frame];
   except:
      Log('# Abbruch: Angegebener Step/Frame nicht verfuegbar');
      return [];
   #
   # Erstelle eine modifizierte Variablenliste mit den exakten Namen der geforderten FieldOutputs
   mod_variablenliste = _FieldOutputVariablenliste(bezugsframe=bezugsframe,
      variablenliste=variablenliste);
   if (mod_variablenliste == []):
      Log('# Abbruch: Variablenliste ungueltig/leer');
      return [];
   #
   # Lade die Bibliothek zur Bestimmung der Gewichtungen
   bibliothek = BibliothekLaden(dateiname='gewichtung');
   if (bibliothek is None):
      Log('# Abbruch: Externe Bibliothek gewichtung nicht gefunden');
      return [];
   #
   cpp_gewichtung_bestimmen = bibliothek.Gewichtung_Bestimmen;
   #
   Log('# 1-3: Bereite Daten fuer Zustandsuebertragung vor');
   #
   odbelemente = odb.rootAssembly.instances[odbinstname.upper()].elements;
   mdbelemente = modell.rootAssembly.instances[mdbinstname].elements;
   knoten_pro_odbelement = len(odbelemente[0].connectivity);
   knoten_pro_mdbelement = len(mdbelemente[0].connectivity);
   #
   odb_dimensionen = 2;
   if ('3D' in str(odbelemente[0].type)):
      odb_dimensionen = 3;
   #
   mdb_dimensionen = 2;
   if ('3D' in str(mdbelemente[0].type)):
      mdb_dimensionen = 3;
   #
   if (not (mdb_dimensionen == odb_dimensionen)):
      Log('# Abbruch: Zustandsuebertragung nur 2D->2D oder 3D->3D moeglich, nicht gemischt');
      return [];
   #
   dimensionen = odb_dimensionen;
   #
   # Pruefe, ob gueltige Elemente/Knotenformate vorliegen
   if (not _UebertragungGueltigeElementeCheck(dimensionen=dimensionen, ecken=knoten_pro_odbelement)):
      Log('# Odb-Elemente/Knoten in nicht unterstuetztem Format');
      return [];
   #
   if (not _UebertragungGueltigeElementeCheck(dimensionen=dimensionen, ecken=knoten_pro_mdbelement)):
      Log('# Mdb-Elemente/Knoten in nicht unterstuetztem Format');
      return [];
   #
   cpp_odbknoten, cpp_odbelemente, cpp_mdbknoten, cpp_mdbelemente = _ZustandsuebertragungDatenVorbereiten(dimensionen=dimensionen,
      odbknoten=odbknoten, odbelemente=odbelemente, mdbknoten=mdbknoten, mdbelemente=mdbelemente);
   #
   # Rueckgabewerte ueber Pointer
   # Fuer die gewichtungen wird jedem Knoten des neuen Modells (mdb) das Element in der odb bestimmt,
   # in dem der Punkt liegt. Fuer jeden Knoten aus der odb, die dieses odb-Element definieren,
   # wird die Gewichtung bestimmt
   gewichtungKnotenLabels = [0 for idx in range(knoten_pro_odbelement*len(mdbknoten))];
   IntArray_gewKnotenLabels = c_int * len(gewichtungKnotenLabels);
   cpp_gewKnotenLabels = IntArray_gewKnotenLabels(*list(gewichtungKnotenLabels));
   #
   gewichtungKnotenWerte = [0.0 for idx in range(knoten_pro_odbelement*len(mdbknoten))];
   DoubleArray_gewKnotenWerte = c_double * len(gewichtungKnotenWerte);
   cpp_gewKnotenWerte = DoubleArray_gewKnotenWerte(*list(gewichtungKnotenWerte));
   #
   bezugsElemente = [0 for idx in range(len(mdbelemente))];
   IntArray_bezugsElemente = c_int * len(bezugsElemente);
   cpp_bezugsElemente = IntArray_bezugsElemente(*list(bezugsElemente));
   #
   Log('# 2-3: Ermittle Gewichtungen');
   cpp_gewichtung_bestimmen(c_int(dimensionen), c_int(knoten_pro_odbelement),
      c_int(knoten_pro_mdbelement), cpp_odbknoten, c_int(len(odbelemente)), cpp_odbelemente,
      c_int(len(mdbknoten)), cpp_mdbknoten, c_int(len(mdbelemente)), cpp_mdbelemente,
      cpp_gewKnotenLabels, cpp_gewKnotenWerte, cpp_bezugsElemente);
   #
   # Wieder Listen aus den uebergebenen Pointern erzeugen
   gewichtungKnotenLabels = list(cpp_gewKnotenLabels);
   gewichtungKnotenWerte = list(cpp_gewKnotenWerte);
   bezugsElemente = list(cpp_bezugsElemente);
   #
   Log('# 3-3: Weise Werte zu'); 
   idx_naechstereintrag = _ErzeugeAbapysAnfangsbedingungenEintrag(modell=modell);
   #
   # Anzahl der Ausgabewerte pro Knoten/Element ermitteln
   for ausgabevariable in mod_variablenliste:
      ausgabedatei, ausgabetext, odbergebnisse = _ZustandsuebertragungAusgabeVorbereiten(mdbname=modell.name,
         ausgabevariable=ausgabevariable, bezugsframe=bezugsframe);
      if (any([ausgabedatei, ausgabetext, odbergebnisse]) is None):
         Log('# Abbruch: Zugriffsprobleme auf Datei oder ungueltige Ergebnisse');
         return [];
      #
      modell.keywordBlock.insert(idx_naechstereintrag, ausgabetext);
      _ZustandsuebertragungErgebnisdateiSchreiben(ausgabedatei=ausgabedatei,
         odbergebnisse=odbergebnisse, mdbinstname=mdbinstname,
         gewichtungKnotenLabels=gewichtungKnotenLabels, gewichtungKnotenWerte=gewichtungKnotenWerte,
         bezugsElemente=bezugsElemente, mdbknoten=mdbknoten, knoten_pro_mdbelement=knoten_pro_mdbelement);
   #
   return [gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente];
#


# -------------------------------------------------------------------------------------------------
def Zustandszuweisung(session, modell, zielkoordinaten, zielelemente, zielwerte, mdbinstname,
   mdbknoten=[], variablentyp=['SDV']):
   """Weise die zielwerte an den zielkoordinaten bze. zielelemente einem in der aktuellen session
   geladenem Modell modell zu als Anfangsloesung fuer variablentyp SDV zu.
   
   Dazu wird fuer die in variablentyp gelistete Variable an jedem Knoten bzw.
   Element (je nach Typ) mit den Koordinaten zielkoordinaten die Anfangsloesungen aus zielwerte auf
   die Koordinaten der mdbknoten in der Assembly-Instanz namens mdbinstname übertragen. Da die
   Position der Knoten nicht uebereinstimmen muss, wird eine lineare Interpolation der zielwerte auf
   die Knoten des neuen Modells vorgenommen.

   Wenn variablentyp an Knoten definiert ist, wird zielkoordinaten als Knotenkoordinaten und
   zielwerte als Knotenwerte interpretiert und zugewiesen. Falls variablentyp an Elementen definiert
   ist, werden zielkoordinaten als Koordinaten der Elementmittelpunkte definiert und zielwerte als
   Elementwerte.
   
   Fuer eine Zustandszuweisung ohne zusaetzliche Transformation der Positionen (bspw. Verschiebung
   oder Rotation), ist es nicht noetig, mdbknoten zusaetzlich zu uebergeben. Andernfalls bietet sich
   eine Transformation der Koordinaten an (bspw. mit der Funktion Knotentransformation). Die
   aktualisierten mdbknoten muessen dann entsprechend uebergeben werden.
   
   Gibt [gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente] zurueck.
   
   Wichtig: Alle Elemente des parts muessen den gleichen Elementyp haben.
   """
   # FIXME: variablentyp erweitern zu (S, SVAVG, EVF, SDV)
   #
   from ctypes import c_double, c_int
   from hilfen import Log, BibliothekLaden
   #
   if (mdbknoten == []):
      mdbknoten = modell.rootAssembly.instances[mdbinstname].nodes;
   #
   # Lade die Bibliothek zur Bestimmung der Gewichtungen
   bibliothek = BibliothekLaden(dateiname='gewichtung');
   if (bibliothek is None):
      Log('# Abbruch: Externe Bibliothek gewichtung nicht gefunden');
      return [None, None, None];
   #
   cpp_gewichtung_bestimmen = bibliothek.Gewichtung_Bestimmen;
   #
   Log('# 1-3: Bereite Daten fuer Zustandszuweisung vor');
   #
   mdbelemente = modell.rootAssembly.instances[mdbinstname].elements;
   odbelemente = zielelemente;
   knoten_pro_mdbelement = len(mdbelemente[0].connectivity);
   knoten_pro_odbelement = len(odbelemente[0]);
   #
   mdb_dimensionen = 2;
   if ('3D' in str(mdbelemente[0].type)):
      mdb_dimensionen = 3;
   #
   odb_dimensionen = len(zielkoordinaten[0]);
   if (not (mdb_dimensionen == odb_dimensionen)):
      Log('# Abbruch: Zustandszuweisung nur 2D->2D oder 3D->3D moeglich, nicht gemischt');
      return [None, None, None];
   #
   #
   dimensionen = mdb_dimensionen;
   if (not _UebertragungGueltigeElementeCheck(dimensionen=dimensionen, ecken=knoten_pro_mdbelement)):
      Log('# Mdb-Elemente/Knoten in nicht unterstuetztem Format');
      return [None, None, None];
   #
   if (len(zielelemente) == len(zielwerte)):
      knotenweise = False;
   elif (len(zielkoordinaten) == len(zielwerte)):
      knotenweise = True;
   else:
      Log('# Abbruch: Anzahl Ergebnisse muss Anzahl Knoten oder Elementen entsprechen');
      return [None, None, None];
   #
   cpp_odbknoten, cpp_odbelemente, cpp_mdbknoten, cpp_mdbelemente = _ZustandsuebertragungDatenVorbereiten(dimensionen=dimensionen,
      odbknoten=zielkoordinaten, odbelemente=odbelemente, mdbknoten=mdbknoten, mdbelemente=mdbelemente,
      odbAbaqus=False);
   #
   # Rueckgabewerte ueber Pointer
   # Fuer die gewichtungen wird jedem Knoten des neuen Modells (mdb) das Element in der odb bestimmt,
   # in dem der Punkt liegt. Fuer jeden Knoten aus der odb, die dieses odb-Element definieren,
   # wird die Gewichtung bestimmt
   gewichtungKnotenLabels = [0 for idx in range(knoten_pro_odbelement*len(mdbknoten))];
   IntArray_gewKnotenLabels = c_int * len(gewichtungKnotenLabels);
   cpp_gewKnotenLabels = IntArray_gewKnotenLabels(*list(gewichtungKnotenLabels));
   #
   gewichtungKnotenWerte = [0.0 for idx in range(knoten_pro_odbelement*len(mdbknoten))];
   DoubleArray_gewKnotenWerte = c_double * len(gewichtungKnotenWerte);
   cpp_gewKnotenWerte = DoubleArray_gewKnotenWerte(*list(gewichtungKnotenWerte));
   #
   bezugsElemente = [0 for idx in range(len(mdbelemente))];
   IntArray_bezugsElemente = c_int * len(bezugsElemente);
   cpp_bezugsElemente = IntArray_bezugsElemente(*list(bezugsElemente));
   #
   # FIXME: Ordentlich unterscheiden
   sindEckpunkte = 1;
   #
   Log('# 2-3: Ermittle Gewichtungen');
   cpp_gewichtung_bestimmen(c_int(dimensionen), c_int(knoten_pro_odbelement),
      c_int(knoten_pro_mdbelement), cpp_odbknoten, c_int(len(odbelemente)), cpp_odbelemente,
      c_int(len(mdbknoten)), cpp_mdbknoten, c_int(len(mdbelemente)), cpp_mdbelemente,
      cpp_gewKnotenLabels, cpp_gewKnotenWerte, cpp_bezugsElemente);
   #
   # Wieder Listen aus den uebergebenen Pointern erzeugen
   gewichtungKnotenLabels = list(cpp_gewKnotenLabels);
   gewichtungKnotenWerte = list(cpp_gewKnotenWerte);
   bezugsElemente = list(cpp_bezugsElemente);
   #
   Log('# 3-3: Weise Werte zu'); 
   idx_naechstereintrag = _ErzeugeAbapysAnfangsbedingungenEintrag(modell=modell);
   #
   ausgabedatei, ausgabetext, odbergebnisse = _ZustandsuebertragungAusgabeVorbereiten(mdbname=modell.name,
      ausgabevariable=variablentyp, bezugsframe=None);
   if (any([ausgabedatei, ausgabetext]) is None):
      Log('# Abbruch: Zugriffsprobleme auf Datei oder ungueltige Ergebnisse');
      return [];
   #
   modell.keywordBlock.insert(idx_naechstereintrag, ausgabetext);
   _ZustandszuweisungErgebnisdateiSchreiben(ausgabedatei=ausgabedatei,
      ergebnisse=zielwerte, mdbinstname=mdbinstname, gewichtungKnotenLabels=gewichtungKnotenLabels,
      gewichtungKnotenWerte=gewichtungKnotenWerte, bezugsElemente=bezugsElemente,
      mdbknoten=mdbknoten, knoten_pro_mdbelement=knoten_pro_mdbelement, knotenweise=knotenweise);
   #
   return [gewichtungKnotenLabels, gewichtungKnotenWerte, bezugsElemente];
#
