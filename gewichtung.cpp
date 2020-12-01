// gewichtung.cpp   v0.4 (2020-09)

// Copyright 2020 Dominik Zobel.
// All rights reserved.
// 
// This file is part of the abapys library.
// abapys is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// abapys is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with abapys. If not, see <http://www.gnu.org/licenses/>.

#include <iostream>
#include <vector>
#include <cmath>


#ifdef _WIN32
#define ADDAPI __declspec(dllexport)
#define ADDCALL __cdecl
// oder ADDCALL __stdcall ?
#else
#ifdef __MINGW32__
#define ADDAPI __declspec(dllexport)
#define ADDCALL __cdecl
#else
#define ADDAPI
#define ADDCALL
#endif
#endif


extern "C" ADDAPI void ADDCALL Gewichtung_Bestimmen(const int dimensionen, const int eckenAlt,
   const int eckenNeu, const double* knotenKoordinatenAlt, int numElementeAlt,
   const int* elementeEckenAlt, int numKnotenNeu, const double* knotenKoordinatenNeu,
   int numElementeNeu, int* const elementeEckenNeu, int* gewichtungKnotenLabels,
   double* gewichtungKnotenWerte, int* bezugsElement);


bool PunktMoeglicherweiseInElement(std::vector<double> punkte, std::vector<double> referenzpunkt,
   const int dimensionen, const int ecken) {
   // Ueberpruefe, ob der Punkt zwischen x-, y- und z-Koordinaten aller Elementknoten liegt.
   // (Notwendige aber nicht hinreichende Bedingung, dass der Punkt auch tatsaechlich im Element ist).
   // Der erste Array enthaelt dimensionen*ecken Werte, bspw. fuer ein Hexaeder
   // [P0x, P0y, P0z, P1x, P1y, P1z, ..., P7x, P7y, P7z]
   // und der zweite Array dimensionen Werte, bspw. fuer drei Achsen [Rx, Ry, Rz]
   int idxPosition = 0;
   for (int idx_richtung = 0; idx_richtung < dimensionen; idx_richtung++) {
      int sum_kleiner = 0;
      int sum_groesser = 0;
      for (int idx_eckpunkt = 0; idx_eckpunkt < ecken; idx_eckpunkt++) {
         idxPosition = dimensionen*idx_eckpunkt+idx_richtung;
         // Ueberpruefe echt groesser und echt kleiner, da Gleichheit noch in Ordnung ist
         if (punkte[idxPosition] < referenzpunkt[idx_richtung]) {
            sum_kleiner += 1;
         }
         else {
            if (punkte[idxPosition] > referenzpunkt[idx_richtung]) {
               sum_groesser += 1;
            }
         }
      }
      // Sobald alle Punkte einer beliebigen Koordinate echt groesser oder echt kleiner
      // als der Referenzpunkt sind, ist der Punkt garantiert nicht im Element
      if ((sum_groesser == ecken) || (sum_kleiner == ecken)) {
         return false;
      }
   }
   return true;
}


double TetraederVolumen(std::vector<double> punkte) {
   // Gibt das Volumen eines Tetraeders zurueck, der durch vier Koordinaten definiert ist.
   // Die vier Koordinaten sind im Array gespeichert [P0x, P0y, P0z, ..., P3x, P3y, P3z]
   double svol = 0.0;
   double a[3] = {punkte[0] - punkte[9], punkte[1] - punkte[10], punkte[2] - punkte[11]};
   double b[3] = {punkte[3] - punkte[9], punkte[4] - punkte[10], punkte[5] - punkte[11]};
   double c[3] = {punkte[6] - punkte[9], punkte[7] - punkte[10], punkte[8] - punkte[11]};
   svol = fabs(c[0]*(a[1]*b[2]-a[2]*b[1]) + c[1]*(a[2]*b[0]-a[0]*b[2]) + c[2]*(a[0]*b[1]-a[1]*b[0]));
   return svol/6.0;
}


double DreieckFlaeche(std::vector<double> punkte) {
   // Gibt das Volumen eines Dreiecks zurueck, das durch drei Koordinaten definiert ist.
   // Die drei Koordinaten sind im Array gespeichert [P0x, P0y,  P1x, P1y,  P2x, P2y]
   double sflaeche = 0.0;
   double a[2] = {punkte[2] - punkte[0], punkte[3] - punkte[1]};
   double b[2] = {punkte[4] - punkte[0], punkte[5] - punkte[1]};
   sflaeche = (a[0]*b[1] - a[1]*b[0])/2.0;
   return sflaeche;
}


double PunktInnerhalbDreieck(std::vector<double> punkte, std::vector<double> referenzpunkt) {
   // Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Dreiecks liegt, das durch die
   // uebergebenen Punkte definiert wird, werden zwei Flaechen berechnet und verglichen: Zum einen
   // wird die Flaeche des Dreiecks direkt bestimmt und zum anderen aus den Kanten mit dem
   // uebergebenen referenzpunkt. Nur wenn der referenzpunkt nicht ausserhalb des Dreiecks ist,
   // sind die Flaechen gleich gross.
   const int dimensionen = 2;
   double elemvol = 0.0;
   double referenzpunktvol = 0.0;
   std::vector<double> punktliste(dimensionen*3, 0.0);
   int idxZielKnoten = 0;
   //
   // Die Flaeche kann direkt ueber die Eckpunkte bestimmt werden
   elemvol = DreieckFlaeche(punkte);
   // Jede Kante kann als Basisseite fuer Dreiecke unterteilt werden. Nach dem gleichen Schema
   // wie fuer die komplette Flaechenberechnung wird aus folgenden Punktindizes die Flaeche
   // aller Dreieckseiten mit referenzpunkt als Spitze der Dreiecke bestimmt
   int dreieck_basispunktliste[6] = {0, 1,   1, 2,   2, 0};
   //
   // _ElementZuReferenzpunktVolumen
   // Einmal zuweisen der Referenzpunktkoordinaten reicht, da die Punkte nicht mehr ueberschrieben
   // werden
   punktliste[4] = referenzpunkt[0];
   punktliste[5] = referenzpunkt[1];
   //
   for (int idx_dreieck = 0; idx_dreieck < 3; idx_dreieck++) {
      for (int idx_knoten = 0; idx_knoten < 2; idx_knoten++) {
         idxZielKnoten = dreieck_basispunktliste[2*idx_dreieck+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      referenzpunktvol += DreieckFlaeche(punktliste);
   }
   return referenzpunktvol/elemvol;
}


double PunktInnerhalbViereck(std::vector<double> punkte, std::vector<double> referenzpunkt) {
   // Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Vierecks liegt, das durch die
   // uebergebenen Punkte definiert wird, werden zwei Flaechen berechnet und verglichen: Zum einen
   // wird die Flaeche des Vierecks ueber zwei Dreiecke bestimmt und zum anderen werden Dreiecke aus
   // den Kanten mit dem uebergebenen referenzpunkt gebildet. Nur wenn der referenzpunkt nicht
   // ausserhalb des Vierecks ist, sind die Flaechen gleich gross.
   const int dimensionen = 2;
   double elemvol = 0.0;
   double referenzpunktvol = 0.0;
   std::vector<double> punktliste(dimensionen*3, 0.0);
   int idxZielKnoten = 0;
   // Die Indizes von zwei Dreiecken, die das Viereck komplett fuellen
   int dreieck_punktliste[6] = {0, 1, 2,   1, 2, 3};
   // Bestimme die Elementflaeche des Vierecks
   for (int idx_dreieck = 0; idx_dreieck < 2; idx_dreieck++) {
      for (int idx_knoten = 0; idx_knoten < 3; idx_knoten++) {
         idxZielKnoten = dreieck_punktliste[3*idx_dreieck+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      elemvol += DreieckFlaeche(punktliste);
   }
   // Jede Kante kann als Basisseite fuer Dreiecke unterteilt werden. Nach dem gleichen Schema
   // wie fuer die komplette Flaechenberechnung wird aus folgenden Punktindizes die Flaeche
   // aller Dreieckseiten mit referenzpunkt als Spitze der Dreiecke bestimmt
   int dreieck_basispunktliste[8] = {0, 1,   1, 2,   2, 3,   3, 0};
   //
   // _ElementZuReferenzpunktVolumen
   // Einmal zuweisen der Referenzpunktkoordinaten reicht, da die Punkte nicht mehr ueberschrieben
   // werden
   punktliste[4] = referenzpunkt[0];
   punktliste[5] = referenzpunkt[1];
   //
   for (int idx_dreieck = 0; idx_dreieck < 4; idx_dreieck++) {
      for (int idx_knoten = 0; idx_knoten < 2; idx_knoten++) {
         idxZielKnoten = dreieck_basispunktliste[2*idx_dreieck+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      referenzpunktvol += DreieckFlaeche(punktliste);
   }
   return referenzpunktvol/elemvol;
}


double PunktInnerhalbTetraeder(std::vector<double> punkte, std::vector<double> referenzpunkt) {
   // Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Tetraeders liegt, das durch die
   // uebergebenen Punkte definiert wird, werden zwei Volumina berechnet und verglichen: Zum einen
   // wird das Volumen des Tetraeders direkt bestimmt und zum anderen werden Tetraeder aus den
   // Aussenflaechen mit dem uebergebenen referenzpunkt gebildet. Nur wenn der referenzpunkt nicht
   // ausserhalb des Tetraeders ist, sind die Volumina gleich gross.
   const int dimensionen = 3;
   double elemvol = 0.0;
   double referenzpunktvol = 0.0;
   std::vector<double> punktliste(dimensionen*4, 0.0);
   int idxZielKnoten = 0;
   //
   // Das Volumen kann direkt ueber die Eckpunkte bestimmt werden
   elemvol = TetraederVolumen(punkte);
   // Jede Aussenflaeche kann als Basisflaeche fuer Tetraeder verwendet werden. Nach dem gleichen
   // Schema wie fuer die komplette Volumenberechnung wird aus folgenden Punktindizes das Volumen
   // aller Aussenflaechen mit referenzpunkt als Spitze der Tetraeder bestimmt
   int tetraeder_basispunktliste[12] = {0, 1, 2,   0, 1, 3,   0, 2, 3,   1, 2, 3};
   //
   // _ElementZuReferenzpunktVolumen
   // Einmal zuweisen der Referenzpunktkoordinaten reicht, da die Punkte nicht mehr ueberschrieben
   // werden
   punktliste[9] = referenzpunkt[0];
   punktliste[10] = referenzpunkt[1];
   punktliste[11] = referenzpunkt[2];
   //
   for (int idx_tetra = 0; idx_tetra < 4; idx_tetra++) {
      for (int idx_knoten = 0; idx_knoten < 3; idx_knoten++) {
         idxZielKnoten = tetraeder_basispunktliste[3*idx_tetra+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      referenzpunktvol += TetraederVolumen(punktliste);
   }
   return referenzpunktvol/elemvol;
}


double PunktInnerhalbHexaeder(std::vector<double> punkte, std::vector<double> referenzpunkt) {
   // Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Hexaeders liegt, das durch die
   // uebergebenen Punkte definiert wird, werden zwei Volumina berechnet und verglichen: Zum einen
   // wird das Volumen des Hexaeders direkt aus zusammengesetzten Tetraedern bestimmt und zum
   // anderen werden je vier Tetraeder pro Aussenflaeche mit dem uebergebenen referenzpunkt
   // gebildet. Nur wenn der referenzpunkt nicht ausserhalb des Tetraeders ist, sind die Volumina
   // gleich gross.
   const int dimensionen = 3;
   double elemvol = 0.0;
   double referenzpunktvol = 0.0;
   std::vector<double> punktliste(dimensionen*4, 0.0);
   int idxZielKnoten = 0;
   //
   // Die Indizes von fuenf Tetraedern, die das Hexaeder komplett fuellen
   int tetraeder_punktliste[20] = {0, 1, 2, 5,   0, 2, 3, 7,   0, 4, 5, 7,   0, 2, 5, 7,   2, 5, 6, 7};
   // Bestimme das Elementvolumen des Hexaeders
   for (int idx_tetra = 0; idx_tetra < 5; idx_tetra++) {
      for (int idx_knoten = 0; idx_knoten < 4; idx_knoten++) {
         idxZielKnoten = tetraeder_punktliste[4*idx_tetra+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      elemvol += TetraederVolumen(punktliste);
   }
   // Jedes Viertel einer Aussenflaeche kann als Basisflaeche fuer Tetraeder verwendet werden. Nach
   // dem gleichen Schema wie fuer die komplette Volumenberechnung wird aus folgenden Punktindizes
   // das Volumen aller Aussenflaechen mit referenzpunkt als Spitze der Tetraeder bestimmt
   int tetraeder_basispunktliste[36] = {0, 1, 2,   0, 1, 5,   0, 2, 3,   0, 3, 7,
                                        0, 4, 5,   0, 4, 7,   1, 2, 5,   2, 3, 7,
                                        2, 5, 6,   2, 6, 7,   4, 5, 7,   5, 6, 7};
   //
   // _ElementZuReferenzpunktVolumen
   // Einmal zuweisen der Referenzpunktkoordinaten reicht, da die Punkte nicht mehr ueberschrieben
   // werden
   punktliste[9] = referenzpunkt[0];
   punktliste[10] = referenzpunkt[1];
   punktliste[11] = referenzpunkt[2];
   //
   for (int idx_tetra = 0; idx_tetra < 12; idx_tetra++) {
      for (int idx_knoten = 0; idx_knoten < 3; idx_knoten++) {
         idxZielKnoten = tetraeder_basispunktliste[3*idx_tetra+idx_knoten];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punktliste[dimensionen*idx_knoten+idx_dim] = punkte[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      referenzpunktvol += TetraederVolumen(punktliste);
   }
   return referenzpunktvol/elemvol;
}


double PunktInnerhalbElement(std::vector<double> punkte, std::vector<double> referenzpunkt,
   const int dimensionen, const int ecken) {
   // Fuer die Bestimmung, ob ein referenzpunkt innerhalb eines Elements liegt, das durch die
   // uebergebenen Punkte definiert wird, werden zwei Flaechen (2D) bzw. zwei Volumina (3D) berechnet
   // und verglichen: Zum einen wird die Berechnung mit den Eckpunkten des Elements durchgefuehrt,
   // zum anderen mit dem uebergebenene referenzpunkt. Nur wenn der referenzpunkt nicht ausserhalb
   // des Elements ist, sind die Flaechen bzw. Volumina gleich gross.
   //
   // Folgende Varianten werden unterstuetzt:
   // - je zwei Koordinaten pro Punkt (dimensionen == 2)
   //   -> Flaechenberechnung mit Dreiecken (ecken == 3 punkte) oder Vierecken (ecken == 4 punkte)
   //
   // - je drei Koordinaten pro Punkt (dimensionen == 3)
   //   -> Volumenberechnung mit Tetraedern (ecken == 4 punkte) oder Hexaeders (ecken == 8 punkte)
   //
   // Der erste Array enthaelt dimensionen*ecken Werte, bspw. bei einem Hexaeder die 3 Koordinaten
   // der 8 Eckpunkte
   // [P0x, P0y, P0z, P1x, P1y, P1z, ..., P7x, P7y, P7z].
   //
   // Fuer die korrekte Berechnung muessen die Knoten von Hexaeder und Viereck-Elements in der
   // dargestellen Reihenfolge gespeichert sein:
   //
   //   7 __________  6          #
   //     \         \            #   3  ____________  0
   //     |\        .\           #     |            |
   //     | \       . \          #     |            |
   //     |4 \_________\ 5       #     |            |
   //     |  |      .  |         #     |            |
   //   3 |..|....... 2|         #     |            |
   //     \  |       . |         #     |            |
   //      \ |        .|         #     |____________|
   //       \|_________|         #   2                1
   //      0             1       #
   //
   double retval = 0.0;
   if (dimensionen == 2) {
      if (ecken == 3) {
         retval = PunktInnerhalbDreieck(punkte, referenzpunkt);
      }
      else {
         retval = PunktInnerhalbViereck(punkte, referenzpunkt);
      }
   }
   else {
      if (ecken == 4) {
         retval = PunktInnerhalbTetraeder(punkte, referenzpunkt);
      }
      else {
         retval = PunktInnerhalbHexaeder(punkte, referenzpunkt);
      }
   }
   return retval;
}


int PunktInElement(const double* knotenKoordinaten, int numElemente, const int* elementeEcken,
   std::vector<double> referenzpunkt, const int dimensionen, const int ecken) {
   // Gebe den Index des Elements zurueck, das referenzpunkt enthaelt.
   // Der Array elementEcken hat ecken*numElemente Eintraege, bspw fuer 8 ecken
   // [E0_P0, E0_P1, E0_P2, E0_P3, E0_P4, E0_P5, E0_P6, E0_P7,   E1_P0, E1_P1, E1_P2, ...]
   // knotenKoordinaten dimensionen-mal soviele Eintraege haben wie der groesste Wert aus elementeEcken
   int idxZielKnoten = 0;
   std::vector<double> punkte(dimensionen*ecken, 0.0);
   //double punkte[dimensionen*ecken] = {0.0};
   int zielElement = -1;
   double minverhaeltnis = 2.0;
   double volverhaeltnis = 2.0;
   for (int idx_element = 0; idx_element < numElemente; idx_element++) {
      // Jedes Element besteht aus ecken (bspw. 8) Punkten mit dimensionen (bspw. 3) Koordinaten
      for (int idx_ecken = 0; idx_ecken < ecken; idx_ecken++) {
         idxZielKnoten = elementeEcken[idx_element*ecken+idx_ecken];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            punkte[dimensionen*idx_ecken+idx_dim] = knotenKoordinaten[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      // Ueberpruefe, ob sich der Referenzpunkt (wahrscheinlich) im Element befindet
      // (notwendige Bedingung - schnelle Berechnung)
      if (!PunktMoeglicherweiseInElement(punkte, referenzpunkt, dimensionen, ecken)) {
         continue;
      }
      // Nur wenn die notwendige Bedingung erfuellt ist, kann genauer untersucht
      // werden, ob der Punkt tatsaechlich innerhalb des Elements ist
      volverhaeltnis = PunktInnerhalbElement(punkte, referenzpunkt, dimensionen, ecken);
      if (volverhaeltnis < minverhaeltnis) {
         zielElement = idx_element;
         minverhaeltnis = volverhaeltnis;
      }
   }
   return zielElement;
}


void KnotengewichtungPunktInDreieck(std::vector<double> dreieckpunkte, std::vector<double> referenzpunkt,
   std::vector<double> gewichtung) {
   // Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in dreieckpunkte
   // definierten Dreiecks hat. Dabei wird ein linearer Ansatz verwendet. Falls einer der
   // Rueckgabewerte kleiner als Null ist, liegt der Referenzpunkt nicht im durch punkte definierten
   // Dreieck. Der Array dreieckpunkte hat 2*3 Eintraege  [P0x, P0y, P1x, P1y, P2x, P2y]
   // Gewichtung muss drei Eintraege bereitstellen, die in dieser Funktion beschrieben werden.
   //
   // Aktuelle Implementierung basierend auf der 2D-Punktgleichung
   // (referenzpunkt-p0) = (p1-p0)*s + (p2-p0)*t
   double Rx = referenzpunkt[0] - dreieckpunkte[0];
   double Ry = referenzpunkt[1] - dreieckpunkte[1];
   double X1 = dreieckpunkte[2] - dreieckpunkte[0];
   double Y1 = dreieckpunkte[3] - dreieckpunkte[1];
   double X2 = dreieckpunkte[4] - dreieckpunkte[0];
   double Y2 = dreieckpunkte[5] - dreieckpunkte[1];
   double det_gesamt = X1*Y2 - X2*Y1;
   // Berechnung kann nur sinnvoll fortgesetzt werden, wenn sich die Determinante von Null unterscheidet
   if (fabs(det_gesamt) > 0.0000001) {
      // Die zwei Gleichungen koennen als Matrix zusammengefasst werden. Die Parameter s und t
      // koennen durch Invertieren der Matrix bestimmt werden.
      //   Rx     X1, X2     s
      //   Ry  =  Y1, Y2  *  t
      double s = ( Rx*Y2 - Ry*X2)/det_gesamt;
      double t = (-Rx*Y1 + Ry*X1)/det_gesamt;
      gewichtung[0] = 1.0-s-t;
      gewichtung[1] = s;
      gewichtung[2] = t;
   }
   else {
      gewichtung[0] = -1.0;
      gewichtung[1] = -1.0;
      gewichtung[2] = -1.0;
   }
}


void KnotengewichtungPunktInViereck(std::vector<double> zielPunktListe, std::vector<double> referenzpunkt,
   std::vector<double> gewichtung) {
   // Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in zielPunktListe
   // definierten Elements hat. Der Array enthaelt 2*4 Werte
   // [P0x, P0y,  P1x, P1y,  P2x, P2y,  P3x, P3y]
   // Gewichtung muss vier Eintraege bereitstellen, die in dieser Funktion beschrieben werden.
   // KnotengewichtungPunktInElement
   const int dimensionen = 2;
   const int ecken = 4;
   //
   for (int idx_gewichtung = 0; idx_gewichtung < ecken; idx_gewichtung++) {
      gewichtung[idx_gewichtung] = 0.0;
   }
   std::vector<double> dreieck_gewichte(ecken, 0.0);
   std::vector<double> mittelpunkt(dimensionen, 0.0);
   std::vector<double> dreieckpunkte(3*dimensionen, 0.0);
   //
   double temp_summe = 0.0;
   int idxZielKnoten = 0;
   // Mittelpunkt
   for (int idx_ecken = 0; idx_ecken < ecken; idx_ecken++) {
      for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
         mittelpunkt[idx_dim] += zielPunktListe[dimensionen*idx_ecken+idx_dim]/ecken;
      }
   }
   // Einmaliges Zuweisen der Mittelpunktkoordinaten reicht, da die Punkte im folgenden nicht mehr
   // ueberschrieben werden
   for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
      dreieckpunkte[dimensionen*2+idx_dim] = mittelpunkt[idx_dim];
   }
   // Mit der Definition der Punkte wie in PunktInnerhalbElement beschrieben (0-3) und dem Mittelpunkt
   // als (4) ergeben sich 4 Dreiecke mit Punkten der folgenden Indizes
   int ref_kombinationen = 4;
   //int dreieck_komb[3*ref_kombinationen] = {0, 1, 4,    1, 2, 4,    2, 3, 4,    3, 0, 4};
   static const int dreieck_komb[] = {0, 1, 4,    1, 2, 4,    2, 3, 4,    3, 0, 4};
   //
   bool gueltigeGewichtung = true;
   for (int idx_dreieck = 0; idx_dreieck < ref_kombinationen; idx_dreieck++) {
      // Fuer jedes der moeglichen Dreiecke werden die Eckpunkte bestimmt (2*3 Werte)
      gueltigeGewichtung = true;
      for (int idx_eckpunkt = 0; idx_eckpunkt < 2; idx_eckpunkt++) {
         idxZielKnoten = dreieck_komb[3*idx_dreieck+idx_eckpunkt];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            dreieckpunkte[dimensionen*idx_eckpunkt+idx_dim] = zielPunktListe[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      //
      KnotengewichtungPunktInDreieck(dreieckpunkte, referenzpunkt, dreieck_gewichte);
      // Nur wenn der Referenzpunkt sich auf oder im Dreieck befindet, sind alle Gewichtungen
      // zwischen 0 und 1 und somit gueltig.
      for (int idx_gewichtung = 0; idx_gewichtung < ecken; idx_gewichtung++) {
         if (dreieck_gewichte[idx_gewichtung] < 0.0) {
            gueltigeGewichtung = false;
            break;
         }
      }
      if (!gueltigeGewichtung) {
        continue;
      }
      // Die ersten beiden Gewichtungen stammen von zwei Eckpunkten des Vierecks und
      // gehen dementsprechend 1:1 in die finale Gewichtung ein
      gewichtung[dreieck_komb[3*idx_dreieck]] = dreieck_gewichte[0];
      gewichtung[dreieck_komb[3*idx_dreieck+1]] = dreieck_gewichte[1];
      // Die Gewichtung des Mittelpunktes geht ueberall gleichmaessig ein
      for (int idx_gewichtung_mp = 0; idx_gewichtung_mp < ecken; idx_gewichtung_mp++) {
         gewichtung[idx_gewichtung_mp] += dreieck_gewichte[2]/ecken;
      }
      // Sobald eine Zuweisung stattgefunden hat, sind wir fertig. Entweder, der Punkt lag
      // echt innerhalb des Tetraeders, dann kaemen keine weiteren Anteile hinzu. Oder der Punkt
      // lag auf einer Aussenseite, Kante oder Eckpunkt des Tetraeders. In dem Fall wuerde er auch so
      // bei anderen Tetraedern gefunden werden, aber das Ergebnis bliebe das selbe.
      break;
   }
}


void KnotengewichtungPunktInTetraeder(std::vector<double> tetraederpunkte, std::vector<double> referenzpunkt,
   std::vector<double> gewichtung) {
   // Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in tetraederpunkte
   // definierten Tetraeders hat. Dabei wird ein linearer Ansatz verwendet. Falls einer der
   // Rueckgabewerte kleiner als Null ist, liegt der Referenzpunkt nicht im durch punkte definierten
   // Tetraeder. Der Array tetraederpunkte hat 4*3 Eintraege
   // [P0x, P0y, P0z, P1x, P1y, P1z, P2x, P2y, P2z, P3x, P3y, P3z]
   // Gewichtung muss vier Eintraege bereitstellen, die in dieser Funktion beschrieben werden.
   //
   // Aktuelle Implementierung basierend auf der 3D-Punktgleichung
   // (referenzpunkt-p0) = (p1-p0)*r + (p2-p1)*s + (p3-p1)*t
   double Rx = referenzpunkt[0] - tetraederpunkte[0];
   double Ry = referenzpunkt[1] - tetraederpunkte[1];
   double Rz = referenzpunkt[2] - tetraederpunkte[2];
   double X1 = tetraederpunkte[3] - tetraederpunkte[0];
   double Y1 = tetraederpunkte[4] - tetraederpunkte[1];
   double Z1 = tetraederpunkte[5] - tetraederpunkte[2];
   double X2 = tetraederpunkte[6] - tetraederpunkte[3];
   double Y2 = tetraederpunkte[7] - tetraederpunkte[4];
   double Z2 = tetraederpunkte[8] - tetraederpunkte[5];
   double X3 = tetraederpunkte[9] - tetraederpunkte[3];
   double Y3 = tetraederpunkte[10] - tetraederpunkte[4];
   double Z3 = tetraederpunkte[11] - tetraederpunkte[5];
   double det_gesamt = X1*(Y2*Z3-Y3*Z2) - X2*(Y1*Z3-Y3*Z1) + X3*(Y1*Z2-Y2*Z1);
   // Berechnung kann nur sinnvoll fortgesetzt werden, wenn sich die Determinante von Null unterscheidet
   if (fabs(det_gesamt) > 0.0000001) {
      // Die drei Gleichungen koennen als Matrix zusammengefasst werden. Die Parameter r, s und t
      // koennen durch Invertieren der Matrix bestimmt werden.
      //   Rx     X1, X2, X3     r
      //   Ry  =  Y1, Y2, Y3  *  s
      //   Ry     Z1, Z2, Y3     t
      double r = ( Rx*(Y2*Z3-Y3*Z2) - Ry*(X2*Z3-X3*Z2) + Rz*(X2*Y3-X3*Y2))/det_gesamt;
      double s = (-Rx*(Y1*Z3-Y3*Z1) + Ry*(X1*Z3-X3*Z1) - Rz*(X1*Y3-X3*Y1))/det_gesamt;
      double t = ( Rx*(Y1*Z2-Y2*Z1) - Ry*(X1*Z2-X2*Z1) + Rz*(X1*Y2-X2*Y1))/det_gesamt;
      gewichtung[0] = 1.0-r;
      gewichtung[1] = r-s-t;
      gewichtung[2] = s;
      gewichtung[3] = t;
   }
   else {
      gewichtung[0] = -1.0;
      gewichtung[1] = -1.0;
      gewichtung[2] = -1.0;
      gewichtung[3] = -1.0;
   }
}


void KnotegewichtungPunktInHexaeder(std::vector<double> zielPunktListe, std::vector<double> referenzpunkt,
   std::vector<double> gewichtung) {
   // Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in zielPunktListe
   // definierten Elements hat. Der Array enthaelt 3*8 Werte
   //  [P0x, P0y, P0z, P1x, P1y, P1z, ..., P7x, P7y, P7z]
   // Gewichtung muss acht Eintraege bereitstellen, die in dieser Funktion beschrieben werden.
   // KnotengewichtungPunktInElement
   const int dimensionen = 3;
   const int ecken = 8;
   //
   for (int idx_gewichtung = 0; idx_gewichtung < ecken; idx_gewichtung++) {
      gewichtung[idx_gewichtung] = 0.0;
   }
   std::vector<double> tetraeder_gewichte(ecken, 0.0);
   // Mit der Definition der Punkte wie in PunktInnerhalbElement beschrieben, ergeben sich die
   // sechs Seitenmitten aus den Punkten mit den folgenden Indizes
   int idxliste_seitenmitten[24] = {0, 1, 2, 3,   0, 1, 4, 5,   0, 3, 4, 7,
                                    1, 2, 5, 6,   2, 3, 6, 7,   4, 5, 6, 7};
   std::vector<double> mittelpunkt(dimensionen, 0.0);
   std::vector<double> seitenmitten(6*dimensionen, 0.0);
   std::vector<double> tetraederpunkte(4*dimensionen, 0.0);
   //
   double temp_summe = 0.0;
   int idxZielKnoten = 0;
   // Mittelpunkt
   for (int idx_ecken = 0; idx_ecken < ecken; idx_ecken++) {
      for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
         mittelpunkt[idx_dim] += zielPunktListe[dimensionen*idx_ecken+idx_dim]/ecken;
      }
   }
   // Seitenmitten
   for (int idx_seiten = 0; idx_seiten < 6; idx_seiten++) {
      for (int idx_tetra = 0; idx_tetra < 4; idx_tetra++) {
         idxZielKnoten = idxliste_seitenmitten[4*idx_seiten+idx_tetra];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            seitenmitten[dimensionen*idx_seiten+idx_dim] += zielPunktListe[dimensionen*idxZielKnoten+idx_dim]/4.0;
         }
      }
   }
   // Einmaliges Zuweisen der Mittelpunktkoordinaten reicht, da die Punkte im folgenden nicht mehr
   // ueberschrieben werden
   for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
      tetraederpunkte[6+idx_dim] = mittelpunkt[idx_dim];
   }
   // Mit der Definition der Punkte wie in PunktInnerhalbElement beschrieben (0-7), dem Mittelpunkt
   // als (8) und allen sechs Seitenmitten (9-14) ergeben sich 24 Tetraeder mit Punkten der
   // folgenden Indizes
   int ref_kombinationen = 24;
   //int tetraeder_kombinationen[4*ref_kombinationen] = {
   static const int tetraeder_kombinationen[] = {
      0, 1, 8, 9,    0, 1, 8, 10,   0, 3, 8, 9,    0, 3, 8, 11,
      0, 4, 8, 10,   0, 4, 8, 11,   1, 2, 8, 9,    1, 2, 8, 12,
      1, 5, 8, 10,   1, 5, 8, 12,   2, 3, 8, 9,    2, 3, 8, 13,
      2, 6, 8, 12,   2, 6, 8, 13,   3, 7, 8, 11,   3, 7, 8, 13,
      4, 5, 8, 10,   4, 5, 8, 14,   4, 7, 8, 11,   4, 7, 8, 14,
      5, 6, 8, 12,   5, 6, 8, 14,   6, 7, 8, 13,   6, 7, 8, 14};
   bool gueltigeGewichtung = true;
   for (int idx_tetra = 0; idx_tetra < ref_kombinationen; idx_tetra++) {
      // Fuer jedes der moeglichen Tetraeder werden die Eckpunkte bestimmt (3*4 Werte)
      gueltigeGewichtung = true;
      for (int idx_eckpunkt = 0; idx_eckpunkt < 2; idx_eckpunkt++) {
         idxZielKnoten = tetraeder_kombinationen[4*idx_tetra+idx_eckpunkt];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            tetraederpunkte[dimensionen*idx_eckpunkt+idx_dim] = zielPunktListe[dimensionen*idxZielKnoten+idx_dim];
         }
      }
      idxZielKnoten = tetraeder_kombinationen[4*idx_tetra+3] - 9;
      for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
         tetraederpunkte[9+idx_dim] = seitenmitten[dimensionen*idxZielKnoten+idx_dim];
      }
      //
      KnotengewichtungPunktInTetraeder(tetraederpunkte, referenzpunkt, tetraeder_gewichte);
      // Nur wenn der Referenzpunkt sich auf oder im Tetraeder befindet, sind alle Gewichtungen
      // zwischen 0 und 1 und somit gueltig.
      for (int idx_gewichtung = 0; idx_gewichtung < ecken; idx_gewichtung++) {
         if (tetraeder_gewichte[idx_gewichtung] < 0.0) {
            gueltigeGewichtung = false;
            break;
         }
      }
      if (!gueltigeGewichtung) {
        continue;
      }
      // Die ersten beiden Gewichtungen stammen von zwei Eckpunkten des Hexaeders und
      // gehen dementsprechend 1:1 in die finale Gewichtung ein
      gewichtung[tetraeder_kombinationen[4*idx_tetra]] = tetraeder_gewichte[0];
      gewichtung[tetraeder_kombinationen[4*idx_tetra+1]] = tetraeder_gewichte[1];
      // Die Gewichtung des Mittelpunktes geht ueberall gleichmaessig ein
      for (int idx_gewichtung_mp = 0; idx_gewichtung_mp < ecken; idx_gewichtung_mp++) {
         gewichtung[idx_gewichtung_mp] += tetraeder_gewichte[2]/ecken;
      }
      // Der letzte Punkt ist eine Seitenmitte. Deren Gewichtung uebertraegt sich gleichmaessig auf
      // die vier Punkte, die diese Seite definieren
      for (int idx_gewichtung_sm = 0; idx_gewichtung_sm < 4; idx_gewichtung_sm++) {
         idxZielKnoten = idxliste_seitenmitten[4*(tetraeder_kombinationen[4*idx_tetra+3] - 9) + idx_gewichtung_sm];
         gewichtung[idxZielKnoten] += tetraeder_gewichte[3]/4.0;
      }
      // Sobald eine Zuweisung stattgefunden hat, sind wir fertig. Entweder, der Punkt lag
      // echt innerhalb des Tetraeders, dann kaemen keine weiteren Anteile hinzu. Oder der Punkt
      // lag auf einer Aussenseite, Kante oder Eckpunkt des Tetraeders. In dem Fall wuerde er auch so
      // bei anderen Tetraedern gefunden werden, aber das Ergebnis bliebe das selbe.
      break;
   }
}


void KnotengewichtungPunktInElement(const std::vector<double> zielPunktListe, std::vector<double> referenzpunkt,
   std::vector<double> gewichtung, const int dimensionen, const int ecken) {
   // Bestimmt die Anteile, die ein referenzpunkt aus den Knotenpunkten des in zielPunktListe
   // definierten Elements hat. Der Array enthaelt dimensionen*ecken Werte, bspw fuer ein Hexaeder
   // Gewichtung muss soviele Eintraege wie ecken bereitstellen, die in dieser Funktion beschrieben
   // werden.
   if (dimensionen == 2) {
      if (ecken == 3) {
         KnotengewichtungPunktInDreieck(zielPunktListe, referenzpunkt, gewichtung);
      }
      else {
         KnotengewichtungPunktInViereck(zielPunktListe, referenzpunkt, gewichtung);
      }
   }
   else {
      if (ecken == 4) {
         KnotengewichtungPunktInTetraeder(zielPunktListe, referenzpunkt, gewichtung);
      }
      else {
         KnotegewichtungPunktInHexaeder(zielPunktListe, referenzpunkt, gewichtung);
      }
   }
}
   

extern "C" ADDAPI void ADDCALL Gewichtung_Bestimmen(const int dimensionen, const int eckenAlt,
   const int eckenNeu, const double* knotenKoordinatenAlt, int numElementeAlt,
   const int* elementeEckenAlt, int numKnotenNeu, const double* knotenKoordinatenNeu,
   int numElementeNeu, int* const elementeEckenNeu, int* gewichtungKnotenLabels,
   double* gewichtungKnotenWerte, int* bezugsElement) {
   // Bestimme die Zuordnung und lineare Gewichtung von einem Satz (neuer) Knoten bezueglich alter
   // Knoten und dazugehoeriger Elemente. Fuer die neuen Elemente soll eine direkte Zuordnung zum
   // alten bezugselement gefunden werden. Dazu werden mehrere Werte und Arrays erwartet:
   // Die Anzahl an dimensionen sollte 2 oder 3 sein sowie fuer jedes Element die entsprechende
   // Anzahl eckenAlt und eckenNeu (2D: 3 fuer Dreieck, 4 fuer Viereck; 3D: 4 fuer Tetraeder, 8 fuer
   // Hexaeder - muss vorher ueberprueft werden).
   // elementeEckenAlt hat numElementeAlt*eckenAlt Eintraege, bspw. fuer ein 3D Hexaeder
   // [E0_P0, E0_P1, E0_P2, E0_P3, E0_P4, E0_P5, E0_P6, E0_P7,   E1_P0, E1_P1, E1_P2, ...]
   // knotenKoordinatenAlt hat dimensionen-mal soviele Eintraege wie die hoechste Zahl in
   // elementeEckenAlt.
   // Der gleiche Zusammenhang bezueglich numElementeNeu gilt auch fuer elementeEckenNeu und
   // knotenKoordinatenNeu, wobei die Anzahl von Eintraegen in knotenKoordinatenNeu gleichzeitig
   // auch eckenNeu*numKnotenNeu sein muss.
   // Die drei Arrays gewichtungKnotenLabels, gewichtungKnotenWerte und bezugsElement werden in
   // dieser Funktion beschrieben und muessen vorher in passender Groesse bereitgestellt werden:
   // gewichtungKnotenLabels und gewichtungKnotenWerte haben jeweils eckenAlt*numKnotenNeu Eintraege,
   // bezugsElement hat numElementeNeu Eintraege.
   std::vector<double> referenzpunkt(dimensionen, 0.0);
   int idxZielElement = 0;
   int idxZielKnoten = 0;
   int idxZuweisung = 0;
   std::vector<double> zielPunktListe(eckenAlt*dimensionen, 0.0);
   std::vector<int> labelliste(eckenAlt, 0);
   std::vector<double> gewichtung(eckenAlt, 0.0);
   int labelElementAlt = -1;
   // Zuerst Elementmittelpunkte aller neuen Zielelemente bestimmen. Dann wird ueberprueft, in
   // welchem der alten Elemente der Mittelpunkt jedes Zielelements liegt. Der Verweis auf dieses
   // alte Element wird in bezugsElement gespeichert.
   for (int idx_element = 0; idx_element < numElementeNeu; idx_element++) {
      for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
         referenzpunkt[idx_dim] = 0.0;
      }
      for (int idx_ecken = 0; idx_ecken < eckenNeu; idx_ecken++) {
         idxZielKnoten = elementeEckenNeu[idx_element*eckenNeu+idx_ecken];
         for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
            referenzpunkt[idx_dim] += knotenKoordinatenNeu[dimensionen*idxZielKnoten+idx_dim]/eckenNeu;
         }
      }
      labelElementAlt = PunktInElement(knotenKoordinatenAlt, numElementeAlt, elementeEckenAlt,
         referenzpunkt, dimensionen, eckenAlt);
      // Labels starten eins hoeher als Indizes (mit denen hier gearbeitet wird)
      // Falls das Element nicht gefunden wird, gibt PunktInElement -1 zurueck und als Label wird
      // 0 gespeichert
      bezugsElement[idx_element] = labelElementAlt+1;
   }
   // Anschliessend fuer alle Knoten des neuen Zielelements das (alte) Element bestimmen, in dem sie
   // gewesen waeren. Nachdem das alte Element gefunden worden ist, wird die Position und somit
   // gewichtung bestimmt, die alle Punkte des alten Elements auf den jeweiligen Knoten des neuen
   // Zielelements haben. Fuer jeden Zielpunkt werden Labels und Gewichtungen der alten Elemente in
   // gewichtungKnotenLabels und gewichtungKnotenWerte gespeichert.
   for (int idx_knoten = 0; idx_knoten < numKnotenNeu; idx_knoten++) {
      for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
         referenzpunkt[idx_dim] = knotenKoordinatenNeu[dimensionen*idx_knoten+idx_dim];
      }
      labelElementAlt = PunktInElement(knotenKoordinatenAlt, numElementeAlt, elementeEckenAlt,
         referenzpunkt, dimensionen, eckenAlt);
      if (labelElementAlt == -1) {
         // Knoten nicht enthalten
         for (int idx_gewichtung = 0; idx_gewichtung < eckenAlt; idx_gewichtung++) {
            labelliste[idx_gewichtung] = -1;
            gewichtung[idx_gewichtung] = 0.0;
         }
      }
      else {
         for (int idx_ecken = 0; idx_ecken < eckenAlt; idx_ecken++) {
            idxZielElement = elementeEckenAlt[eckenAlt*labelElementAlt+idx_ecken];
            for (int idx_dim = 0; idx_dim < dimensionen; idx_dim++) {
               zielPunktListe[dimensionen*idx_ecken+idx_dim] = knotenKoordinatenAlt[dimensionen*idxZielElement+idx_dim];
            }
            labelliste[idx_ecken] = idxZielElement;
         }         
         KnotengewichtungPunktInElement(zielPunktListe, referenzpunkt, gewichtung, dimensionen, eckenAlt);
      }
      for (int idx_gewichtung = 0; idx_gewichtung < eckenAlt; idx_gewichtung++) {
         gewichtungKnotenLabels[eckenAlt*idx_knoten+idx_gewichtung] = labelliste[idx_gewichtung];
         gewichtungKnotenWerte[eckenAlt*idx_knoten+idx_gewichtung] = gewichtung[idx_gewichtung];
      }
   }
}
 
