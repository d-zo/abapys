# -*- coding: utf-8 -*-
"""
auswahl.py   v0.3 (2020-09)
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
def BedingteAuswahl(elemente, bedingung='True', var=[]):
   """Erstelle eine Sequenz aller uebergebenen elemente, die bedingung erfuellen. Alle Variablen aus
   bedingung muessen global lesbar oder optional in var uebergeben und als var[...] bezeichnet sein,
   sonst kann die bedingung nicht korrekt ausgewertet werden. Gibt die Sequenz der ausgewaehlten
   Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element zugegriffen werden. Auf die
   Basiskoordinaten eines Elementes kann mit elem.pointOn[0][#] zugegriffen werden, wobei die Raute
   fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   
   Fuer mathematische Zusammenhaenge stehen die Funktionen pi, sqrt, sin, cos, tan, asin, acos, atan
   zur Verfuegung.
   """
   method = 'index';
   try:
      i = elemente[0].index
   except:
      method = 'label';
   #
   if (method == 'index'):
      return _BedingteAuswahlIndex(elemente=elemente, bedingung=bedingung, var=var);
   else:
      return _BedingteAuswahlLabel(elemente=elemente, bedingung=bedingung, var=var);
#


# -------------------------------------------------------------------------------------------------
def _BedingteAuswahlIndex(elemente, bedingung='True', var=[]):
   """Erstelle eine Sequenz aus den Indizes aller uebergebenen elemente, die bedingung erfuellen.
   Alle Variablen aus bedingung muessen global lesbar oder optional in var uebergeben und als
   var[...] bezeichnet sein, sonst kann die bedingung nicht korrekt ausgewertet werden.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element zugegriffen werden. Auf die
   Basiskoordinaten eines Elementes kann mit elem.pointOn[0][#] zugegriffen werden, wobei die Raute
   fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   """
   from math import pi, sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung
   #
   ausgewaehlteElemente = elemente[0:0];
   erlaubt = ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName', 'instanceNames',
      'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type', 'var', 'elem'];
   #
   if (not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=erlaubt)):
      Log('# Abbruch: Uebergebene bedingung ist ungueltig');
      return ausgewaehlteElemente;
   #
   for elem in elemente:
      if (eval(bedingung)):
         ausgewaehlteElemente += elemente[elem.index:elem.index+1];
   #
   return ausgewaehlteElemente;
#


# -------------------------------------------------------------------------------------------------
def _BedingteAuswahlLabel(elemente, bedingung='True', var=[]):
   """Erstelle eine Sequenz aus den Labels aller uebergebenen elemente, die bedingung erfuellen.
   Alle Variablen aus bedingung muessen global lesbar oder optional in var uebergeben und als
   var[...] bezeichnet sein, sonst kann die bedingung nicht korrekt ausgewertet werden.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element zugegriffen werden. Auf die
   Basiskoordinaten eines Elementes kann mit elem.coordinates[#] zugegriffen werden, wobei die Raute
   fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   """
   from math import pi, sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung
   #
   erlaubt = ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName', 'instanceNames',
      'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type', 'var', 'elem'];
   #
   if (not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=erlaubt)):
      Log('# Abbruch: Uebergebene bedingung ist ungueltig');
      return elemente[0:0];
   #
   ausgewaehlteLabels = [];
   for elem in elemente:
      if (eval(bedingung)):
         ausgewaehlteLabels += [elem.label];
   #
   return LabelAuswahl(elemente=elemente, labelliste=ausgewaehlteLabels);
#


# -------------------------------------------------------------------------------------------------
def ZweifachbedingteKantenAuswahl(elemente, bedingung1='True', bedingung2='True', bedingung3='True',
   var=[]):
   """Erstelle eine Sequenz aller Kanten aus elemente, die bedingung1 und bedingung2 erfuellen.
   Die Rueckgabe der Kanten ist sortiert nach bedingung3. Alle Variablen aus bedingung1, bedingung2
   und bedingung3 muessen global lesbar oder optional in var uebergeben und als var[...] bezeichnet
   sein, sonst koennen die Bedingungen nicht korrekt ausgewertet werden.
   
   In der ersten Bedingung kann mit edge auf eine einzelne Kante zugegriffen werden (bspw.
   edge.pointOn[0][#], wobei die Raute fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen
   steht). In der zweiten und dritten Bedingung kann zusaetzlich auch auf die beiden Endpunkte vert1
   sowie vert2 zugegriffen werden (ebenfalls vert.pointOn[0][#] mit Raute als 0, 1 oder 2).
   
   Die ersten beiden Bedingungen sind zur Auswahl der der Kanten. Kanten die eine der ersten beiden
   Bedingungen nicht erfuellen, werdne ignoriert. Die restlichen Kanten werden sortiert, abhaengig
   davon, ob sie die letzte Bedingung erfuellen oder nicht. Gibt eine Liste mit zwei Sequenzen der
   ausgewaehlten Kanten [kanten_bedingung3_True, kanten_bedingung3_False] zurueck.
   
   Fuer mathematische Zusammenhaenge stehen die Funktionen sqrt, sin, cos, tan, asin, acos, atan
   zur Verfuegung.
   """
   from math import sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung
   #
   kanten1 = elemente.edges[0:0];
   kanten2 = elemente.edges[0:0];
   #
   erlaubt = ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName', 'instanceNames',
      'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type', 'var', 'edge', 'vert1', 'vert2'];
   #
   if (any([(not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=erlaubt)) for bedingung in [bedingung1, bedingung2, bedingung3]])):
      Log('# Abbruch: Uebergebene bedingung1/bedingung2/bedingung3 ungueltig');
      return;
   #
   for edge in elemente.edges:
      if (eval(bedingung1)):
         vert1 = elemente.vertices[edge.getVertices()[0]];
         vert2 = elemente.vertices[edge.getVertices()[1]];
         if (eval(bedingung2)):
            if (eval(bedingung3)):
               kanten1 += elemente.edges[edge.index:edge.index+1];
            else:
               kanten2 += elemente.edges[edge.index:edge.index+1];
   #
   kanten = [kanten1, kanten2];
   return kanten;
#


# -------------------------------------------------------------------------------------------------
def LabelAuswahl(elemente, labelliste, elementhilfsliste=[]):
   """Erstelle eine Sequenz aller uebergebener elemente, deren Label sich in labelliste befindet.
   Optional kann eine elementhilfsliste vorab erzeugt und uebergeben werden, was vorallem bei
   mehrmaligen Aufrufen einer LabelAuswahl fuer gleiche elemente deutlich schneller ist.
   Falls keine elementhilfsliste uebergeben worden ist, wird (jedes mal) intern eine erstellt.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   """
   from hilfen import ErstelleLabelsortierteGeomlist
   #
   if (elementhilfsliste == []):
      elementhilfsliste = ErstelleLabelsortierteGeomlist(geomliste=elemente);
   #
   ausgewaehlteElemente = elemente[0:0];
   for label in labelliste:
      idxelem = elementhilfsliste[label];
      ausgewaehlteElemente += elemente[idxelem:idxelem+1];
   #
   return ausgewaehlteElemente;
#


# -------------------------------------------------------------------------------------------------
def ElementAuswahl(elemente, punktliste, bedingung='True', var=[], listenhilfe=[]):
   """Gib eine Sequenz an Elementen aus den uebergebenen elemente zurueck, die bzw. deren Punkte die
   bedingung erfuellen. Fuer die Zuordnung der einzelnen Punkte zu den Elementen muss eine
   punktliste uebergeben werden, die alle Punkte aller elemente enthaelt.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element und mit punkt auf einen Punkt des
   Elements zugegriffen werden. Die Koordinaten eines Punktes koennen mit punkt.coordinates[#]
   erhalten werden, wobei die Raute fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   
   Optional kann die korrekte Zuordnung der Labels der Punkte bei odb-elementen durch Uebergabe
   einer listenhilfe beschleunigt werden.
   
   Fuer mathematische Zusammenhaenge stehen die Funktionen pi, sqrt, sin, cos, tan, asin, acos, atan
   zur Verfuegung.
   
   WICHTIG: Wenn Elemente einer mdb statt einer odb untersucht werden sollen, sollte entweder keine
            oder die folgende listenhilfe uebergeben werden:
   
   listenhilfe = [idx for idx in range(len(punktliste))];
   """
   from hilfen import ElementAusOdb
   #
   if (ElementAusOdb(element=elemente[0])):
      return _OdbElementAuswahl(elemente=elemente, punktliste=punktliste, bedingung=bedingung,
         var=var, listenhilfe=listenhilfe);
   else:
      return _MdbElementAuswahl(elemente=elemente, punktliste=punktliste, bedingung=bedingung,
         var=var);
#


# -------------------------------------------------------------------------------------------------
def _MdbElementAuswahl(elemente, punktliste, bedingung='True', var=[]):
   """Gib eine Sequenz an Elementen aus den uebergebenen elemente zurueck, die bzw. deren Punkte die
   bedingung erfuellen (nur mdb). Fuer die Zuordnung der einzelnen Punkte zu den Elementen muss eine
   punktliste uebergeben werden, die alle Punkte aller elemente enthaelt.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element und mit punkt auf einen Punkt des
   Elements zugegriffen werden. Die Koordinaten eines Punktes koennen mit punkt.coordinates[#]
   erhalten werden, wobei die Raute fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   """
   from math import pi, sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung
   #
   ausgewaehlteElemente = elemente[0:0];
   erlaubt = ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName', 'instanceNames',
      'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type', 'var', 'elem', 'punkt'];
   #
   if (not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=erlaubt)):
      Log('# Abbruch: Uebergebene bedingung ist ungueltig');
      return ausgewaehlteElemente;
   #
   numPunkte = len(elemente[0].connectivity);
   for idx, elem in enumerate(elemente):
      numErfuellt = 0;
      for punktidx in elem.connectivity:
         punkt = punktliste[punktidx];
         if (eval(bedingung)):
            numErfuellt += 1;
      #
      if (numErfuellt == numPunkte):
         ausgewaehlteElemente += elemente[idx:idx+1];
   #
   return ausgewaehlteElemente;
#


# -------------------------------------------------------------------------------------------------
def _OdbElementAuswahl(elemente, punktliste, bedingung='True', var=[], listenhilfe=[]):
   """Gib eine Sequenz an Elementen aus den uebergebenen elemente zurueck, die bzw. deren Punkte die
   bedingung erfuellen (nur odb). Fuer die Zuordnung der einzelnen Punkte zu den Elementen muss eine
   punktliste uebergeben werden, die alle Punkte aller elemente enthaelt. Die korrekte Zuordnung der
   Labels der Punkte kann durch Uebergabe einer listenhilfe beschleunigt werden.
   Gibt die Sequenz der ausgewaehlten Elemente zurueck.
   
   In der Bedingung kann mit elem auf ein einzelnes Element und mit punkt auf einen Punkt des
   Elements zugegriffen werden. Die Koordinaten eines Punktes koennen mit punkt.coordinates[#]
   erhalten werden, wobei die Raute fuer 0, 1 oder 2 und somit eine der drei Bezugsrichtungen steht.
   """
   from math import pi, sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung, ErstelleLabelsortierteGeomlist
   #
   ausgewaehlteElemente = elemente[0:0];
   erlaubt = ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName', 'instanceNames',
      'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type', 'var', 'elem', 'punkt'];
   #
   if (not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=erlaubt)):
      Log('# Abbruch: Uebergebene bedingung ist ungueltig');
      return ausgewaehlteElemente;
   #
   if (listenhilfe == []):
      listenhilfe = ErstelleLabelsortierteGeomlist(geomliste=punktliste);
   #
   numPunkte = len(elemente[0].connectivity);
   for idx, elem in enumerate(elemente):
      numErfuellt = 0;
      for punktlabel in elem.connectivity:
         punkt = punktliste[listenhilfe[punktlabel]];
         if (eval(bedingung)):
            numErfuellt += 1;
         else:
            continue;
      #
      if (numErfuellt == numPunkte):
         ausgewaehlteElemente += elemente[idx:idx+1];
   #
   return ausgewaehlteElemente;
#


# -------------------------------------------------------------------------------------------------
def KnotenAuswahlLabelliste(knoten, sortierung=0, aufsteigend=True):
   """Sortiert alle uebergebenen knoten nach der Koordinatenrichtung sortierung basierend auf den
   jeweiligen Koordinaten.

   Fuer die sortierung ist die jeweilige Richtung (0, 1 oder 2) anzugeben. Die Reihenfolge wird
   ueber die Koordinaten der Mittelpunkte der Elemente bestimmt. Die Werte koennen entweder
   aufsteigend oder absteigend sortiert werden.
   """
   from operator import itemgetter
   #
   tempsortierung = sortierung;
   if ((not (sortierung == 0)) and (not (sortierung == 1)) and (not (sortierung == 2))):
      Log('# Warnung: Ungueltige sortierung, nehme sortierung = 0');
      tempsortierung = 0;
   #
   if (len(knoten) == 0):
      Log('# Hinweis: Keine Knoten uebergeben');
      return [];
   #
   templiste = [];
   for einzelpunkt in knoten:
      templiste += [(einzelpunkt.coordinates[tempsortierung], einzelpunkt.label), ];
   #
   templiste.sort(key=itemgetter(0));
   labelliste = [x[1] for x in templiste];
   if (aufsteigend):
      return labelliste;
   else:
      return list(reversed(labelliste));
#


# -------------------------------------------------------------------------------------------------
def ElementAuswahlLabelliste(elemente, punktliste, sortierung=0, aufsteigend=True,
   listenhilfe=[]):
   """Sortiert alle uebergebenen elemente nach der Koordinatenrichtung sortierung basierend auf den
   Koordinaten des Elementmittelpunktes. Fuer die Berechnung der Mittelpunktkoordinaten werden die
   Knoten der Elemente benutzt. Fuer die Zuordnung der einzelnen Punkte zu den Elementen muss eine
   punktliste uebergeben werden, die alle Punkte aller elemente enthaelt. Gibt eine Liste der Labels
   aller uebergebenen elemente zurueck, deren Mittelpunkte nach der Koordinatenrichtung sortierung
   sortiert ist.

   Fuer die sortierung ist die jeweilige Richtung (0, 1 oder 2) anzugeben. Die Reihenfolge wird
   ueber die Koordinaten der Mittelpunkte der Elemente bestimmt. Die Werte koennen entweder
   aufsteigend oder absteigend sortiert werden.
   
   Optional kann die korrekte Zuordnung der Labels der Punkte bei odb-elementen durch Uebergabe
   einer listenhilfe beschleunigt werden.
   
   WICHTIG: Wenn Elemente einer mdb statt einer odb untersucht werden sollen, sollte entweder keine
            oder die folgende listenhilfe uebergeben werden:
   
   listenhilfe = [idx for idx in range(len(punktliste))];
   """
   from operator import itemgetter
   from hilfen import Log, ElementAusOdb, ErstelleLabelsortierteGeomlist
   #
   tempsortierung = sortierung;
   if ((not (sortierung == 0)) and (not (sortierung == 1)) and (not (sortierung == 2))):
      Log('# Warnung: Ungueltige sortierung, nehme sortierung = 0');
      tempsortierung = 0;
   #
   if (len(elemente) == 0):
      Log('# Hinweis: Keine Elemente uebergeben');
      return [];
   #
   if (listenhilfe == []):
      if (ElementAusOdb(element=elemente[0])):
         listenhilfe = ErstelleLabelsortierteGeomlist(geomliste=punktliste);
      else:
         listenhilfe = [idx for idx in range(len(punktliste))];
   #
   templiste = [];
   anzahlpunkte = float(len(elemente[0].connectivity));
   for elem in elemente:
      mittelwert = 0;
      for punktlabel in elem.connectivity:
         punkt = punktliste[listenhilfe[punktlabel]];
         mittelwert = punkt.coordinates[tempsortierung]/anzahlpunkte;
      #
      templiste += [(mittelwert, elem.label), ];
   #
   templiste.sort(key=itemgetter(0));
   labelliste = [x[1] for x in templiste];
   if (aufsteigend):
      return labelliste;
   else:
      return list(reversed(labelliste));
#
