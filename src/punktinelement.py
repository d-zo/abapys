# -*- coding: utf-8 -*-
"""
punktinelement.py   v1.2 (2020-09)
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
def PunktInElement(elemente, knoten, referenzpunkt, listenhilfe=[], elementinfoliste=[]):
   """Gebe den Label des Elements aus elemente zurueck, das referenzpunkt enthaelt. Die
   Koordinaten der elemente muessen in knoten definiert sein. Die optionale Uebergabe einer
   Zuordnung listenhilfe von Labels zu Indizes beschleunigt den Vorgang. Falls eine elementinfoliste
   mit den Volumina und Punktkoordinaten aller Elemente verfuegbar ist, kann ebenfalls eine kleine
   Beschleunigung erzielt werden. Gibt zielElement zurueck.
   
   WICHTIG: Wenn Elemente einer mdb statt einer odb untersucht werden sollen, sollte entweder keine
            oder die folgende listenhilfe uebergeben werden:
   
   listenhilfe = [idx for idx in range(len(knoten))];
   """
   from hilfen import Log, ElementAusOdb, ErstelleLabelsortierteGeomlist
   #
   if (listenhilfe == []):
      if (ElementAusOdb(element=elemente[0])):
         listenhilfe = ErstelleLabelsortierteGeomlist(geomliste=knoten);
      else:
         listenhilfe = [idx for idx in range(len(knoten))];
   #
   zielElement = None;
   minverhaeltnis = 2.0;
   dimensionen = 2;
   if ('3D' in str(elemente[0].type)):
      dimensionen = 3;
   #
   if (elementinfoliste == []):
      for elem in elemente:
         punkte = PunktkoordinatenVonElement(element=elem, knoten=knoten, listenhilfe=listenhilfe);
         if (not _PunktMoeglicherweiseInElement(punkte=punkte, referenzpunkt=referenzpunkt,
            dimensionen=dimensionen)):
            continue;
         #
         volverhaeltnis = _PunktInnerhalbElement(punkte=punkte, referenzpunkt=referenzpunkt,
            dimensionen=dimensionen);
         if (volverhaeltnis < minverhaeltnis):
            zielElement = elem.label;
            minverhaeltnis = volverhaeltnis;
   else:
      if (not len(elemente) == len(elementinfoliste)):
         Log('# Abbruch: Anzahl Elemente stimmt nicht mit Eintraegen in Elementlist ueberein');
         return zielElement;
      for idx, elem in enumerate(elemente):
         if (not _PunktMoeglicherweiseInElement(punkte=elementinfoliste[idx][0],
            referenzpunkt=referenzpunkt, dimensionen=dimensionen)):
            continue;
         #
         referenzpunktvol = _ElementZuReferenzpunktVolumen(punkte=elementinfoliste[idx][0],
            referenzpunkt=referenzpunkt, dimensionen=dimensionen);
         volverhaeltnis = referenzpunktvol/elementinfoliste[idx][1];
         if (volverhaeltnis < minverhaeltnis):
            zielElement = elem.label;
            minverhaeltnis = volverhaeltnis;
   #
   return zielElement;
#


# -------------------------------------------------------------------------------------------------
def _PunktMoeglicherweiseInElement(punkte, referenzpunkt, dimensionen):
   """Ueberpruefe, ob referenzpunkt in allen Koordinatenrichtungen zwischen der kleinsten und
   groessten Koordinate aller uebergebenen punkte (Elementknoten) liegt. Eine erfolgreiche Ueber-
   pruefung ist notwendig (aber nicht hinreichend), dass der Punkt auch tatsaechlich im Element ist.
   Gibt Wahrheitswert ob Punkt moeglicherweise in Element ist zurueck.
   """
   knotenpunkte = len(punkte);
   #
   for richtung in range(dimensionen):
      # sum([list of boolean]) scheint in Abaqus nicht zu funktionieren, deshalb:
      sum_kleiner = [einzelpunkt[richtung] < referenzpunkt[richtung] for einzelpunkt in punkte].count(True);
      sum_groesser = [einzelpunkt[richtung] > referenzpunkt[richtung] for einzelpunkt in punkte].count(True);
      if ((sum_kleiner == knotenpunkte) or (sum_groesser == knotenpunkte)):
         return False;
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def KnotengewichtungInElement(element, referenzpunkt, knoten, label_zu_idx_punkte=[]):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Elements hat. Die Koordinaten der Elemente muessen in knoten definiert sein. Die optionale
   Uebergabe einer Zuordnung Listenhilfe von Labels zu Indizes beschleunigt den Vorgang.
   Gibt [labelsEckpunkte, Knotengewichtung] zurueck.
   
   WICHTIG: Wenn Elemente einer mdb statt einer odb untersucht werden sollen, sollte entweder keine
            oder die folgende label_zu_idx_punkte uebergeben werden:
   
   label_zu_idx_punkte = [idx for idx in range(len(knoten))];
   """
   from hilfen import ElementAusOdb, ErstelleLabelsortierteGeomlist
   #
   if (label_zu_idx_punkte == []):
      if (ElementAusOdb(element=element)):
         label_zu_idx_punkte = ErstelleLabelsortierteGeomlist(geomliste=knoten);
      else:
         label_zu_idx_punkte = [idx for idx in range(len(knoten))];
   #
   dimensionen = 2;
   if ('3D' in str(element.type)):
      dimensionen = 3;
   #
   punkte = PunktkoordinatenVonElement(element=element, knoten=knoten,
      listenhilfe=label_zu_idx_punkte);
   punktlabels = [knoten[label_zu_idx_punkte[einzelpunkt]].label for einzelpunkt in element.connectivity];
   return [punktlabels, KnotengewichtungPunktInPunktkoordinaten(punkte=punkte,
      referenzpunkt=referenzpunkt, dimensionen=dimensionen)];
#

   
# -------------------------------------------------------------------------------------------------
def KnotengewichtungPunktInPunktkoordinaten(punkte, referenzpunkt, dimensionen):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Elements hat. Abhaengig von dimensionen wird eine Flaeche (2D) oder ein Volumen (3D) als Referenz
   betrachtet. Gibt gewichtung zurueck.
   
   WICHTIG: punkte muss unabhaengig von dimensionen drei Koordinaten fuer jeden Punkt enthalten.
   """
   from hilfen import Log
   #
   nichtUnterstuetzt = False;
   gewichtung = [];
   knotenpunkte = len(punkte);
   #
   # WICHTIG: Die selbe Art der Ueberpruefung auch in den Funktionen ElementVolumen und
   #          _ElementZuReferenzpunktVolumen anpassen!
   nichtUnterstuetzt = False;
   if (dimensionen == 2):
      punkte2D = [einzelpunkt[0:2] for einzelpunkt in punkte];
      referenzpunkt2D = referenzpunkt[0:2];
      if (knotenpunkte == 3):
         # C3 - Dreieck
         gewichtung = _KnotengewichtungPunktInDreieck(punkte=punkte2D, referenzpunkt=referenzpunkt2D);
      elif (knotenpunkte == 4):
         # C4 - Viereck
         gewichtung = _KnotengewichtungPunktInViereck(punkte=punkte2D, referenzpunkt=referenzpunkt2D);
      else:
         nichtUnterstuetzt = True;
   elif (dimensionen == 3):
      if (knotenpunkte == 4):
         # C3D4 - Tetraeder
         gewichtung = _KnotengewichtungPunktInTetraeder(punkte=punkte, referenzpunkt=referenzpunkt);
      elif (knotenpunkte == 8):
         # C3D8 - Hexaeder
         gewichtung = _KnotengewichtungPunktInHexaeder(punkte=punkte, referenzpunkt=referenzpunkt);
      else:
         nichtUnterstuetzt = True;
   else:
      nichtUnterstuetzt = True;
   #
   if (nichtUnterstuetzt):
      Log('Elementtyp zur Bestimmung der Gewichtung nicht unterstuetzt C' + str(dimensionen) + 'D' +
          str(knotenpunkte));
   #
   return gewichtung;
#

   
# -------------------------------------------------------------------------------------------------   
def _KnotengewichtungPunktInHexaeder(punkte, referenzpunkt):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Hexaeders hat. Die Reihenfolge der Knoten muss so sein, wie in dem Hilfstext von ElementVolumen
   beschrieben ist. Gibt gewichtung zurueck.
   """
   gewichtung = [0.0 for x in punkte];
   # Wenn das mit Tetraeder bearbeitet werden soll, bietet es sich an, Stuetzpunkte an den
   # Flaechenmitten und der Elementmitte hinzuzufuegen (sonst gibt es Probleme mit Gewichtungen bei
   # anderer Knotenwahl).
   idx_seitenmitten = [[0, 1, 2, 3], [0, 1, 4, 5], [0, 3, 4, 7], [1, 2, 5, 6], [2, 3, 6, 7], [4, 5, 6, 7]];
   #
   punkt_mitte = [sum([punkte[idx][0] for idx in range(8)])/8.0,
                  sum([punkte[idx][1] for idx in range(8)])/8.0,
                  sum([punkte[idx][2] for idx in range(8)])/8.0];
   #
   punkte_seiten = [];
   basisgewichtung = [];
   for liste_idx_seite in idx_seitenmitten:
      punkte_seiten += [[sum([punkte[idx][0] for idx in liste_idx_seite])/4.0,
                        sum([punkte[idx][1] for idx in liste_idx_seite])/4.0,
                        sum([punkte[idx][2] for idx in liste_idx_seite])/4.0]];
      basisgewichtung += [[0 for idx in range(8)]];
      for idx_gewicht in liste_idx_seite:
         basisgewichtung[-1][idx_gewicht] = 1;
   #
   punkte_neu = punkte + [punkt_mitte] + punkte_seiten;
   #
   # Fuer alle 24 Tetraeder pruefen, ob der Punkt darin liegt, und wenn ja, die richtigen Gewichte
   # zurueckgeben.
   tetraeder_kombinationen = [
      [0, 1, 8, 9], [0, 1, 8, 10], [0, 3, 8, 9], [0, 3, 8, 11], [0, 4, 8, 10], [0, 4, 8, 11],
      [1, 2, 8, 9], [1, 2, 8, 12], [1, 5, 8, 10], [1, 5, 8, 12], [2, 3, 8, 9], [2, 3, 8, 13],
      [2, 6, 8, 12], [2, 6, 8, 13], [3, 7, 8, 11], [3, 7, 8, 13], [4, 5, 8, 10], [4, 5, 8, 14],
      [4, 7, 8, 11], [4, 7, 8, 14], [5, 6, 8, 12], [5, 6, 8, 14],[6, 7, 8, 13], [6, 7, 8, 14]];
   for liste_idx_kombination in tetraeder_kombinationen:
      punkteauswahl = [punkte_neu[idx] for idx in liste_idx_kombination];
      tetraeder_gewichte = _KnotengewichtungPunktInTetraeder(punkte=punkteauswahl,
         referenzpunkt=referenzpunkt);
      if (any(temp_gewicht < 0.0 for temp_gewicht in tetraeder_gewichte)):
         continue;
      #
      gewichtung[liste_idx_kombination[0]] = tetraeder_gewichte[0];
      gewichtung[liste_idx_kombination[1]] = tetraeder_gewichte[1];
      for idx in range(8):
         gewichtung[idx] += 0.125*tetraeder_gewichte[2] + \
            0.25*tetraeder_gewichte[3]*basisgewichtung[liste_idx_kombination[3]-9][idx];
      #
      break;
   #
   return gewichtung;
#


# -------------------------------------------------------------------------------------------------
def _KnotengewichtungPunktInTetraeder(punkte, referenzpunkt):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Tetraeders hat. Dabei wird ein linearer Ansatz verwendet. Falls einer der Rueckgabewerte kleiner
   als Null ist, liegt der Referenzpunkt nicht im durch punkte definierten Tetraeder.
   Gibt gewichtung zurueck.
   """
   # Aktuelle Implementierung basierend auf der 3D-Punktgleichung
   # (referenzpunkt-p0) = (p1-p0)*r + (p2-p1)*s + (p3-p1)*t
   Rx, Ry, Rz = [a-b for a, b in zip(referenzpunkt, punkte[0])];
   X1, Y1, Z1 = [a-b for a, b in zip(punkte[1], punkte[0])];
   X2, Y2, Z2 = [a-b for a, b in zip(punkte[2], punkte[1])];
   X3, Y3, Z3 = [a-b for a, b in zip(punkte[3], punkte[1])];
   #
   det_gesamt = X1*(Y2*Z3-Y3*Z2) - X2*(Y1*Z3-Y3*Z1) + X3*(Y1*Z2-Y2*Z1);
   # Berechnung kann nur sinnvoll fortgesetzt werden, wenn sich die Determinante von Null unterscheidet
   if (abs(det_gesamt) <= 0.0000001):
      return [-1.0, -1.0, -1.0, -1.0];
   #
   # Die drei Gleichungen koennen als Matrix zusammengefasst werden. Die Parameter r, s und t
   # koennen durch Invertieren der Matrix bestimmt werden.
   #   Rx     X1, X2, X3     r
   #   Ry  =  Y1, Y2, Y3  *  s
   #   Ry     Z1, Z2, Z3     t
   r = ( Rx*(Y2*Z3-Y3*Z2) - Ry*(X2*Z3-X3*Z2) + Rz*(X2*Y3-X3*Y2))/det_gesamt;
   s = (-Rx*(Y1*Z3-Y3*Z1) + Ry*(X1*Z3-X3*Z1) - Rz*(X1*Y3-X3*Y1))/det_gesamt;
   t = ( Rx*(Y1*Z2-Y2*Z1) - Ry*(X1*Z2-X2*Z1) + Rz*(X1*Y2-X2*Y1))/det_gesamt;
   #
   # Jetzt koennen r, s und t in die gesuchten Gewichtungen umgerechnet werden.
   #       w1     w2     w3     w4
   return [1-r,   r-s-t, s,     t];
#


# -------------------------------------------------------------------------------------------------
def _KnotengewichtungPunktInViereck(punkte, referenzpunkt):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Viereck hat. Die Reihenfolge der Knoten muss so sein, wie in dem Hilfstext von ElementVolumen
   beschrieben ist (alle im oder alle gegen den Uhrzeigersinn definiert). Gibt gewichtung zurueck.
   """
   gewichtung = [0.0 for x in punkte];
   # Wenn das mit Dreiecken bearbeitet werden soll, bietet es sich an, einen Stuetzpunkte in der
   # Elementmitte hinzuzufuegen (sonst gibt es Probleme mit Gewichtungen bei anderer Knotenwahl).
   punkt_mitte = [sum([punkte[idx][0] for idx in range(4)])/4.0,
                  sum([punkte[idx][1] for idx in range(4)])/4.0];
   #
   punkte_neu = punkte + [punkt_mitte];
   #
   # Fuer alle 4 Dreiecke pruefen, ob der Punkt darin liegt, und wenn ja, die richtigen Gewichte
   # zurueckgeben.
   dreieck_kombinationen = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]];
   for liste_idx_kombination in tetraeder_kombinationen:
      punkteauswahl = [punkte_neu[idx] for idx in liste_idx_kombination];
      dreieck_gewichte = _KnotengewichtungPunktInDreieck(punkte=punkteauswahl,
         referenzpunkt=referenzpunkt);
      if (any(temp_gewicht < 0.0 for temp_gewicht in tetraeder_gewichte)):
         continue;
      #
      gewichtung[liste_idx_kombination[0]] = tetraeder_gewichte[0];
      gewichtung[liste_idx_kombination[1]] = tetraeder_gewichte[1];
      for idx in range(4):
         gewichtung[idx] += 0.25*tetraeder_gewichte[2];
      #
      break;
   #
   return gewichtung;
#


# -------------------------------------------------------------------------------------------------
def _KnotengewichtungPunktInDreieck(punkte, referenzpunkt):
   """Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in punkte definierten
   Dreiecks hat. Dabei wird ein linearer Ansatz verwendet. Falls einer der Rueckgabewerte kleiner
   als Null ist, liegt der Referenzpunkt nicht im durch punkte definierten Dreieck.
   Gibt gewichtung zurueck.
   """
   # Aktuelle Implementierung basierend auf der 2D-Punktgleichung
   # (referenzpunkt-p0) = (p1-p0)*s + (p2-p0)*t
   Rx, Ry = [a-b for a, b in zip(referenzpunkt, punkte[0])];
   X1, Y1 = [a-b for a, b in zip(punkte[1], punkte[0])];
   X2, Y2 = [a-b for a, b in zip(punkte[2], punkte[0])];
   #
   det_gesamt = X1*Y2 - X2*Y1;
   # Berechnung kann nur sinnvoll fortgesetzt werden, wenn sich die Determinante von Null unterscheidet
   if (abs(det_gesamt) <= 0.0000001):
      return [-1.0, -1.0, -1.0, -1.0];
   #
   # Die zwei Gleichungen koennen als Matrix zusammengefasst werden. Die Parameter s und t
   # koennen durch Invertieren der Matrix bestimmt werden.
   #   Rx     X1, X2     s
   #   Ry  =  Y1, Y2  *  t
   s = ( Rx*Y2 - Ry*X2)/det_gesamt;
   t = (-Rx*Y1 + Ry*X1)/det_gesamt;
   #
   # Jetzt koennen s und t in die gesuchten Gewichtungen umgerechnet werden.
   #       w1     w2     w3
   return [1-s-t, s,     t];
#


# -------------------------------------------------------------------------------------------------
def ElementInfolisteErstellen(elemente, knoten, listenhilfe=[]):
   """Erstelle eine Hilfsliste mit Punktkoordinaten und Volumina aller uebergebenen elemente. Dazu
   wird neben elemente eine Liste aller Punktkoordinaten (knoten) benoetigt. Die optionale
   Uebergabe einer Zuordnung listenhilfe von Labels zu Indizes beschleunigt den Vorgang.
   Gibt elementinfoliste zurueck.
   
   WICHTIG: Wenn Elemente einer mdb statt einer odb untersucht werden sollen, sollte entweder keine
            oder die folgende listenhilfe uebergeben werden:
   
   listenhilfe = [idx for idx in range(len(knoten))];
   """
   from hilfen import ElementAusOdb, ErstelleLabelsortierteGeomlist
   #
   if (listenhilfe == []):
      if (ElementAusOdb(element=elemente[0])):
         listenhilfe = ErstelleLabelsortierteGeomlist(geomliste=knoten);
      else:
         listenhilfe = [idx for idx in range(len(knoten))];
   #
   elementinfoliste = [];
   dimensionen = 2;
   if ('3D' in str(elemente[0].type)):
      dimensionen = 3;
   #
   for idx, elem in enumerate(elemente):
      punkte = PunktkoordinatenVonElement(element=elem, knoten=knoten, listenhilfe=listenhilfe);
      elementinfoliste += [[punkte, ElementVolumen(punkte=punkte, dimensionen=dimensionen)]];
   #
   return elementinfoliste;
#


# -------------------------------------------------------------------------------------------------
def _TetraederVolumen(punkt1, punkt2, punkt3, punkt4):
   """Berechnet das durch die vier Koordinaten punkt1 bis punkt4 definierte Volumen eines Tetraeders.
   Gibt das Volumen zurueck.
   """
   a = [punkt1[0] - punkt4[0], punkt1[1] - punkt4[1], punkt1[2] - punkt4[2]];
   b = [punkt2[0] - punkt4[0], punkt2[1] - punkt4[1], punkt2[2] - punkt4[2]];
   c = [punkt3[0] - punkt4[0], punkt3[1] - punkt4[1], punkt3[2] - punkt4[2]];
   svol = abs(c[0]*(a[1]*b[2]-a[2]*b[1]) + c[1]*(a[2]*b[0]-a[0]*b[2]) + c[2]*(a[0]*b[1]-a[1]*b[0]));
   return svol/6.0;
#


# -------------------------------------------------------------------------------------------------
def _PunktInnerhalbTetraeder(punkte, referenzpunkt):
   """Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Tetraeders liegt, das durch die
   uebergebenen Punkte definiert wird, werden zwei Volumina berechnet und verglichen: Zum einen wird
   das Volumen des Elements ueber die vier Punkte bestimmt. Zum anderen wird das Volumen aller
   Seiten des Elements als Pyramiden mit dem referenzpunkt als Spitze bestimmt. Ist das Volumen mit
   dem Referenzpunkt groesser, so liegt der Punkt ausserhalb des Elements.
   Gibt das verhaeltnis der Volumina zurueck (1 -> innerhalb, >1 -> ausserhalb).
   """
   elemvol = _TetraederVolumen(punkt1=punkte[0], punkt2=punkte[1], punkt3=punkte[2], punkt4=punkte[3]);
   referenzpunktvol = _TetraederZuReferenzpunktVolumen(punkte=punkte, referenzpunkt=referenzpunkt);
   return referenzpunktvol/elemvol;
#


# -------------------------------------------------------------------------------------------------
def ElementVolumen(punkte, dimensionen):
   """Berechnet das Referenzvolumen eines 3D-Elements oder die Referenzflaeche eines 2D-Elements,
   abhaengig davon ob dimensionen 2 oder 3 ist. Unterstuetzt werden Hexaeder, Tetraeder (3D) sowie
   Vierecke und Dreiecke (2D). Fuer die korrekte Berechnung muessen die Knoten von Hexaeder und
   Viereck-Elements in der dargestellen Reihenfolge gespeichert sein (was Abaqus standardmaessig
   tun sollte):
   
   7 __________  6          #
     \         \            #   3  ____________  0
     |\        .\           #     |            |
     | \       . \          #     |            |
     |4 \_________\ 5       #     |            |
     |  |      .  |         #     |            |
   3 |..|....... 2|         #     |            |
     \  |       . |         #     |            |
      \ |        .|         #     |____________|
       \|_________|         #   2                1
      0             1       #
      
   Gibt das Volumen eines Elements zurueck.
   """
   from hilfen import Log
   #
   vol = 0;
   knotenpunkte = len(punkte);
   #
   # WICHTIG: Die selbe Art der Ueberpruefung auch in den Funktionen _ElementZuReferenzpunktVolumen
   #          und KnotengewichtungPunktInPunktkoordinaten anpassen!
   nichtUnterstuetzt = False;
   if (dimensionen == 2):
      punkte2D = [einzelpunkt[0:2] for einzelpunkt in punkte];
      if (knotenpunkte == 3):
         # C3 - Dreieck
         vol = _DreieckFlaeche(punkt1=punkte2D[0], punkt2=punkte2D[1], punkt3=punkte2D[2]);
      elif (knotenpunkte == 4):
         # C4 - Viereck
         vol = _ViereckFlaeche(punkte=punkte2D);
      else:
         nichtUnterstuetzt = True;
   elif (dimensionen == 3):
      if (knotenpunkte == 4):
         # C3D4 - Tetraeder
         vol = _TetraederVolumen(punkt1=punkte[0], punkt2=punkte[1], punkt3=punkte[2], punkt4=punkte[3]);
      elif (knotenpunkte == 8):
         # C3D8 - Hexaeder
         vol = _HexaederVolumen(punkte=punkte);
      else:
         nichtUnterstuetzt = True;
   else:
      nichtUnterstuetzt = True;
   #
   if (nichtUnterstuetzt):
      Log('Elementtyp zur Bestimmung des Volumens nicht unterstuetzt C' + str(dimensionen) + 'D' +
          str(knotenpunkte));
   #
   return vol;
#


# -------------------------------------------------------------------------------------------------
def _HexaederVolumen(punkte):
   """Berechnet das Referenzvolumen eines Hexaeders, indem es die Volumina aller beteiligten
   Tetraeder berechnet. Dazu muessen die Knoten eines Elements in der dargestellen Reihenfolge
   gespeichert sein (was Abaqus standardmaessig tun sollte):
   
   7 __________  6          #
     \         \            #
     |\        .\           #
     | \       . \          #
     |4 \_________\ 5       #
     |  |      .  |         #
   3 |..|....... 2|         #
     \  |       . |         #
      \ |        .|         #
       \|_________|         #
      0             1       #
      
   Gibt das Volumen eines Hexaeders zurueck.
   """
   tetraeder_punktliste = [[0, 1, 2, 5], [0, 2, 3, 7], [0, 4, 5, 7], [0, 2, 5, 7], [2, 5, 6, 7]];
   vol = 0;
   for tetra_index in tetraeder_punktliste:
      punkt1, punkt2, punkt3, punkt4 = [punkte[index] for index in tetra_index];
      vol += _TetraederVolumen(punkt1=punkt1, punkt2=punkt2, punkt3=punkt3, punkt4=punkt4);
   #
   return vol;
#


# -------------------------------------------------------------------------------------------------
def _DreieckFlaeche(punkt1, punkt2, punkt3):
   """Bestimme die Flaeche eines Dreiecks anhand der Koordinaten (2D) der drei Eckpunkte.
   Gibt die Flaeche des Dreiecks zuruck.
   """
   # Wenn das Dreieck als ein Punkt und zwei aufspannende Verbindungsvektoren angenommen wird,
   # dann ist das Kreuzprodukt Verbindungsvektoren die Fläche das Parallelogramm und somit die
   # doppelte Flaeche des Dreiecks.
   X1, Y1 = [a-b for a, b in zip(punkt2, punkt1)];
   X2, Y2 = [a-b for a, b in zip(punkt3, punkt1)];
   #
   return 0.5*(X1*Y2 - X2*Y1);
#


# -------------------------------------------------------------------------------------------------
def _ViereckFlaeche(punkte):
   """Bestimme die Flaeche eines Vierecks anhand der Koordinaten (2D) der vier Eckpunkte. Dazu
   muessen die Knoten eines Elements in der dargestellen Reihenfolge gespeichert sein (was Abaqus
   standardmaessig tun sollte):
   

   3  ____________  0       #
     |            |         #
     |            |         #
     |            |         #
     |            |         #
     |            |         #
     |            |         #
     |____________|         #
   2                1       #
   
   Gibt die Flaeche des Vierecks zurueck.
   """
   dreieck_punktliste = [[0, 1, 2], [0, 2, 3]];
   flaeche = 0;
   for dreieck_index in dreieck_punktliste:
      punkt1, punkt2, punkt3 = [punkte[index] for index in dreieck_index];
      flaeche += _DreieckFlaeche(punkt1=punkt1, punkt2=punkt2, punkt3=punkt3);
   #
   return flaeche;
#


# -------------------------------------------------------------------------------------------------
def _ElementZuReferenzpunktVolumen(punkte, referenzpunkt, dimensionen):
   """Bestimme das Volumen (3D) bzw. die Flaeche (2D), das durch die punkte eines Elements mit einem
   referenzpunkt definiert wird (abhaengig von dimensionen). Gibt das Volumen mit Referenzpunkt als
   Teil des Elements zurueck.
   """
   from hilfen import Log
   #
   vol = 0;
   knotenpunkte = len(punkte);
   #
   # WICHTIG: Die selbe Art der Ueberpruefung auch in den Funktionen _ElementZuReferenzpunktVolumen
   #          und KnotengewichtungPunktInPunktkoordinaten anpassen!
   nichtUnterstuetzt = False;
   if (dimensionen == 2):
      punkte2D = [einzelpunkt[0:2] for einzelpunkt in punkte];
      referenzpunkt2D = referenzpunkt[0:2];
      if (knotenpunkte == 3):
         # C3 - Dreieck
         vol = _XeckZuReferenzpunktFlaeche(punkte=punkte2D, referenzpunkt=referenzpunkt2D, ecken=3);
      elif (knotenpunkte == 4):
         # C4 - Viereck
         vol = _XeckZuReferenzpunktFlaeche(punkte=punkte2D, referenzpunkt=referenzpunkt2D, ecken=4);
      else:
         nichtUnterstuetzt = True;
   elif (dimensionen == 3):
      if (knotenpunkte == 4):
         # C3D4 - Tetraeder
         vol = _TetraederZuReferenzpunktVolumen(punkte=punkte, referenzpunkt=referenzpunkt);
      elif (knotenpunkte == 8):
         # C3D8 - Hexaeder
         vol = _HexaederZuReferenzpunktVolumen(punkte=punkte, referenzpunkt=referenzpunkt);
      else:
         nichtUnterstuetzt = True;
   else:
      nichtUnterstuetzt = True;
   #
   if (nichtUnterstuetzt):
      Log('Elementtyp zur Bestimmung des ReferenzVolumens nicht unterstuetzt C' + str(dimensionen) +
          'D' + str(knotenpunkte));
   #
   return vol;
#


# -------------------------------------------------------------------------------------------------
def _HexaederZuReferenzpunktVolumen(punkte, referenzpunkt):
   """Berechnet anhand der uebergebenen punkte das Volumen aller Tetraederseiten mit referenzpunkt
   als Spitze der Tetraeder. Die Reihenfolge der Knoten muss so sein, wie in dem Hilfstext von
   ElementVolumen beschrieben wird. Gibt das Volumen mit Referenzpunkt als Teil des Elements zurueck.
   """
   tetraeder_basispunktliste = [[0, 1, 2], [0, 1, 5], [0, 2, 3], [0, 3, 7], [0, 4, 5], [0, 4, 7],
                                [1, 2, 5], [2, 3, 7], [2, 5, 6], [2, 6, 7], [4, 5, 7], [5, 6, 7]];
   vol = 0;
   for tetra_index in tetraeder_basispunktliste:
      punkt1, punkt2, punkt3 = [punkte[index] for index in tetra_index];
      vol += _TetraederVolumen(punkt1=punkt1, punkt2=punkt2, punkt3=punkt3, punkt4=referenzpunkt);
   #
   return vol;
#


# -------------------------------------------------------------------------------------------------
def _TetraederZuReferenzpunktVolumen(punkte, referenzpunkt):
   """Berechnet anhand der uebergebenen punkte das Volumen aller Seiten mit referenzpunkt als Spitze
   eines Tetraeders. Gibt das Volumen mit Referenzpunkt als Teil des Elements zurueck.
   """
   tetraeder_basispunktliste = [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]];
   vol = 0;
   for tetra_index in tetraeder_basispunktliste:
      punkt1, punkt2, punkt3 = [punkte[index] for index in tetra_index];
      vol += _TetraederVolumen(punkt1=punkt1, punkt2=punkt2, punkt3=punkt3, punkt4=referenzpunkt);
   #
   return vol;
#


# -------------------------------------------------------------------------------------------------
def _XeckZuReferenzpunktFlaeche(punkte, referenzpunkt, ecken):
   """Berechnet anhand der uebergebenen punkte die Flaeche aller Seiten mit referenzpunkt
   als Spitze eines Dreiecks. Die Reihenfolge der Knoten muss so gewaehlt sein, dass sie auch
   tatsaechlich benachbarte Knoten sind. Gibt die Flaeche mit Referenzpunkt als Teil des Elements
   zurueck.
   """
   xeck_basispunkte = [(punkt_idx, punkt_idx+1) for punkt_idx in range(ecken-1)] + [(ecken-1, 0)];
   flaeche = 0;
   for xeck_index in xeck_basispunkte:
      punkt1, punkt2 = [punkte[index] for index in xeck_index];
      flaeche += _DreieckFlaeche(punkt1=punkt1, punkt2=punkt2, punkt3=referenzpunkt);
   #
   return flaeche;
#


# -------------------------------------------------------------------------------------------------
def _PunktInnerhalbElement(punkte, referenzpunkt, dimensionen):
   """Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Elements liegt, das durch die
   uebergebenen Punkte definiert wird, werden abhaengig von dimensionen zwei Flaechen (2D) oder
   zwei Volumina (3D) berechnet und verglichen: Zum einen wird die Berechnung mit den Eckpunkten
   des Elements durchgefuehrt, zum anderen mit dem uebergebenene referenzpunkt. Nur wenn der
   referenzpunkt nicht ausserhalb des Elements ist, sind die Flaechen bzw. Volumina gleich gross.
   Gibt das verhaeltnis der Volumina zurueck (1 -> innerhalb, >1 -> ausserhalb).
   
   Folgende Varianten werden unterstuetzt:
   - dimensionen == 2 -> Flaechenberechnung mit Dreiecken (3 punkte) oder Vierecken (4 punkte)
   - dimensionen == 3 -> Volumenberechnung mit Tetraedern (4 punkte) oder Hexaedern (8 punkte)
   """
   elemvol = ElementVolumen(punkte=punkte, dimensionen=dimensionen);
   referenzpunktvol = _ElementZuReferenzpunktVolumen(punkte=punkte, referenzpunkt=referenzpunkt,
      dimensionen=dimensionen);
   return referenzpunktvol/elemvol;
#


# -------------------------------------------------------------------------------------------------
def PunktkoordinatenVonElement(element, knoten, listenhilfe):
   """Bestimme eine Liste mit den Punktkoordinaten, die die Ecken von element sind. Dazu werden alle
   knoten mit den Koordinaten der Punkte und eine listenhilfe zur Zuordnung von Labels und Indizes
   benoetigt. Gibt die Koordinaten aller Punkte von element zurueck.
   """
   koordinaten = [];
   for einzelpunkt in element.connectivity:
      koordinaten += [knoten[listenhilfe[einzelpunkt]].coordinates];
   #
   return koordinaten;
#


# -------------------------------------------------------------------------------------------------
def PartVolumen(part):
   """Bestimme das Volumen (3D) bzw. die Flaeche (2D) eines gemeshten part. Gibt das Volumen zurueck.
   
   Wichtig: Alle Elemente des parts muessen den gleichen Elementyp haben.
   """
   dimensionen = 2;
   if ('3D' in str(part.elements[0].type)):
      dimensionen = 3;
   #
   elemvol = 0;
   for elem in part.elements:
      punkte = [];
      # Fuer parts muessen die Indizes statt label betrachtet werden
      for punktidx in elem.connectivity:
         punkte += [part.nodes[punktidx].coordinates];
      #
      elemvol += ElementVolumen(punkte=punkte, dimensionen=dimensionen);
   #
   return elemvol;
#
