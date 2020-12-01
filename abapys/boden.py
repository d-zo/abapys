# -*- coding: utf-8 -*-
"""
boden.py   v1.9 (2020-10)
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

# TODO:
# - Lineare Uebergaenge am Rand scheint nur fuer zylindrische Koerper zu stimmen
#   (fuer quaderfoerminge aktuell konstant)
# - Ueber die Tiefe mehr Kontrolle fuer die Mesh-Anpassung
# - Aktuell kann der lineare Uebergang "Unten" nur vermieden werden, wenn bodenbereich[0] nur ein
#   Element hat (ggfs. kuenstlich erzeugt)


# -------------------------------------------------------------------------------------------------
def Boden(modell, name, bodentiefe, voidhoehe, bodenbereich, gittergroessen, gitter_boden_vertikal,
   schichten, schichtmaterial, restmaterial, extrasets=False, netz=True, euler=True,
   xypartition=[True, True], partition_durchziehen=False, viertel=4, rotationsprofilpunkte=None):
   """Erzeuge einen Untergrund name im uebergebenen modell. Die folgende Skizze gibt einen
   Ueberblick ueber die verwendeten geometrischen Groessen und Bestandteile intern verwendeter
   Bezeichnungen (bspw. fuer Sets), wobei in der Darstellung alle bodenbereiche als rund angenommen
   werden. Gibt [part<name>, inst<name>] zurueck.
   
          bodenbereich[0]
            ("Aussen")
       _|________________|_
        |                |
        | bodenbereich[1:-1]
        | ("Uebergaenge")|
        | _|__________|_ |
        |  |          |  |
        .  .          .  .
        .  .          .  .
        | bodenbereich[-1]
        |  | ("Innen")|  |
        |  | _|____|_ |  |
        |  |  |    |  |  |
        |                |
            ..------..
          .. ..----.. .. 
         /  /  .--.  \  \    
        |  |  (    )  |  |   ___|_
        |\ |\ |'--'| /| /|      |
        | '+ '+----+' +' |      |
        |  |''+----+''|  |      |
        |  |  |    |  |  |      | voidhoehe (nur bei euler=True)
        |  |..+----+..|  |      |
        | .+ .+----+. +. |      |
        |/ |/ |.--.| \| \|      |
        |  |  (    )  |  |   ___|__________________|_
        |\ |\ |'--'| /| /|      |                  |
        | '+ '+----+' +' |      |                  |
        |  |''+----+''|  |      |                  |
        |  |  |    |  |  |      | schichten[-1]    |
        |  |..+----+..|  |      | ("Schichten")    |
        | .+ .+----+. +. |      |                  |
        |/ |/ |.--.| \| \|      |                  |
        |  |  (    )  |  |   ___|_                 | bodentiefe
        |\ |\ |'--'| /| /|      |                  |
        | '+ '+----+' +' |      |                  |
        |  |''+----+''|  |      |                  |
        |  |  |    |  |  |      | ("Unten")        |
        |  |..+----+..|  |      |                  |
        | .+ .+----+. +. |      |                  |
        |/ |/ |.--.| \| \|      |                  |
        |  |  (    )  |  |   ___|__________________|_
         \  \  '--'  /  /       |                  |
          '' ''----'' ''
            ''------''

   Der Vektor bodenbereich besteht entweder aus Eintraegen mit einem Element (Radius fuer runde
   Geometrie/Partition) oder zwei Elementen (halbe Kantenlaenge fuer rechteckige Geometrie oder
   Partition). Zur Vernetzung werden entsprechend viele Eintraege wie in schichten fuer
   gittergroessen benoetigt. Dabei kann entweder ein Wert gegeben werden (konstante Gittergroesse)
   oder zwei (linear veraendernde Gittergroesse). gitter_boden_vertikal gibt die vertikale
   Gitterfeinheit fuer den Schichtenbereich und das Void an. Fuer jeden Eintrag in schichten muss
   auch ein Material in schichtmaterial definiert sein. Zusaetzlich ist ein restmaterial, bspw. fuer
   den Bereich unterhalb der Schichten, anzugeben. Optional koennen extrasets erstellt werden.
   Optional kann der Boden als euler-Koerper oder Lagrange-Loerper ohne void-Bereich) erstellt
   werden. Partitionen werden mit einer Standardpartitionierung in x/y-Richtung erzeugt. Das
   Verhalten kann mit xypartition explizit deaktiviert werden. Optional kann nur Viertel- oder
   Halbmodell mit dem Parameter viertel erzeugt werden (nur die Werte 1,2 und 4 werden
   unterstuetzt). Falls nur ein halbes/viertel Modell erzeugt wird, werden Partitionen in der
   Schnittebene nicht erzeugt (unabhaengig von den Angaben in xypartition).
   Rechteckige Partitionen ziehen sich mit partition_durchziehen=True durch das komplette Modell,
   standardmaessig aber nur bis zur naechstgroesseren Partition (ggfs. mit Verbindungen).
   
   Zusaetzlich erlaubt die Uebergabe von rotationsprofilpunkte (x-y-Punktkoordinaten) die Erstellung
   eines 3D-Profils auf Basis der Zeichnung (aus den Punkten) und einer Rotation um die vertikale
   Achse der Zeichnung (experimentell).
   """
   import assembly
   from abaqusConstants import DEFORMABLE_BODY, EULERIAN, ON
   from grundkoerper import Zylinder_erstellen, Zylinder_flaechensets
   from grundkoerper import Quader_erstellen, Quader_flaechensets
   from grundkoerper import Grundkoerper_sets
   from grundkoerper import Rotationsprofil_erstellen
   from hilfen import Log
   #
   if (not (len(bodenbereich) == len(gittergroessen))):
      Log('# Fehler: bodenbereich und gittergroessen muessen gleich viele Eintraege haben');
      return;
   #
   # Erstelle und partitioniere Bodenkoerper
   if (euler):
      bodenmaterial = EULERIAN;
   else:
      bodenmaterial = DEFORMABLE_BODY;
      voidhoehe = 0.0;
   #
   # Falls ein Zylinder erstellt wird, erzeuge den inneren Bereich als sweep statt als structured
   kernSweep = False;
   if (rotationsprofilpunkte is None):
      if   (len(bodenbereich[0]) == 1):
         kernSweep = True;
         Zylinder_erstellen(modell=modell, name=name, radius=bodenbereich[0][0],
            hoehe=bodentiefe+voidhoehe, materialtyp=bodenmaterial, viertel=viertel);
      elif (len(bodenbereich[0]) == 2):
         laenge = 2.0*bodenbereich[0][0];
         breite = 2.0*bodenbereich[0][1];
         if ((viertel == 1) or (viertel == 2)):
            if (viertel == 1):
               breite = [0.0, bodenbereich[0][1]];
            #
            laenge = [0.0, bodenbereich[0][0]];
         #
         Quader_erstellen(modell=modell, name=name, laenge=laenge, breite=breite,
            hoehe=bodentiefe+voidhoehe, materialtyp=bodenmaterial);
      else:
         Log('# Fehler: Ungueltige Anzahl an Werten in bodenbereich[0]');
         return;
   #
   else:
      Rotationsprofil_erstellen(modell=modell, name=name, punkte=rotationsprofilpunkte,
         materialtyp=bodenmaterial, viertel=viertel);
   #
   _Boden_partitionieren(modell=modell, name=name, bodentiefe=bodentiefe,
      voidhoehe=voidhoehe, bodenbereich=bodenbereich, schichten=schichten,
      xypartition=xypartition, partition_durchziehen=partition_durchziehen, viertel=viertel);
   #
   Grundkoerper_sets(modell=modell, name=name);
   _Boden_setserstellen(modell=modell, name=name, bodentiefe=bodentiefe,
      voidhoehe=voidhoehe, bodenbereich=bodenbereich, schichten=schichten,
      schichtmaterial=schichtmaterial, restmaterial=restmaterial);
   if (len(bodenbereich[0]) == 1):
      Zylinder_flaechensets(modell=modell, name=name, radius=bodenbereich[0][0],
         hoehe=bodentiefe+voidhoehe, viertel=viertel);
   else:
      Quader_flaechensets(modell=modell, name=name, laenge=laenge, breite=breite,
         hoehe=bodentiefe+voidhoehe);
   #
   _Boden_vernetzen(modell=modell, name=name, bodentiefe=bodentiefe, voidhoehe=voidhoehe,
      bodenbereich=bodenbereich, gittergroessen=gittergroessen,
      gitter_boden_vertikal=gitter_boden_vertikal, schichten=schichten,
      extrasets=extrasets, netz=netz, euler=euler, kernSweep=kernSweep);
   instname = 'inst' + name;
   instBoden = modell.rootAssembly.Instance(dependent=ON, name=instname, part=modell.parts[name]);
   return [modell.parts[name], instBoden];
#


# -------------------------------------------------------------------------------------------------
def _Boden_partitionieren(modell, name, bodentiefe, voidhoehe, bodenbereich, schichten,
   xypartition=[True, True], partition_durchziehen=False, viertel=4):
   """Partitioniere das Bauteil (Part) name aus dem aktiven modell anhand der uebergebenen Parameter.
   Die gesamte Bauteilhoehe ist bodentiefe und voidhoehe, wobei bodentiefe zusaetzlich in einzelne
   schichten unterteilt ist. In jeder Ebene werden mit bodenbereich einzelne Partitionen definiert.
   Die Erstellung der Grundpartitionen kann mit xypartition explizit deaktiviert werden. Falls nur
   ein halbes/viertel Modell erzeugt wird, werden Partitionen in der Schnittebene nicht erzeugt
   (unabhaengig von den Angaben in xypartition).
   Rechteckige Partitionen ziehen sich mit partition_durchziehen = True durch das komplette Modell,
   standardmaessig aber nur bis zur naechstgroesseren Partition (ggfs. mit Verbindungen).
   """
   from grundkoerper import Grundkoerper_standardpartitionen
   #
   xPartition, yPartition = xypartition;
   if   (viertel == 1):
      xPartition = False;
      yPartition = False;
   elif (viertel == 2):
      xPartition = False;
   #
   partBoden = modell.parts[name];
   Grundkoerper_standardpartitionen(modell=modell, name=name,
      xPartition=xPartition, yPartition=yPartition, zPartition=False);
   #
   if (len(bodenbereich) > 1):
      _Boden_ebenenpartition(modell=modell, name=name, bodenbereich=bodenbereich,
         partition_durchziehen=partition_durchziehen, viertel=viertel);
   #
   _Boden_tiefenpartition(modell=modell, name=name, bodentiefe=bodentiefe,
      schichten=schichten, voidhoehe=voidhoehe);
#


# -------------------------------------------------------------------------------------------------
def _Boden_tiefenpartition(modell, name, bodentiefe, schichten, voidhoehe):
   """Erzeuge vertikale Partitionen am Bauteil (Part) name aus dem aktiven modell. Dazu wird jeder
   in schichten definierte Bereich ueber die bodentiefe partitioniert.
   """
   import part
   #
   partBoden = modell.parts[name];
   zachsenid = partBoden.features['zAchse'].id;
   #
   # Voidbereich (falls existent) und unterer Bodenbereich unterhalb der Schichten abgrenzen
   if (voidhoehe > 0.0):
      partBoden.DatumPointByCoordinate(coords=(0.0, 0.0, bodentiefe));
      partBoden.features.changeKey(fromName='Datum pt-1', toName='datum_GOK');
      partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
         normal=partBoden.datums[zachsenid],
         point=partBoden.datums[partBoden.features['datum_GOK'].id]);
   #
   # Alle Schichten erstellen und definieren
   for tiefe in schichten:
      if (tiefe < bodentiefe):
         datumname = 'datum_' + str(tiefe).replace(".","-") + 'm';
         partBoden.DatumPointByCoordinate(coords=(0.0, 0.0, bodentiefe-tiefe));
         partBoden.features.changeKey(fromName='Datum pt-1', toName=datumname);
         datumid = partBoden.features[datumname].id;
         partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
            normal=partBoden.datums[zachsenid], point=partBoden.datums[datumid]);
#


# -------------------------------------------------------------------------------------------------
def _Boden_ebenenpartition(modell, name, bodenbereich, partition_durchziehen=False, viertel=4):
   """Erzeuge Ebenenpartitionen am Bauteil (Part) name aus dem aktiven modell. Dazu werden je nach
   Elementen in bodenbereich runde (ein Wert) oder rechteckige (zwei Werte) Partitionen durch das
   gesamte Bauteils erstellt. Wenn nur ein Viertel- oder Halbmodell erzeugt worden ist, muss der
   Parameter viertel entsprechend angepasst uebergeben werden.
   """
   from hilfen import Log
   #
   partBoden = modell.parts[name];
   vorangegangenerbereich = bodenbereich[0];
   lenvoran = len(vorangegangenerbereich);
   # Arbeite Partitionsweise von aussen nach innen
   for idx, aktuellerbereich in enumerate(bodenbereich[1:]):
      lenaktuell = len(aktuellerbereich);
      aeste = False;
      
      # Da die aktuelle und die vorangegangene Partition entweder rechteckig
      # oder kreisfoermig sind, gibt es vier Faelle zu unterscheiden
      if ((not lenaktuell == 1) and (not lenaktuell == 2)):
         Log('# Fehler: Ungueltiger Wert in bodenbereich[' + str(idx) + ']');
         return;
      #
      # Falls partition_durchziehen = True und eine rechteckige Partition erstellt werden soll,
      # wird eine simplere Methode zur Erzeugung der noetigen Partitionen verwendet
      if ((partition_durchziehen) and (lenaktuell == 2)):
         _Ebenenpartition_durchziehen(modell=modell, name=name, partitionsname='Bereich' + str(idx),
            bereich=aktuellerbereich, viertel=viertel);
         continue;
      #
      if   ((lenaktuell == 2) and (lenvoran == 2)):
         # Rechteck -> kleineres Rechteck. Aeste hinzufuegen, wenn beide neuen Seiten echt kleiner
         if ((aktuellerbereich[0] > vorangegangenerbereich[0]) or (aktuellerbereich[1] > vorangegangenerbereich[1]) or
            ((aktuellerbereich[0] == vorangegangenerbereich[0]) and (aktuellerbereich[1] == vorangegangenerbereich[1]))):
            #
            Log('# Fehler: Rechteck-Partition in bodenbereich[' + str(idx) + '] muss kleiner sein als umgebendes Rechteck');
            return;
         #
         if ((aktuellerbereich[0] < vorangegangenerbereich[0]) and (aktuellerbereich[1] < vorangegangenerbereich[1])):
            aeste = True;
      elif ((lenaktuell == 1) and (lenvoran == 1)):
         # Kreis -> kleinerer Kreis, keine Aeste noetig
         if (aktuellerbereich[0] >= vorangegangenerbereich[0]):
            Log('# Fehler: Kreis-Partition in bodenbereich[' + str(idx) + '] muss kleiner sein als umgebender Kreis');
            return;
      elif ((lenaktuell == 2) and (lenvoran == 1)):
         # Kreis -> kleineres Rechteck, Aeste hinzufuegen, wenn Rechteck echt innerhalb des Kreises
         if ((aktuellerbereich[0]**2 + aktuellerbereich[1]**2) > vorangegangenerbereich[0]**2):
            Log('# Fehler: Rechteck-Partition in bodenbereich[' + str(idx) + '] muss kleiner sein als umgebender Kreis');
            return;
         if ((aktuellerbereich[0]**2 + aktuellerbereich[1]**2) < vorangegangenerbereich[0]**2):
            aeste = True;
      else:
         # Rechteck -> kleineren Kreis, immer Aeste hinzufuegen
         if ((aktuellerbereich[0] > vorangegangenerbereich[0]) or (aktuellerbereich[0] > vorangegangenerbereich[1])):
            Log('# Fehler: Kreis-Partition in bodenbereich[' + str(idx) + '] muss kleiner sein als umgebendes Rechteck');
            return;
         aeste = True;
      #
      _Ebenenpartition_erstellen(modell=modell, name=name, partitionsname='Bereich' + str(idx),
         bodenbereich_aussen=vorangegangenerbereich, bodenbereich_innen=aktuellerbereich,
         aeste=aeste, viertel=viertel);
      #   
      vorangegangenerbereich = aktuellerbereich;
      lenvoran = lenaktuell;
#


# -------------------------------------------------------------------------------------------------
def _Ebenenpartition_erstellen(modell, name, partitionsname, bodenbereich_aussen,
   bodenbereich_innen, aeste=False, viertel=4):
   """Definiere eine Ebenenpartitionen am Bauteil (Part) name aus dem aktiven modell. Die Partition
   wird mit partitionsname bezeichnet. Abhaengig von bodenbereich_innen und bodenbereich_aussen, die
   beide entweder kreisfoermig oder rechteckig sein koennen, wird die Partitionierung vorgenommen.
   Optional koennen aeste zur Verbindung der beiden Partitionen erzeugt werden. Wenn nur ein
   Viertel- oder Halbmodell erzeugt worden ist, muss der Parameter viertel entsprechend angepasst
   uebergeben werden.
   """
   import part
   from abaqusConstants import COPLANAR_EDGES, SIDE1, RIGHT, CLOCKWISE, FORWARD
   from math import sqrt
   from auswahl import BedingteAuswahl
   from hilfen import abapys_tol
   from zeichnung import Linie, Rechteck, Kreis, KreisbogenWinkel
   #
   partBoden = modell.parts[name];
   xachsenid = partBoden.features['xAchse'].id;
   yachsenid = partBoden.features['yAchse'].id;
   zachsenid = partBoden.features['zAchse'].id;
   flaecheUnterseite = BedingteAuswahl(elemente=partBoden.faces,
      bedingung='elem.pointOn[0][2] < var[0]', var=[abapys_tol]);
   #
   modell.ConstrainedSketch(gridSpacing=5, name='profil_' + partitionsname, sheetSize=40,
      transform=partBoden.MakeSketchTransform(sketchPlane=flaecheUnterseite[0],
      sketchPlaneSide=SIDE1, sketchUpEdge=partBoden.datums[xachsenid], sketchOrientation=RIGHT,
      origin=(0.0, 0.0, 0.0)));
   zeichnung = modell.sketches['profil_' + partitionsname];
   partBoden.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=zeichnung);
   if (len(bodenbereich_innen) == 1):
      if (viertel == 1):
         Linie(zeichnung=zeichnung, punkt1=(bodenbereich_innen[0], 0.0), punkt2=(0.0, 0.0));
         Linie(zeichnung=zeichnung, punkt1=(0.0, 0.0), punkt2=(0.0, bodenbereich_innen[0]));
         KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=bodenbereich_innen[0],
            startwinkel=0.0, endwinkel=90.0, richtung=CLOCKWISE);
      elif (viertel == 2):
         Linie(zeichnung=zeichnung, punkt1=(0.0, -bodenbereich_innen[0]),
            punkt2=(0.0, bodenbereich_innen[0]));
         KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=bodenbereich_innen[0],
            startwinkel=0.0, endwinkel=180.0, richtung=CLOCKWISE);
      else:
         Kreis(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=bodenbereich_innen[0]);
   else:
      # Moeglicherweise sind zwei der vier inneren Kanten identisch mit den aeusseren. Abaqus
      # handhabt die Skizze in dem Fall als zwei nicht zusammenhaengende Seiten, die auch in zwei
      # unterschiedlichen Schritten partitioniert werden muessen.
      identischeSeiten = False;
      if (len(bodenbereich_aussen) == 2):
         if ((bodenbereich_aussen[0] == bodenbereich_innen[0]) or
            (bodenbereich_aussen[1] == bodenbereich_innen[1])):
            #
            identischeSeiten = True;
      #
      if (not identischeSeiten):
         # Das neue Rechteck ist echt kleiner als das alte
         xstart = -bodenbereich_innen[0];
         ystart = -bodenbereich_innen[1];
         if ((viertel == 1) or (viertel == 2)):
            if (viertel == 1):
               ystart = 0.0;
            #
            xstart = 0.0;
         #
         Rechteck(zeichnung=zeichnung, punkt1=(-bodenbereich_innen[0], -bodenbereich_innen[1]),
            punkt2=(bodenbereich_innen[0], bodenbereich_innen[1]));
      else:
         # Zwei Seiten sind nicht kleiner und die anderen beiden muessen einzeln gezeichnet werden,
         # sofern viertel == 4
         #
         #   Fall 1                         #   Fall 2     ^ y
         #                                  #              |
         #              ^ y                 #          +---+---+
         #              |                   #          |   |   |
         #      +---+---+---+---+           #      (a) +...+...+
         #      |   :   |   :   |           #          |   |   |
         #    --+---+---+---+---+-->        #        --+---+---+-->
         #      |   :   |   :   |   x       #          |   |   |   x
         #      +---+---+---+---+           #      (b) +...+...+
         #              |                   #          |   |   |
         #         (b)     (a)              #          +---+---+
         #                                  #              |
         #
         # Erste Seite
         if (bodenbereich_aussen[0] > bodenbereich_innen[0]):
            # Fall 1(a)
            startx = bodenbereich_innen[0];
            stopx = bodenbereich_innen[0];
            starty = -bodenbereich_innen[1];
            stopy = bodenbereich_innen[1];
            if (viertel == 1):
               starty = 0.0;
         else:
            # Fall 2(a)
            startx = -bodenbereich_innen[0];
            stopx = bodenbereich_innen[0];
            starty = bodenbereich_innen[1];
            stopy = bodenbereich_innen[1];
            if ((viertel == 1) or (viertel == 2)):
               startx = 0.0;
         #
         Linie(zeichnung=zeichnung, punkt1=(startx, starty), punkt2=(stopx, stopy));
         #
         # Falls nur ein Viertel betrachtet wird oder eine Haelfte und einer der Partitionsseiten
         # parallel zur Schnittflaeche ist (und ausserhalb, d.h. im negativen),
         # gibt es fuer die zweite Seite nichts zu tun
         if ((viertel == 1) or ((viertel == 2) and (bodenbereich_aussen[0] > bodenbereich_innen[0]))):
            pass;
         else:
            # Vorgriff auf den Rest dieser Funktion, um effektiv die Funktion nach dieser else-Abfrage
            # erneut nutzen zu koennen
            temppartitionsname = partitionsname + '-a';
            neupartition = partBoden.PartitionFaceBySketch(faces=flaecheUnterseite,
               sketch=zeichnung, sketchUpEdge=partBoden.datums[xachsenid]);
            del zeichnung;
            partBoden.features.changeKey(fromName=neupartition.name, toName=temppartitionsname);
            neueKanten = BedingteAuswahl(elemente=partBoden.edges,
               bedingung='elem.featureName == \'' + temppartitionsname + '\'');
            partBoden.PartitionCellByExtrudeEdge(cells=partBoden.cells,
               edges=(neueKanten), line=partBoden.datums[zachsenid], sense=FORWARD);
            #
            # Erneutes Auswaehlen der Oberfleche
            flaecheUnterseite = BedingteAuswahl(elemente=partBoden.faces,
               bedingung='elem.pointOn[0][2] < var[0]', var=[abapys_tol]);
            partitionsname = partitionsname + '-b';
            modell.ConstrainedSketch(gridSpacing=5, name='profil_' + partitionsname, sheetSize=40,
               transform=partBoden.MakeSketchTransform(sketchPlane=flaecheUnterseite[0],
               sketchPlaneSide=SIDE1, sketchUpEdge=partBoden.datums[xachsenid],
               sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)));
            zeichnung = modell.sketches['profil_' + partitionsname];
            partBoden.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=zeichnung);
            #
            # Zweite Seite
            if (bodenbereich_aussen[0] > bodenbereich_innen[0]):
               # Fall 1(b)
               startx = -bodenbereich_innen[0];
               stopx = -bodenbereich_innen[0];
               starty = -bodenbereich_innen[1];
               stopy = bodenbereich_innen[1];
            else:
               # Fall 2(b)
               startx = -bodenbereich_innen[0];
               stopx = bodenbereich_innen[0];
               starty = -bodenbereich_innen[1];
               stopy = -bodenbereich_innen[1];
               if (viertel == 2):
                  startx = 0.0;
            #
            Linie(zeichnung=zeichnung, punkt1=(startx, starty), punkt2=(stopx, stopy));
   #
   neupartition = partBoden.PartitionFaceBySketch(faces=flaecheUnterseite,
      sketch=zeichnung, sketchUpEdge=partBoden.datums[xachsenid]);
   del zeichnung;
   partBoden.features.changeKey(fromName=neupartition.name, toName=partitionsname);
   # Alle neu erstellten Kanten des Feingitters finden und zum Extrudieren verwenden
   neueKanten = BedingteAuswahl(elemente=partBoden.edges,
      bedingung='elem.featureName == \'' + partitionsname + '\'');
   partBoden.PartitionCellByExtrudeEdge(cells=partBoden.cells,
      edges=(neueKanten), line=partBoden.datums[zachsenid], sense=FORWARD);
   #
   if (aeste):
      for idx in range(0, 4):
         # Vier Aeste zwischen den Uebergangsbereichen hinzufuegen
         # Die Vorzeichenzuweisung funktioniert aufgrund der Integer-Division
         xvz = (-1)**((idx+1)/2);
         yvz = (-1)**(idx/2);
         #
         # Falls nur ein Viertel- oder Halbbereich vorhanden ist, sollen auch
         # nur die gueltigen Partitionen erzeugt werden
         if ((viertel == 1) or (viertel == 2)):
            if (viertel == 1):
               if (yvz < 0.0):
                  continue;
            #
            if (xvz < 0.0):
               continue;
         #
         flaecheUnterseite = BedingteAuswahl(elemente=partBoden.faces,
            bedingung='elem.pointOn[0][2] < var[0]', var=[abapys_tol]);
         if (len(bodenbereich_aussen) == 1):
            p1 = [xvz*bodenbereich_aussen[0]/sqrt(2), yvz*bodenbereich_aussen[0]/sqrt(2)];
         else:
            p1 = [xvz*bodenbereich_aussen[0], yvz*bodenbereich_aussen[1]];
         #
         if (len(bodenbereich_innen) == 1):
            p2 = [xvz*bodenbereich_innen[0]/sqrt(2), yvz*bodenbereich_innen[0]/sqrt(2)];
         else:
            p2 = [xvz*bodenbereich_innen[0], yvz*bodenbereich_innen[1]];
         #
         name = partitionsname + '_Ast' + str(idx);
         modell.ConstrainedSketch(gridSpacing=5, name='profile_' + name, sheetSize=40,
            transform=partBoden.MakeSketchTransform(sketchPlane=flaecheUnterseite[0],
            sketchPlaneSide=SIDE1, sketchUpEdge=partBoden.datums[xachsenid], sketchOrientation=RIGHT,
            origin=(0.0, 0.0, 0.0)));
         zeichnung = modell.sketches['profile_' + name];
         partBoden.projectReferencesOntoSketch(
            filter=COPLANAR_EDGES, sketch=zeichnung);
         #
         Linie(zeichnung=zeichnung, punkt1=(p1[0], p1[1]), punkt2=(p2[0], p2[1]));
         astpartition = partBoden.PartitionFaceBySketch(faces=flaecheUnterseite,
            sketch=zeichnung, sketchUpEdge=partBoden.datums[xachsenid]);
         del zeichnung;
         partBoden.features.changeKey(fromName=astpartition.name, toName='Ast-Partition');
         #
         neueKanten = BedingteAuswahl(elemente=partBoden.edges,
            bedingung='elem.featureName == \'Ast-Partition\'');
         partBoden.PartitionCellByExtrudeEdge(cells=partBoden.cells,
            edges=(neueKanten),line=partBoden.datums[zachsenid], sense=FORWARD);
         partBoden.features.changeKey(fromName='Ast-Partition', toName=name);
#


# -------------------------------------------------------------------------------------------------
def _Ebenenpartition_durchziehen(modell, name, partitionsname, bereich, viertel=4):
   """Erzeuge Ebenenpartition(en) an einem Bauteil, d.h. ueber Partitionen senkrecht zur x- und y-
   Richtung, die sich voll durch das Bauteil (Part) name aus dem aktiven modell ziehen. Die
   Partitionen enthalten das Namenspraefix partitionsname und sind definiert an den in bereich
   uebergebenen x- und y-Koordinaten. Wenn nur ein Viertel- oder Halbmodell erzeugt worden ist, muss
   der Parameter viertel entsprechend angepasst uebergeben werden, damit nur die realisierbaren
   Partitionen erzeugt werden.
   """
   import part
   #
   partBoden = modell.parts[name];
   xachsenid = partBoden.features['xAchse'].id;
   yachsenid = partBoden.features['yAchse'].id;
   xkoord, ykoord = bereich;
   #
   xpartition = partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
      normal=partBoden.datums[xachsenid], point=(xkoord, ykoord, 0.0));
   partBoden.features.changeKey(fromName=xpartition.name, toName=partitionsname + '_x1');
   #
   ypartition = partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
      normal=partBoden.datums[yachsenid], point=(xkoord, ykoord, 0.0));
   partBoden.features.changeKey(fromName=ypartition.name, toName=partitionsname + '_y1');
   #
   if ((not (viertel == 1)) and (not (viertel == 2))):
      xpartition = partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
         normal=partBoden.datums[xachsenid], point=(-xkoord, -ykoord, 0.0));
      partBoden.features.changeKey(fromName=xpartition.name, toName=partitionsname + '_x2');
   #
   if (not (viertel == 1)):
      ypartition = partBoden.PartitionCellByPlanePointNormal(cells=partBoden.cells,
         normal=partBoden.datums[yachsenid], point=(-xkoord, -ykoord, 0.0));
      partBoden.features.changeKey(fromName=ypartition.name, toName=partitionsname + '_y2');
#


# -------------------------------------------------------------------------------------------------
def _Boden_setserstellen(modell, name, bodentiefe, voidhoehe, bodenbereich, schichten,
   schichtmaterial, restmaterial):
   """Erzeuge alle relevanten Sets am Bauteil (Part) name aus dem aktiven modell. Dazu werden die
   folgenden Parameter fuer eine richtige Zuweisung der Sets erwartet: Die Bauteilhoehe, die sich
   aus bodentiefe und voidhoehe zusammensetzt, wobei bodentiefe zusaetzlich in einzelne schichten
   unterteilt ist. Um Sets aus gleichen Materialien zu erstellen, werden zusaetzlich die
   Bezeichnungen in schichtmaterial und restmaterial benoetigt. In jeder Ebene wird die Unterteilung
   mit bodenbereich definiert.
   """
   import part
   from auswahl import BedingteAuswahl
   from hilfen import abapys_tol, Log
   #
   partBoden = modell.parts[name];
   # Sets
   partBoden.Set(name='setAll', cells=partBoden.cells);
   if (voidhoehe > 0.0):
      zellenVoid = BedingteAuswahl(elemente=partBoden.cells,
         bedingung='elem.pointOn[0][2] >= var[0]', var=[bodentiefe]);
      partBoden.Set(name='setVoid', cells=zellenVoid);
      zellenNotVoid = BedingteAuswahl(elemente=partBoden.cells,
         bedingung='elem.pointOn[0][2] < var[0]', var=[bodentiefe]);
      partBoden.Set(name='setNotVoid', cells=zellenNotVoid);
   #
   # FIXME: Aktuell werden noch Warnungen von Abaqus ausgegeben, auch wenn es scheint, dass alles
   #        funktioniert wie erwartet. Nach dem aktuellen Stand koennen alle Warnungen mit der
   #        folgenden Ausgabe aus Vergleichen zu elemente[0:0] ignoriert werden:
   #           RuntimeWarning: tp_compare didn't return -1, 0 or 1
   xZellen = BedingteAuswahl(elemente=partBoden.cells, bedingung='elem.pointOn[0][0] < 0.0');
   if (not (xZellen == partBoden.cells[0:0])):
      partBoden.Set(name='setXBereich', cells=xZellen);
   #
   yZellen = BedingteAuswahl(elemente=partBoden.cells, bedingung='elem.pointOn[0][1] < 0.0');
   if (not (yZellen == partBoden.cells[0:0])):
      partBoden.Set(name='setYBereich', cells=yZellen);
   #   
   # Sets aller Materialien (Bereiche) definieren
   # Verschiedene Materialien (ohne doppelte Eintraege)
   if (schichten[-1] == bodentiefe):
      tempSchichten = [0.0] + schichten;
      tempSchichtmaterial = schichtmaterial;
   else:
      tempSchichten = [0.0] + schichten + [bodentiefe];
      tempSchichtmaterial = schichtmaterial + [restmaterial];
   #
   materialien = list(set(tempSchichtmaterial));
   zellen_Schichtmaterial = [partBoden.cells[0:0] for x in materialien];
   for idxSchicht, schichttiefe in enumerate(tempSchichten):
      if (idxSchicht == 0):
         continue;
      # FIXME: pointOn der Zellen ist manchmal auf der Randflaeche - welche? Eindeutig bestimmbar?
      #        Ueber Randflaechen gehen - min. vier muessen in der ebene sein?
      # FIXME: 2020-02-20: Unterscheidung zwischen unterster Schicht und Rest bei Auswahl
      #        vorher: '(elem.pointOn[0][2] >= var[0]) and (elem.pointOn[0][2] <= var[1])'
      if (idxSchicht == len(tempSchichten)-1):
         bedingung = '(elem.pointOn[0][2] >= var[0]) and (elem.pointOn[0][2] <= var[1])';
      else:
         bedingung = '(elem.pointOn[0][2] > var[0]) and (elem.pointOn[0][2] <= var[1])';
      #
      tempZellen = BedingteAuswahl(elemente=partBoden.cells, bedingung=bedingung,
         var=[bodentiefe-tempSchichten[idxSchicht], bodentiefe-tempSchichten[idxSchicht-1]]);
      if (not (tempZellen == partBoden.cells[0:0])):
         partBoden.Set(name='setSchicht' + str(idxSchicht).zfill(2), cells=tempZellen);
         #
         for idx, tempMaterial in enumerate(materialien):
            if (tempMaterial == tempSchichtmaterial[idxSchicht-1]):
               zellen_Schichtmaterial[idx] += tempZellen;
               break;
   #
   for idx, zellen in enumerate(zellen_Schichtmaterial):
      if ((not (zellen == partBoden.cells[0:0])) and (not materialien[idx] == '-')):
         partBoden.Set(name='set' + materialien[idx], cells=zellen);
   #
   flaechen_ZX = BedingteAuswahl(elemente=partBoden.faces,
      bedingung='(abs(elem.pointOn[0][0]) <= var[0])', var=[abapys_tol]);
   partBoden.Set(faces=flaechen_ZX, name='set_ZX');
   flaechen_ZY = BedingteAuswahl(elemente=partBoden.faces,
      bedingung='(abs(elem.pointOn[0][1]) <= var[0])', var=[abapys_tol]);
   partBoden.Set(faces=flaechen_ZY, name='set_ZY');
   #
   if (len(bodenbereich[-1]) == 1):
      innererBereich = BedingteAuswahl(elemente=partBoden.cells,
         bedingung='(sqrt(elem.pointOn[0][0]**2 + elem.pointOn[0][1]**2) < var[0]+var[1])',
         var=[bodenbereich[-1][0], abapys_tol]);
   else:
      innererBereich = BedingteAuswahl(elemente=partBoden.cells,
         bedingung='(abs(elem.pointOn[0][0]) < var[0]+var[2]) and (abs(elem.pointOn[0][1]) < var[1]+var[2])',
         var=[bodenbereich[-1][0], bodenbereich[-1][1], abapys_tol]);
   #
   partBoden.Set(name='setInnererBereich', cells=innererBereich);
#


# -------------------------------------------------------------------------------------------------
def _Boden_vernetzen(modell, name, bodentiefe, voidhoehe, bodenbereich, gittergroessen,
   gitter_boden_vertikal, schichten, extrasets=False, netz=True, euler=True, kernSweep=False):
   """Erzeuge das Gitternetz am Bauteil (Part) name aus dem aktiven modell. Dazu werden neben der
   Bauteilhoehe, die sich aus bodentiefe und voidhoehe zusammensetzt, auch die Anordnung in der
   Ebene in bodenbereich benoetigt. Die dazugehoerigen gittergroessen beziehen sich auf die
   definierte Ebenen in bodenbereich, waehrend gitter_boden_vertikal die vertikale Netzfeinheit von
   voidhoehe bis zu der tiefsten Ebene in schichten bestimmt. Optional koennen extrasets der Kanten
   fuer die Netzbestimmung erstellt werden. Optional kann setInnererBereich mit kernSweep == True
   als Sweep statt als Structured Mesh erstellt werden.
   """
   import part
   import mesh
   from abaqusConstants import C3D8, C3D6, C3D4, EC3D8R, UNKNOWN_TET, UNKNOWN_WEDGE
   from abaqusConstants import DEFAULT, STANDARD, EXPLICIT, OFF, FINER, ADVANCING_FRONT, SWEEP
   from abaqusConstants import SINGLE, STRAIN, AVERAGE_STRAIN
   from auswahl import BedingteAuswahl, ZweifachbedingteKantenAuswahl
   from hilfen import abapys_tol, Log 
   #
   # Die Hoehe des nicht mehr fein vernetzten Bodenkoerpers
   tiefe_uebergang = bodentiefe - schichten[-1]
   
   # Elementtypen und HourglassControl anpassen
   partBoden = modell.parts[name];
   if (euler):
      partBoden.setElementType(elemTypes=(
         mesh.ElemType(elemCode=EC3D8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF), # hourglassControl=STIFFNESS
         mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT),
         mesh.ElemType(elemCode=UNKNOWN_TET, elemLibrary=EXPLICIT)),
         regions=partBoden.sets['setAll']);
   else:
      partBoden.setElementType(elemTypes=(
         mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD, secondOrderAccuracy=OFF, distortionControl=DEFAULT),
         mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD),
         mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)),
         regions=partBoden.sets['setAll']);
   #
   if (kernSweep):
      # MEDIAL_AXIS, ADVANCING_FRONT
      partBoden.setMeshControls(regions=partBoden.sets['setInnererBereich'].cells,
         technique=SWEEP, algorithm=ADVANCING_FRONT);
   #
   # Mesh
   # --- Unterteilung in mehrere Teilbereiche
   # 1) kanten_Untenvertikal
   #      Alle vertikalen Linien unterhalb von schichten[-1]
   # 2) kanten_Schichten
   #    a) Flaechen/Aussenseite
   #      Alle Flaechen deren Normale keinen Vertikalanteil hat, die eine bodenbereich-Partition umgrenzen
   #    b) Verbindungen
   #      Horizontale Linien zwischen zwei bodenbereich-Partitionen
   # 3) kanten_Schichtvertikal
   #      Alle vertikalen Linien oberhalb von schichten[-1]
   #
   # Globale Seeds vorgeben (v.a. fuer alle nicht im Folgenden explizit definierte Bereiche)
   partBoden.seedPart(size=gittergroessen[0][0], deviationFactor=0.1, minSizeFactor=0.1);
   #
   # 1) kanten_Untenvertikal (Alle vertikalen Linien unterhalb von schichten[-1])
   if (not (bodentiefe == schichten[-1])):
      kanten_Untenvertikal = ZweifachbedingteKantenAuswahl(elemente=partBoden,
         bedingung1='(edge.pointOn[0][2] >= var[0]) and (edge.pointOn[0][2] < var[1]-var[0])',
         bedingung2='not ((vert1.pointOn[0][2]) == (vert2.pointOn[0][2]))',
         bedingung3='(vert1.pointOn[0][2]) < (vert2.pointOn[0][2])',
         var=[abapys_tol, tiefe_uebergang]);
      if (len(gittergroessen[0]) == 1):
         partBoden.seedEdgeBySize(constraint=FINER, deviationFactor=0.1,
            edges=kanten_Untenvertikal[0]+kanten_Untenvertikal[1], minSizeFactor=0.1,
            size=gittergroessen[0][0]);
      else:
         partBoden.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER,
            end1Edges=kanten_Untenvertikal[1], end2Edges=kanten_Untenvertikal[0],
            maxSize=gittergroessen[0][0], minSize=gitter_boden_vertikal);
      #
      if (extrasets):
         partBoden.Set(edges=kanten_Untenvertikal, name='setK_Untenvertikal');
   #
   # 2) kanten_Schichten
   for idx, aktuellerbereich in enumerate(bodenbereich):
      # a) Flaechen/Aussenseite (Alle Flaechen deren Normale keinen Vertikalanteil hat,
      #                          die eine bodenbereich-Partition umgrenzen)
      if (len(bodenbereich[idx]) == 1):
         # Kontur eines Kreises mit Liniendicke abapys_tol
         kanten_Schichtflaeche = BedingteAuswahl(elemente=partBoden.edges,
            bedingung='(abs(sqrt(elem.pointOn[0][0]**2 + elem.pointOn[0][1]**2) - var[0]) < var[2]) and (elem.pointOn[0][2] > var[1]-var[2])',
            var=[bodenbereich[idx][0], tiefe_uebergang, abapys_tol]);
      else:
         # Kontur eines Rechtecks mit Liniendicke abapys_tol
         kanten_Schichtflaeche = BedingteAuswahl(elemente=partBoden.edges,
            bedingung='(elem.pointOn[0][2] > var[2]-var[3]) and (abs(elem.pointOn[0][0]) < var[0]+var[3]) and (abs(elem.pointOn[0][1]) < var[1]+var[3]) and (not ((abs(elem.pointOn[0][0]) < var[0]-var[3]) and (abs(elem.pointOn[0][1]) < var[1]-var[3])))',
            var=[bodenbereich[idx][0], bodenbereich[idx][1], tiefe_uebergang, abapys_tol]);
      #
      partBoden.seedEdgeBySize(constraint=FINER, deviationFactor=0.1,
         edges=kanten_Schichtflaeche, minSizeFactor=0.1, size=gittergroessen[idx][0]);
      #
      if (extrasets):
         partBoden.Set(edges=kanten_Schichtflaeche, name='setK_Schichtflaeche' + str(idx));
      #
      # b) Verbindungen (Horizontale Linien zwischen zwei bodenbereich-Partitionen)
      if (idx < len(bodenbereich)-1):
         # Irgendein Uebergangsbereich
         naechsterbereich = bodenbereich[idx+1];
         if (len(naechsterbereich) == 1):
            if (len(bodenbereich[idx]) == 1):
               # Kreis zu kleinerem Kreis
               kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
                  bedingung1='(sqrt(edge.pointOn[0][0]**2 + edge.pointOn[0][1]**2) < var[0]-var[2])',
                  bedingung2='(sqrt(edge.pointOn[0][0]**2 + edge.pointOn[0][1]**2) > var[1]+var[2])',
                  bedingung3='(vert1.pointOn[0][0]**2 + vert1.pointOn[0][1]**2) > (vert2.pointOn[0][0]**2 + vert2.pointOn[0][1]**2)',
                  var=[bodenbereich[idx][0], naechsterbereich[0], abapys_tol]);
            else:
               # Rechteck zu kleinerem Kreis
               kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
                  bedingung1='(abs(edge.pointOn[0][0]) < var[0]-var[3]) and (abs(edge.pointOn[0][1]) < var[1]-var[3])',
                  bedingung2='(sqrt(edge.pointOn[0][0]**2 + edge.pointOn[0][1]**2) > var[2]+var[3])',
                  bedingung3='(vert1.pointOn[0][0]**2 + vert1.pointOn[0][1]**2) > (vert2.pointOn[0][0]**2 + vert2.pointOn[0][1]**2)',
                  var=[bodenbereich[idx][0], bodenbereich[idx][1], naechsterbereich[0], abapys_tol]);
         else:
            if (len(bodenbereich[idx]) == 1):
               # Kreis zu kleinerem Rechteck
               kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
                  bedingung1='(sqrt(edge.pointOn[0][0]**2 + edge.pointOn[0][1]**2) < var[0]-var[3])',
                  bedingung2='(not ((abs(edge.pointOn[0][0]) < var[1]+var[3]) and (abs(edge.pointOn[0][1]) < var[2]+var[3])))',
                  bedingung3='(vert1.pointOn[0][0]**2 + vert1.pointOn[0][1]**2) > (vert2.pointOn[0][0]**2 + vert2.pointOn[0][1]**2)',
                  var=[bodenbereich[idx][0], naechsterbereich[0], naechsterbereich[1], abapys_tol]);
            else:
               # Rechteck zu kleinerem Rechteck
               tol_laenge = abapys_tol;
               tol_breite = abapys_tol;
               if (bodenbereich[idx][0] == naechsterbereich[0]):
                  tol_laenge = -abapys_tol;
               if (bodenbereich[idx][1] == naechsterbereich[1]):
                  tol_breite = -abapys_tol;
               kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
                  bedingung1='(abs(edge.pointOn[0][0]) < var[0]-var[4]) and (abs(edge.pointOn[0][1]) < var[1]-var[5])',
                  bedingung2='(not ((abs(edge.pointOn[0][0]) < var[2]+var[4]) and (abs(edge.pointOn[0][1]) < var[3]+var[5])))',
                  bedingung3='(vert1.pointOn[0][0]**2 + vert1.pointOn[0][1]**2) > (vert2.pointOn[0][0]**2 + vert2.pointOn[0][1]**2)',
                  var=[bodenbereich[idx][0], bodenbereich[idx][1], naechsterbereich[0], naechsterbereich[1], tol_laenge, tol_breite]);
      #
      else:
         # Innerster Bereich
         if (len(bodenbereich[idx]) == 1):
            kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
               bedingung1='(sqrt(edge.pointOn[0][0]**2 + edge.pointOn[0][1]**2) < var[0]-var[1])',
               bedingung2='(not (((abs(edge.pointOn[0][0]) < var[1]) and ((abs(edge.pointOn[0][1]) < var[1])))))',
               bedingung3='(vert1.pointOn[0][2]) < (vert2.pointOn[0][2])',
               var=[bodenbereich[idx][0], abapys_tol]);
         else:
            kanten_Schichtverbindung = ZweifachbedingteKantenAuswahl(elemente=partBoden,
               bedingung1='((edge.pointOn[0][0]) > -var[0]+var[2]) and ((edge.pointOn[0][0]) < var[0]-var[2]) and ((edge.pointOn[0][1]) > -var[1]+var[2]) and ((edge.pointOn[0][1]) < var[1]-var[2])',
               bedingung2='(not ((abs(edge.pointOn[0][0]) < var[2]) and (abs(edge.pointOn[0][1]) < var[2])))',
               bedingung3='(vert1.pointOn[0][2]) < (vert2.pointOn[0][2])',
               var=[bodenbereich[idx][0], bodenbereich[idx][1], abapys_tol]);
      #
      kanten = kanten_Schichtverbindung[0] + kanten_Schichtverbindung[1];
      if (not (kanten == partBoden.edges[0:0])):
         if (len(gittergroessen[idx]) == 1):
            partBoden.seedEdgeBySize(constraint=FINER, deviationFactor=0.1,
               edges=kanten, minSizeFactor=0.1,
               size=gittergroessen[idx][0]);
         else:
            partBoden.seedEdgeByBias(biasMethod=SINGLE, constraint=FINER,
               end1Edges=kanten_Schichtverbindung[1], end2Edges=kanten_Schichtverbindung[0],
               maxSize=gittergroessen[idx][0], minSize=gittergroessen[idx][1]);
         #
         if (extrasets):
            partBoden.Set(edges=kanten, name='setK_Schichtverbindung' + str(idx));
   #
   # 3) kanten_Schichtvertikal (Alle vertikalen Linien oberhalb von schichten[-1])
   kanten_Schichtvertikal = ZweifachbedingteKantenAuswahl(elemente=partBoden,
      bedingung1='edge.pointOn[0][2] > var[0]-var[1]', bedingung2='not ((vert1.pointOn[0][2]) == (vert2.pointOn[0][2]))',
      var=[tiefe_uebergang, abapys_tol]);
   partBoden.seedEdgeBySize(constraint=FINER, deviationFactor=0.1,
      edges=kanten_Schichtvertikal[0], minSizeFactor=0.1,
      size=gitter_boden_vertikal);
   if (extrasets):
      partBoden.Set(edges=kanten_Schichtvertikal, name='setK_Schichtvertikal');
   #
   if (netz):
      partBoden.generateMesh();
      if (len(partBoden.elements) == 0 ):
         Log('# Warnung: Mesh-Erstellung zu ' + name + ' fehlgeschlagen');
#


# -------------------------------------------------------------------------------------------------
def BodenspannungErstellen(modell, bodenname, nullspannung, voidhoehe, schichten, bodentiefe,
   materialschichten, verwendeteBodenwerte, verwendeteMaterialien, verbose=False):
   """Erzeuge im modell fuer den Bodenkoerper bodenname eine Bodenspannungsverteilung (in z-Richtung
   mit GOK bei z=0). Nutze dazu eine konstante Vorbelastung nullspannung fuer den Voidbereich der
   Hoehe voidhoehe. Fuer jede Schicht der uebergebenen schichten bis bodentiefe werden ueber die
   Bezeichnungen in materialschichten die verwendeteBodenwerte fuer verwendeteMaterialien
   zugewiesen. Optional kann eine Infoausgabe mit verbose=True erstellt werden.
   """
   from hilfen import g, Log
   #
   if (voidhoehe > 0.0) and (not (nullspannung == 0.0)):
      if (modell.rootAssembly.instances['inst' + bodenname].sets.has_key('setVoid')):
         modell.GeostaticStress(lateralCoeff1=0.5, lateralCoeff2=None, name='SpannungVoid',
            region=modell.rootAssembly.instances['inst' + bodenname].sets['setVoid'], 
            stressMag1=-nullspannung, vCoord1=voidhoehe, stressMag2=-nullspannung, vCoord2=0.0);
   #
   if (schichten[-1] == bodentiefe):
      tempSchichten = [0.0] + schichten;
   else:
      tempSchichten = [0.0] + schichten + [bodentiefe];
   #
   spannung_ende = nullspannung;
   idxMat = 0;
   if (verbose):
      Log('# Index      Material       Endtiefe   Bodenspg      K0       Dichte\n' \
          '# ------|-----------------|----------|----------|----------|----------');
   #
   for idxSchicht, schichttiefe in enumerate(tempSchichten):
      if (idxSchicht == 0):
         continue;
      # FIXME: Auch ungueltige Materialien sinnvoll handhaben
      for idxMaterial, tempMaterial in enumerate(verwendeteMaterialien):
         if (tempMaterial == materialschichten[idxSchicht-1]):
            idxMat = idxMaterial;
            break;
      #
      tempBodendichte = verwendeteBodenwerte[idxMat][0];
      tempBodenschichtK0 = verwendeteBodenwerte[idxMat][1];
      #
      numSchicht = str(idxSchicht).zfill(2);
      name = 'Bodenspannung' + numSchicht;
      spannung_start = spannung_ende;
      spannung_ende = spannung_start + tempBodendichte*g*(schichttiefe-tempSchichten[idxSchicht-1]);
      #
      if (verbose):
         Log('# {:3d}     {:>15}   {:7.3f}    {:7.3f}    {:7.3f}    {:7.3f}'.format(idxSchicht,
            tempMaterial, schichttiefe, spannung_ende, tempBodenschichtK0, tempBodendichte));
      #
      modell.GeostaticStress(lateralCoeff1=tempBodenschichtK0, lateralCoeff2=None, name=name,
         region=modell.rootAssembly.instances['inst' + bodenname].sets['setSchicht' + numSchicht], 
         stressMag1=-spannung_start, vCoord1=-tempSchichten[idxSchicht-1],
         stressMag2=-spannung_ende, vCoord2=-schichttiefe);
#


# -------------------------------------------------------------------------------------------------
def BodenspannungDirektZuweisen(modell, bodenname, nullspannung, voidhoehe, schichten, bodentiefe,
   bodendichten, k0Werte):
   """Erzeuge im modell fuer den Bodenkoerper bodenname eine Bodenspannungsverteilung (in z-Richtung
   mit GOK bei z=0). Nutze dazu eine konstante Vorbelastung nullspannung fuer den Voidbereich der
   Hoehe voidhoehe. Fuer jede Schichttiefe in schichten bis bodentiefe werden die uebergebenen Werte
   aus bodendichten und k0Werte direkt zugewiesen.
   """
   from hilfen import g
   #
   if (voidhoehe > 0.0) and (not (nullspannung == 0.0)):
      if (modell.rootAssembly.instances['inst' + bodenname].sets.has_key('setVoid')):
         modell.GeostaticStress(lateralCoeff1=0.5, lateralCoeff2=None, name='SpannungVoid',
            region=modell.rootAssembly.instances['inst' + bodenname].sets['setVoid'], 
            stressMag1=-nullspannung, vCoord1=voidhoehe, stressMag2=-nullspannung, vCoord2=0.0);
   #
   if (schichten[-1] == bodentiefe):
      tempSchichten = [0.0] + schichten;
   else:
      tempSchichten = [0.0] + schichten + [bodentiefe];
   #
   spannung_ende = nullspannung;
   for idxSchicht, schichttiefe in enumerate(tempSchichten):
      if (idxSchicht == 0):
         continue;
      #
      tempBodendichte = bodendichten[idxSchicht-1];
      tempBodenschichtK0 = k0Werte[idxSchicht-1];
      #
      numSchicht = str(idxSchicht).zfill(2);
      name = 'Bodenspannung' + numSchicht;
      spannung_start = spannung_ende;
      spannung_ende = spannung_start + tempBodendichte*g*(schichttiefe-tempSchichten[idxSchicht-1]);
      modell.GeostaticStress(lateralCoeff1=tempBodenschichtK0, lateralCoeff2=None, name=name,
         region=modell.rootAssembly.instances['inst' + bodenname].sets['setSchicht' + numSchicht], 
         stressMag1=-spannung_start, vCoord1=-tempSchichten[idxSchicht-1],
         stressMag2=-spannung_ende, vCoord2=-schichttiefe);
#


# -------------------------------------------------------------------------------------------------
def BodenmaterialUndSectionErstellen(modell, verwendeteMaterialien, verfuegbareMaterialien,
   userroutine='', numDepVar=0, euler=True):
   """Erstelle im modell je nach euler eine EulerianSection oder mehrere HomogeneousSolidSections
   mit allen verwendeteMaterialien. Die Abfolge der Materialschichten wird mit der Reihenfolge in
   verfuegbareMaterialien festgelegt. Falls ein Stoffgesetz eine Userroutine benoetigt, muss die
   Bezeichnung userroutine und die Anzahl der Rueckgabevariablen numDepVar uebergeben werden.
   Gibt [benoetigtUserroutine, verwendeteBodenwerte] zurueck.
   
   Jeder Eintrag von verfuegbareMaterialien enthaelt:
      [abqbodenname, dbbodenname, <optional: dbbodenbez,> saettigung, verdichtungsgrad, stoffgesetz]
   """
   from math import sin
   import material
   import section
   from abaqusConstants import OFF
   from hilfen import Log
   from bodendatenbank import Bodenparameter
   #
   # Da die Liste verwendeteMaterialien nicht sortiert ist und einzelne Eintraege von
   # verwendeteBodenwerte direkt geschrieben werden sollen, wird verwendeteBodenwerte schon
   # vorinitialisiert
   for benoetigtesMaterial in verwendeteMaterialien:
      material_definiert = False;
      for material in verfuegbareMaterialien:
         if (benoetigtesMaterial == material[0]):
            material_definiert = True;
            break;
      #
      if (not material_definiert):
         Log('# Abbruch: Verwendetes Material ' + benoetigtesMaterial + ' nicht in verfuegbarenMaterialien definiert');
         return [None, None];
   #
   verwendeteBodenwerte = [[0.0, 0.5]]*len(verwendeteMaterialien);
   benoetigtUserroutine = False;
   dictMaterials = {};
   for parametersatz in verfuegbareMaterialien:
      neuesMaterial = False;
      dbbodenbez = '';
      if (len(parametersatz) == 5):
         abqbodenname, dbbodenname, saettigung, verdichtungsgrad, stoffgesetz = parametersatz;
      elif (len(parametersatz) == 6):
         abqbodenname, dbbodenname, dbbodenbez, saettigung, verdichtungsgrad, stoffgesetz = parametersatz;
      else:
         Log('# Abbruch: Jedes Material in verfuegbareMaterialien muss 5 oder 6 Eintraege haben');
         return [None, None];
      #
      idxBodenwert = 0;
      for idxMaterial, verwendetesMaterial in enumerate(verwendeteMaterialien):
         if (abqbodenname == verwendetesMaterial):
            neuesMaterial = True;
            idxBodenwert = idxMaterial;
            break;
      #
      if (not neuesMaterial):
         continue;
      #
      korndichte = 2.65; # t/m^3   Korndichte
      dichte_wasser = 1.0; # t/m^3
      tempBodenparameter = Bodenparameter(name=dbbodenname, stoffgesetz=stoffgesetz,
         bezeichnung=dbbodenbez);
      if (tempBodenparameter is None):
         Log('# Abbruch: Fehler beim Laden der Materialdaten');
         return [None, None];
      #
      mindichte, maxdichte, kritReibwinkel = tempBodenparameter[0:3];
      #
      trockendichte = mindichte + verdichtungsgrad*(maxdichte-mindichte);
      aktuelleporenzahl = korndichte/trockendichte - 1.0;
      tempBodenschichtdichte = trockendichte \
                             + saettigung * aktuelleporenzahl/(1+aktuelleporenzahl) * dichte_wasser;
      #
      tempBodenschichtK0 = 1.0 - sin(kritReibwinkel);
      verwendeteBodenwerte[idxBodenwert] = [tempBodenschichtdichte, tempBodenschichtK0];
      #
      modell.Material(name=abqbodenname);
      tempBoden = modell.materials[abqbodenname];
      tempBoden.Density(table=((tempBodenschichtdichte, ), ));
      #
      if (stoffgesetz[-6:] == '-StdIG'):
         stoffgesetz = stoffgesetz[:-6];
      if (stoffgesetz[-7:] == '-OhneIG'):
         stoffgesetz = stoffgesetz[:-7];
      #
      if   (stoffgesetz == 'Elastisch'):
         tempBoden.Elastic(table=((tempBodenparameter[3], tempBodenparameter[4]), ));
      elif (stoffgesetz == 'Mohr-Coulomb'):
         tempBoden.Elastic(table=((tempBodenparameter[3], tempBodenparameter[4]), ));
         tempBoden.MohrCoulombPlasticity(table=((tempBodenparameter[5], tempBodenparameter[6]), ));
         tempBoden.mohrCoulombPlasticity.MohrCoulombHardening(
            table=((tempBodenparameter[7], tempBodenparameter[8]), ));
         tempBoden.mohrCoulombPlasticity.TensionCutOff(
            dependencies=0, table=((0.0, 0.0), ), temperatureDependency=OFF);
      elif (stoffgesetz == 'Hypoplastisch'):
         benoetigtUserroutine = True;
         # Fuer die visco_hypo-Routinen ist die Anfangsporenzahl an 15. Stelle (und 16. egal),
         # bei den anderen an der 16. Stelle (und 15. egal)
         if (userroutine[0:5] == 'visco'):
            tempBoden_hp = tuple(tempBodenparameter[2:] + [aktuelleporenzahl, 0.0]);
         else:
            tempBoden_hp = tuple(tempBodenparameter[2:] + [0.0, aktuelleporenzahl]);
         #
         tempBoden.Depvar(n=numDepVar);
         tempBoden.UserMaterial(mechanicalConstants=tempBoden_hp);
      elif (stoffgesetz == 'Viskohypoplastisch'):
         benoetigtUserroutine = True;
         tempBoden_hp = tuple(tempBodenparameter[3:10] + tempBodenparameter[2:3] + tempBodenparameter[10:] + [0.0]);
         tempBoden.Depvar(n=numDepVar);
         tempBoden.UserMaterial(mechanicalConstants=tempBoden_hp);
      #
      if (euler):
         dictMaterials['imat' + abqbodenname] = abqbodenname;
      else:
         modell.HomogeneousSolidSection(material=abqbodenname, name='sec' + abqbodenname,
            thickness=None);
   #
   if (euler):
      modell.EulerianSection(data=dictMaterials, name='secEuler');
   #
   return [benoetigtUserroutine, verwendeteBodenwerte];
#
