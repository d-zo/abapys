# -*- coding: utf-8 -*-
"""
beatify.py   v0.65 (2020-11)
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
def ViewportVerschoenern(session, neuerHintergrund=True, saubererViewport=True, saubereLegende=True,
   evfSchnitt=False, minimaleKanten=True, farbspektrum='Viridis', diskreteFarben=True,
   ausgabeVerschmieren=True, zeigeMarkierungen=True, exportiereHintergrund=False,
   Standardansicht=False):
   """Wende die in dieser Funktion gespeicherten Standardwerte fuer die Ansicht des aktiven
   Viewports der session an. Optional koennen verschiedene Effekte aktiviert oder deaktiviert
   werden. Fuer farbspektrum sind die folgenden Spektren definiert: abpViridis, abpCubeHelix,
   abpRainbow und abpMoreland sowie deren Inverse (abpViridisINV, abpCubeHelixINV, abpRainbowINV und
   abpMorelandINV). Gibt einen Verweis auf den viewport zurueck.
   """
   # Basiert hauptsaechlich auf dem Abaqus Scripting Reference Guide (Abschnittstitel und -nummern
   # aus der Version 6.14 sowie
   # http://ifcuriousthenlearn.com/blog/2015/04/02/Abaqus-FEA-Scripting-with-python/
   # http://desicos.github.io/desicos/_modules/desicos/abaqus/abaqus_functions.html
   #
   import visualization
   from abaqusConstants import FIXED, TRUE, FALSE, ON, OFF, FEATURE, SPECIFY, CONTINUOUS
   from abaqusConstants import PARALLEL, MODEL, ABSOLUTE
   from hilfen import Log
   #
   myviewport = session.viewports[session.currentViewportName];
   #
   if ((not isinstance(neuerHintergrund, bool)) or (not isinstance(saubererViewport, bool)) or
      (not isinstance(saubereLegende, bool)) or(not isinstance(evfSchnitt, bool)) or
      (not isinstance(minimaleKanten, bool)) or(not isinstance(diskreteFarben, bool)) or
      (not isinstance(ausgabeVerschmieren, bool)) or(not isinstance(zeigeMarkierungen, bool)) or
      (not isinstance(exportiereHintergrund, bool)) or(not isinstance(Standardansicht, bool))):
      Log('# Abbruch: Alle Argumente ausser session und farbspektrum muessen True/False sein');
      return myviewport;
   #
   #
   #########################################
   # --- GraphicsOptions object (17.9) --- #
   #########################################
   #
   mygraphicoptions = session.graphicsOptions;
   #
   if (neuerHintergrund):
      # Gradient: 40% der Hoehe -> 85% des Farbwechsels von der unteren zur oberen Farbe
      mygraphicoptions.setValues(backgroundColor='#FFFFFF');
      mygraphicoptions.setValues(backgroundBottomColor='#AABBDD');
      #
   #
   #
   #
   #####################################################
   # --- ViewportAnnotationsOptions object (17.19) --- #
   #####################################################
   #
   myannotationoptions = myviewport.viewportAnnotationOptions;
   #
   # Alle Hilfselemente im Viewport entfernen
   if (saubererViewport):
      myannotationoptions.setValues(compass=0, triad=0, state=0, title=0);
   #
   # Anzeige der Legende anpassen
   if (saubereLegende):
      myannotationoptions.setValues(legendBox=0);
      myannotationoptions.setValues(legendNumberFormat=FIXED,      legendDecimalPlaces=2);
      myannotationoptions.setValues(legendFont='-*-arial-bold-r-normal-*-*-120-*-*-p-*-*-*');
   #
   #
   #
   ####################################
   # --- OdbDisplay object (35.1) --- #
   ####################################
   #
   myodbdisplay = myviewport.odbDisplay;
   #
   # Bei CEL-Modellen den viewCut an leeren Euler-Elementen aktivieren
   if (evfSchnitt):
      myodbdisplay.setValues(viewCutNames=('EVF_VOID', ), viewCut=TRUE);
   #
   #
   #
   ########################################
   # --- CommonOptions object (35.2)  --- #
   ########################################
   #
   mycommonoptions = myviewport.odbDisplay.commonOptions;
   #
   # Sichtbarkeit der Netzkanten anpassen
   if (minimaleKanten):
      mycommonoptions.setValues(visibleEdges=FEATURE);
   #
   #
   #
   ########################################
   # --- ContourOptions object (35.3) --- #
   ########################################
   #
   mycontouroptions = myviewport.odbDisplay.contourOptions;
   #
   # Manuelle Farbwahl fuer Werte ausserhalb der vorgegebenen Grenzen
   mycontouroptions.setValues(outsideLimitsMode=SPECIFY);
   mycontouroptions.setValues(outsideLimitsAboveColor='#EEEEEE', outsideLimitsBelowColor='#111111');
   #
   # Zulaessige Farbspektren
   if ((farbspektrum == 'CubeHelix') or (farbspektrum == 'CubeHelixINV') or
      (farbspektrum == 'Moreland') or (farbspektrum == 'MorelandINV') or
      (farbspektrum == 'UniformRainbow') or (farbspektrum == 'UniformRainbowINV') or
      (farbspektrum == 'Viridis') or (farbspektrum == 'ViridisINV')):
      #
      mycontouroptions.setValues(spectrum=farbspektrum);
   else:
      Log('# Warnung: farbspektrum unbekannt - wird ignoriert');
   #
   if (not diskreteFarben):
      mycontouroptions.setValues(contourStyle=CONTINUOUS);
   else:
      mycontouroptions.setValues(numIntervals=10);
   #
   #
   #
   ##################################
   # --- Spectrum object (39.8) --- #
   ##################################
   #
   # Spektren aus einer Reihe an Farben definieren (linear interpoliert)
   # CubeHelix (http://www.mrao.cam.ac.uk/~dag/CUBEHELIX/)
   # - Helligkeitswerte: [0.1 0.75]
   # - Anfangswert Rotation: 0.5
   # - Anzahl/Richtung Rotationen: -1.3
   # - Farbwert: 1.3
   # - Gammakorrektur: 0.8
   session.Spectrum('CubeHelix',
      ['#2C2145', '#2B446D', '#226D74', '#2C905F', '#56A244', '#96A242', '#D59B66', '#F99CA4', '#FDADE1']);
   # UniformRainbow (https://peterkovesi.com/projects/colourmaps/index.html rainbow_bgyr_35-85_c72_n256)
   session.Spectrum('UniformRainbow',
      ['#0034F9', '#2A7F82', '#55A915', '#B9C11C', '#FDBC20', '#FE8212', '#FD482B']);
   # Moreland (https://www.kennethmoreland.com/color-maps/)
   session.Spectrum('Moreland',
      ['#3B4CC0', '#6282EA', '#8DB0FE', '#B8D0F9', '#DDDDDD', '#F5C4AD', '#F49A7B', '#DE604D', '#B40426']);
   # Viridis (https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html)
   session.Spectrum('Viridis',
      ['#440154', '#472D7B', '#3B528B', '#2C728E', '#21918C', '#28AE80', '#5EC962', '#ADDC30', '#FDE725']);
   #
   # Die invertierten Spektren
   session.Spectrum('CubeHelixINV',
      ['#FDADE1', '#F99CA4', '#D59B66', '#96A242', '#56A244', '#2C905F', '#226D74', '#2B446D', '#2C2145']);
   #
   session.Spectrum('UniformRainbowINV',
      ['#FD482B', '#FE8212', '#FDBC20', '#B9C11C', '#55A915', '#2A7F82', '#0034F9']);
   #
   session.Spectrum('MorelandINV',
      ['#B4426', '#DE604D', '#F49A7B', '#F5C4AD', '#DDDDDD', '#B8D0F9', '#8DB0FE', '#6282EA', '#3B4CC0']);
   #
   session.Spectrum('ViridisINV',
      ['#FDE725', '#ADDC30', '#5EC962', '#28AE80', '#21918C', '#2C728E', '#3B528B', '#472D7B', '#440154']);
   #
   #
   #
   ######################################
   # --- BasicOptions object (40.1) --- #
   ######################################
   #
   mybasicoptions = myviewport.odbDisplay.basicOptions;
   #
   # Mitteln der Ergebnisse deaktivieren
   if (not ausgabeVerschmieren):
      mybasicoptions.setValues(averageElementOutput=OFF);
   #
   # Winkel der Feature-Kanten anpassen
   mybasicoptions.setValues(featureAngle=60);
   #
   # Sichtbarkeit der Punktelemente
   if (not zeigeMarkierungen):
      mybasicoptions.setValues(pointElements=OFF);
   #
   #
   #
   ######################################
   # --- PrintOptions object (43.1) --- #
   ######################################
   #
   myprintoptions = session.printOptions;
   #
   # Viewportdekoration abschalten
   myprintoptions.setValues(vpDecorations=OFF);
   #
   # Viewporthintergrund aktivieren
   if (exportiereHintergrund):
      myprintoptions.setValues(vpBackground=ON);
   #
   # Farbreduktion fuer png-Bilder deaktivieren
   myprintoptions.setValues(reduceColors=False);
   #
   #
   #
   ##############################
   # --- View object (54.1) --- #
   ##############################
   #
   myviewoptions = myviewport.view;
   #
   # Viewportansicht auf eine Standardsicht anpassen
   if (Standardansicht):
      myviewoptions.setValues(projection=PARALLEL);
      myviewoptions.setValues(session.views['Bottom']);
      #
      myviewoptions.rotate(xAngle=0, yAngle=0, zAngle=90, mode=MODEL);
      myviewoptions.rotate(xAngle=0, yAngle=-30, zAngle=0, mode=MODEL);
      myviewoptions.zoom(zoomFactor=0.95, mode=ABSOLUTE);
      myviewoptions.pan(xFraction=0.12, yFraction=-0.04);
   #
   return myviewport;
#
