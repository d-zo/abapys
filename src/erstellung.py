# -*- coding: utf-8 -*-
"""
erstellung.py   v0.8 (2020-09)
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
class PunktListe(object):
   """Mini-Klasse zur Erstellung von Paaren aus Koordinaten und Labels.
   """
   def __init__(self, coordinates, label):
      self.coordinates = coordinates;
      self.label = label;
   def __repr__(self):
      return 'PunktListe (abapys)';
#


# -------------------------------------------------------------------------------------------------
def NamePartInstance(modell, namensvorschlag):
   """Ermittle basierend auf namensvorschlag einen Namen fuer ein part/instance im uebergebenen
   modell, der eindeutig ist/noch nicht existiert. Dazu wird modell.parts mit <namensvorschlag> und
   modell.rootAssembly.instances mit inst<namensvorschlag> untersucht und namensvorschlag und ggs.
   mehreren Anpassungen davon ueberprueft. Gibt den (ggfs. angepassten) namensvorschlag zurueck.
   """
   name = namensvorschlag;
   nameGefunden = False;
   while (not nameGefunden):
      instname = 'inst' + name;
      if ((not modell.parts.has_key(name)) and (not modell.rootAssembly.instances.has_key(instname))):
         nameGefunden = True;
      else:
         name = name + 'x';
   #
   return name;
#


# -------------------------------------------------------------------------------------------------
def ReferenzpunktErstellenUndKoppeln(modell, punkt, name, flaeche):
   """In der rootAssembly von modell einen Referenzpunkt an den Koordinaten punkt erstellen, zu name
   umbenennen und mit der uebergebenen flaeche verknuepfen.
   """
   import assembly
   import interaction
   from abaqusConstants import ON, DISTRIBUTING, WHOLE_SURFACE, UNIFORM
   #
   modell.rootAssembly.ReferencePoint(point=punkt);
   modell.rootAssembly.features.changeKey(fromName='RP-1', toName='RP_' + name);
   #
   modell.rootAssembly.Set(name='setRP_' + name, referencePoints=(
      modell.rootAssembly.referencePoints[modell.rootAssembly.features['RP_' + name].id], ));
   #
   modell.Coupling(controlPoint=modell.rootAssembly.sets['setRP_' + name], couplingType=DISTRIBUTING,
      influenceRadius=WHOLE_SURFACE, localCsys=None, name='Couple_' + name, 
      surface=flaeche, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON, weightingMethod=UNIFORM);
#


# -------------------------------------------------------------------------------------------------
def _ConnectorErstellen(modell, verbindungstyp, name, punkt1, punkt2, kos):
   """Erzeuge im modell einen Connector name von punkt1 zu punkt2 mit dem Koordinatensystem kos. Je
   nach verbindungstyp werden gewisse Einschraenkungen der Freiheitsgrade - bezogen auf das
   uebergebene KOS (!) - fest zugewiesen:
   - 'TranslateConnector': Beim Axiallager ist nur eine Verschiebung entlang der x-Achse moeglich.
   - 'HingeConnector': Beim Drehscharnier ist nur eine Drehung um die x-Achse moeglich.
   """
   import section
   import assembly
   from abaqusConstants import TRANSLATOR, HINGE, IMPRINT
   from auswahl import BedingteAuswahl
   from hilfen import Log
   #
   if (verbindungstyp == 'TranslateConnector'):
      if (not modell.sections.has_key('TranslateConnector')):
         modell.ConnectorSection(assembledType=TRANSLATOR, name='TranslateConnector');
   #
   elif (verbindungstyp == 'HingeConnector'):
      if (not modell.sections.has_key('HingeConnector')):
         modell.ConnectorSection(assembledType=HINGE, name='HingeConnector');
   else:
      Log('# Warnung: Connector nicht implementiert');
   #
   modell.rootAssembly.WirePolyLine(mergeType=IMPRINT, meshable=False, points=((punkt1, punkt2), ));
   modell.rootAssembly.features.changeKey(fromName='Wire-1', toName=name);
   #
   KabelKanten = BedingteAuswahl(elemente=modell.rootAssembly.edges,
      bedingung='elem.featureName == \'' + name + '\'');
   modell.rootAssembly.Set(edges=KabelKanten, name='set' + name);
   #
   modell.rootAssembly.SectionAssignment(sectionName=verbindungstyp,
      region=modell.rootAssembly.sets['set' + name]);
   modell.rootAssembly.ConnectorOrientation(localCsys1=kos,
      region=modell.rootAssembly.sets['set' + name]);
#


# -------------------------------------------------------------------------------------------------
def AxiallagerErstellen(modell, name, punkt1, punkt2, kos):
   """Erzeuge im modell ein Axiallager name von punkt1 zu punkt2 mit dem Koordinatensystem kos. Beim
   Axiallager ist nur eine Verschiebung entlang der x-Achse des uebergebenen KOS moeglich.
   """
   _ConnectorErstellen(modell=modell, verbindungstyp='TranslateConnector', name=name,
      punkt1=punkt1, punkt2=punkt2, kos=kos);
#


# -------------------------------------------------------------------------------------------------
def DrehscharnierErstellen(modell, name, punkt1, punkt2, kos):
   """Erzeuge im modell ein Drehscharnier name von punkt1 zu punkt2 mit dem Koordinatensystem kos.
   Beim Drehscharnier ist nur eine Drehung um die x-Achse des uebergebenen KOS moeglich.
   """
   _ConnectorErstellen(modell=modell, verbindungstyp='HingeConnector', name=name,
      punkt1=punkt1, punkt2=punkt2, kos=kos);
#


# -------------------------------------------------------------------------------------------------
def Knotentransformation(punktliste, xneu='x', yneu='y', zneu='z'):
   """Erstelle eine neue Knotenliste basierend auf punktliste. Dabei werden von allen Eintraegen nur
   label und coordinates uebernommen. Die Koordinaten koennen ueber die Felder xneu, yneu und zneu
   transformiert werden.
   Gibt die transformierte punktliste zurueck.
   
   Fuer alle drei Variablen kann eine Transformationsanweisung wie bspw.
   "sqrt(x**2+y**2)" uebergeben werden, wobei jeweils die Variablen x, y und z zur Verfuegung
   stehen, die die Orignalwerte fuer jeden Knoten enthalten.
   
   Fuer mathematische Zusammenhaenge stehen die Funktionen pi, sqrt, sin, cos, tan, asin, acos, atan
   zur Verfuegung.
   
   WICHTIG: Wenn eine Zustandsuebertragung mit Knoten stattfinden soll, die in dieser Funktion
            transformiert worden sind, dann werden auch tatsaechlich nur die Knotenkoordinaten
            und keinerlei Werte modifiziert. Das gilt insbesondere fuer Drehungen wie im angegebenen
            Beispiel, bei dem Tensorergebnisse nicht gedreht, sondern nur an anderer Stelle
            ausgegeben werden.
   """
   from math import pi, sqrt, sin, cos, tan, asin, acos, atan
   from hilfen import Log, _Eval_Basispruefung
   #
   neue_knotenliste = []
   #
   if (any([(not _Eval_Basispruefung(code=bedingung, zusatz_erlaubt=['x', 'y', 'z'])) for bedingung in [xneu, yneu, zneu]])):
      Log('# Abbruch: Uebergebene xneu/yneu/zneu ungueltig');
      return;
   #
   for knoten in punktliste:
      x = knoten.coordinates[0];
      y = knoten.coordinates[1];
      z = knoten.coordinates[2];
      xmod = eval(xneu);
      ymod = eval(yneu);
      zmod = eval(zneu);
      #
      if (not (zneu is None)):
         neue_knotenliste += [PunktListe(coordinates=(xmod, ymod, zmod), label=knoten.label)];
      else:
         neue_knotenliste += [PunktListe(coordinates=(xmod, ymod), label=knoten.label)];
   #
   return neue_knotenliste;
#
