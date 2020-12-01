# -*- coding: utf-8 -*-
"""
ausgabe.py   v1.2 (2020-10)
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
def Modellansicht(session, ansicht='', rechts=1, oben=2):
   """Aendere die Ansicht des aktiven Viewports der session entweder durch die interne ansicht
   (d.h. 'Front', 'Back', 'Top', 'Bottom', 'Left' oder 'Right') oder durch Angabe der Achsen rechts
   und oben (x = +/-1, y = +/-2, z = +/-3).

          y                        y                  +-- x                    z          
   Front  |              Back      |            Top   |                Bottom  |         
          +-- x                x --+                  z                        +-- x     
   (rechts=1, oben=2)    (rechts=-1, oben=2)    (rechts=1, oben=-3)    (rechts=1, oben=3) 
   
   
         y                          y                  y
   Left  |               Right      |           Iso    |
         +-- z                  z --+                z   x
   (rechts=3, oben=2)    (rechts=-3, oben=2)    --nicht ohne zusaetzliche Drehung---
   """
   from abaqusConstants import MODEL
   from hilfen import Log
   #
   angabenUngueltig = False;
   viewport = session.viewports[session.currentViewportName];
   #
   if (not ansicht == ''):
      if ((ansicht == 'Front') or (ansicht == 'Back') or (ansicht == 'Top') or (ansicht == 'Bottom')
         or (ansicht == 'Left') or (ansicht == 'Right') or (ansicht == 'Iso')):
         #
         viewport.view.setValues(session.views[ansicht]);
      else:
         angabenUngueltig = True;
   #
   else:
      if (((abs(rechts) == 1) or (abs(rechts) == 2) or (abs(rechts) == 3)) and ((abs(oben) == 1) or
         (abs(oben) == 2) or (abs(oben) == 3)) and (not (abs(rechts) == abs(oben)))):
         #
         basisebene = abs(rechts) + abs(oben);
         aufbauebene = abs(rechts + oben);
         if (basisebene == 3):
            # Blick auf die XY-Ebene
            if (((aufbauebene == 3) and (abs(rechts) == 1)) or ((aufbauebene == 1) and (abs(rechts) == 2))):
               viewport.view.setValues(session.views['Front']);
               viewport.view.rotate(xAngle=0.0, yAngle=0.0, zAngle=-90.0*abs(rechts-1), mode=MODEL);
            else:
               viewport.view.setValues(session.views['Back']);
               viewport.view.rotate(xAngle=0.0, yAngle=0.0, zAngle=-90.0*abs(rechts+1), mode=MODEL);
            #
         elif (basisebene == 4):
            # Blick auf die XZ-Ebene
            if (((aufbauebene == 2) and (abs(rechts) == 1)) or ((aufbauebene == 4) and (abs(rechts) == 3))):
               viewport.view.setValues(session.views['Top']);
               viewport.view.rotate(xAngle=0.0, yAngle=-90.0*(abs(2.0*rechts+oben+1)%5),
                  zAngle=0.0, mode=MODEL);
            else:
               viewport.view.setValues(session.views['Bottom']);
               viewport.view.rotate(xAngle=0.0, yAngle=-90.0*(abs(2.0*rechts-oben+1)%5),
                  zAngle=0.0, mode=MODEL);
            #
         else:
            # Blick auf die YZ-Ebene
            if (((aufbauebene == 5) and (abs(rechts) == 3)) or ((aufbauebene == 1) and (abs(rechts) == 2))):
               viewport.view.setValues(session.views['Left']);
               viewport.view.rotate(xAngle=90.0*(4.0-abs(rechts+1)), yAngle=0.0,
                  zAngle=0.0, mode=MODEL);
            else:
               viewport.view.setValues(session.views['Right']);
               viewport.view.rotate(xAngle=90.0*(4.0-abs(rechts-1)), yAngle=0.0,
                  zAngle=0.0, mode=MODEL);
      #
      else:
         angabenUngueltig = True;
   #
   if (angabenUngueltig):
      Log('# Warnung: Angeforderte Modellansicht ungueltig - nichts getan');
#


# -------------------------------------------------------------------------------------------------
def Ueberlagerung(session, ebenen, versteckteSets=[], versteckteInstances=[], verschiebung=0.0):
   """Erstelle mehrere Darstellungsebenen im aktiven Viewport der session mit den Bezeichnungen
   ebenen. Basierend auf der Anzeige beim Aufruf der Funktion koennen zusaetzliche Sets (mit vollem
   Instance-Pfad) oder/und Instances je Ebene versteckt werden. Optional kann eine globale
   Verschiebung der Ebenen zueinander definiert werden.
   """
   import visualization
   import displayGroupOdbToolset as myodbtoolset
   from abaqusConstants import OVERLAY, CURRENT
   #
   viewport = session.viewports[session.currentViewportName];
   for idxEbene, aktuellerEbenenname in enumerate(ebenen):
      if (viewport.layers.has_key(aktuellerEbenenname)):
         del viewport.layers[aktuellerEbenenname];
      #
   for idxEbene, aktuellerEbenenname in enumerate(ebenen):
      if (idxEbene == 0):
         viewport.Layer(name=aktuellerEbenenname);
      else:
         viewport.Layer(name=aktuellerEbenenname, copyViewName=ebenen[0]);
   #
   # Nachdem alle Ebenen erstellt worden sind, koennen Einzelteile entfernt werden
   viewport.setValues(visibleLayers=tuple(ebenen), currentLayer=ebenen[0], displayMode=OVERLAY);
   viewport.setValues(plotStateLayers=CURRENT, plotOptionsLayers=CURRENT, fieldOutputLayers=CURRENT);
   viewport.setValues(layerOffset=verschiebung);
   for idxEbene, aktuellerEbenenname in enumerate(ebenen):
      viewport.setValues(visibleLayers=tuple(ebenen), currentLayer=ebenen[idxEbene],
         displayMode=OVERLAY);
      if (len(versteckteSets) > 0):
         if (not (versteckteSets[idxEbene] == [])):
            viewport.odbDisplay.displayGroup.remove(leaf=myodbtoolset.LeafFromElementSets(
               elementSets=tuple([einzelSet.upper() for einzelSet in versteckteSets[idxEbene]])));
      if (len(versteckteInstances) > 0):
        if (not (versteckteInstances[idxEbene] == [])):
           viewport.odbDisplay.displayGroup.remove(leaf=myodbtoolset.LeafFromPartInstance(
              partInstanceName=tuple([einzelInst.upper() for einzelInst in versteckteInstances[idxEbene]])));
#


# -------------------------------------------------------------------------------------------------
def BauteileEinfaerben(viewport, zuweisungen, standardfarbe='#000000', odb=True):
   """Faerbt das im uebergebenen viewport dargestellte Modell nach Instanzen ein. Mit zuweisungen
   wird eine Liste erwartet mit [[Instanzname, Farbe], [...]] wobei, die Farbe im Hexadezimal-Format
   zu geben ist (bspw. ist rot '#FF0000'). Alle Instanzen, die nicht in der zuweisung gelistet sind,
   werden mit standardfarbe eingefaerbt. Um die korrekte Zuweisung zu ermoeglichen, muss  mit dem
   Flag odb angegeben werden, ob es sich um eine odb oder mdb (odb=False) handelt.
   """
   if (odb):
      cmap = viewport.colorMappings['Internal set'];
   else:
      cmap = viewport.colorMappings['Set'];
   #
   viewport.setColor(colorMapping=cmap);
   #
   for colorSet in cmap.attributeColors:
      cmap.updateOverrides(overrides={colorSet[0]: (False, ), });
   #
   # U.a. fuer Punktelemente wie Reference points
   viewport.setColor(initialColor='#000000');
   for einzelzuweisung in zuweisungen:
      nameElem, farbeElem = einzelzuweisung;
      if (odb):
         nameElem = nameElem.upper();
      #
      for colorSet in cmap.attributeColors:
         if (nameElem in colorSet[0]):
            cmap.updateOverrides(overrides={colorSet[0]: (True, farbeElem, 'Default', farbeElem), });
   #
   viewport.setColor(colorMapping=cmap);
#


# -------------------------------------------------------------------------------------------------
def PlotFormatieren(xyplot, chart, titel='', xlabel='', ylabel='', xlim=[], ylim=[]):
   """Plot xyplot und Darstellung chart verschoenern und an typisches Format anpassen. Optional
   koennen titel, xlabel und ylabel als Text definiert werden. Ausserdem kann der
   Darstellungsbereich der beiden Achsen durch einen Vektor mit Minimal- und Maximalwert beschraenkt
   werden (ohne Angabe erfolgt Autoskalierung).
   """
   #
   from abaqusConstants import ACROSS, DASHED, DECIMAL
   #
   if (not (titel == '')):
      xyplot.title.setValues(text=titel);
   xyplot.title.style.setValues(font='-*-liberation sans-medium-r-normal-*-*-360-*-*-p-*-*-*');
   #
   # X-Achse
   chart.axes1[0].setValues(tickPlacement=ACROSS, tickLength=4);
   chart.axes1[0].labelStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-180-*-*-p-*-*-*');
   if (not (xlabel == '')):
      chart.axes1[0].axisData.setValues(useSystemTitle=False, title=xlabel);
      chart.axes1[0].titleStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-240-*-*-p-*-*-*');
   if (not (xlim == [])):
      chart.axes1[0].axisData.setValues(minAutoCompute=False, minValue=xlim[0],
         maxAutoCompute=False, maxValue=xlim[1]);
   #
   # Y-Achse
   chart.axes2[0].setValues(tickPlacement=ACROSS, tickLength=4);
   chart.axes2[0].labelStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-180-*-*-p-*-*-*');
   if (not (ylabel == '')):
      chart.axes2[0].axisData.setValues(useSystemTitle=False, title=ylabel);
      chart.axes2[0].titleStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-240-*-*-p-*-*-*');
   if (not (ylim == [])):
      chart.axes2[0].axisData.setValues(minAutoCompute=False, minValue=ylim[0],
         maxAutoCompute=False, maxValue=ylim[1]);
   #
   # Hintergrund
   chart.gridArea.style.setValues(fill=False);
   chart.majorAxis1GridStyle.setValues(show=True, style=DASHED);
   chart.minorAxis1GridStyle.setValues(show=True, color='#CCCCCC');
   chart.majorAxis2GridStyle.setValues(show=True, style=DASHED);
   chart.minorAxis2GridStyle.setValues(show=True, color='#CCCCCC');
   #
   # Legende
   chart.legend.titleStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-180-*-*-p-*-*-*');
   chart.legend.textStyle.setValues(font='-*-liberation sans-medium-r-normal-*-*-180-*-*-p-*-*-*');
   chart.legend.setValues(numberFormat=DECIMAL, numDigits=2);
   chart.legend.area.setValues(inset=True);
   chart.legend.area.style.setValues(fill=True);
#


# -------------------------------------------------------------------------------------------------
def StandardFarben():
   """Gebe den Vektor mit den Standardfarben und deren Reihenfolge in Abaqus aus.
   """
   colors = ('#FF0000', '#003366', '#A020F0', '#008000', '#0000FF', '#C84B00', '#D20096', '#710000',
      '#777700', '#EEC900');
   return colors;
#


# -------------------------------------------------------------------------------------------------
def _StandardLinienstile():
   """Gebe den Vektor mit den Standardlinienstilen und deren Reihenfolge in Abaqus aus.
   """#
   from abaqusConstants import SOLID, DASHED, DOT_DASH, DOTTED
   #
   styles = (SOLID, DASHED, DOT_DASH, DOTTED);
   return styles;
#


# -------------------------------------------------------------------------------------------------
def _LegendenGroesseAendern(chart):
   """Hilfsfunktion, um die Positionierung der Legende aus der gegebenen chart zu ermitteln.
   """
   import visualization
   from abaqusConstants import MANUAL, AUTOMATIC, TOP_RIGHT
   from hilfen import Log
   #
   # Standardmaessig oben rechts anzeigen (Die Legende muss ausserdem erstmal gezeichnet werden,
   # damit die korrekten Geometrien extrahiert werden koennen)
   chart.legend.area.setValues(positionMethod=AUTOMATIC, alignment=TOP_RIGHT, inset=True);
   #
   c_breite = chart.area.width;
   c_hoehe = chart.area.height;
   a_xoff = chart.gridArea.origin[0];
   a_yoff = chart.gridArea.origin[1];
   a_breite = chart.gridArea.width;
   a_hoehe = chart.gridArea.height;
   l_breite = chart.legend.area.width;
   l_hoehe = chart.legend.area.height;
   #
   legxstart = 1.0 - (c_breite - a_xoff - a_breite + l_breite)/c_breite;
   legystart = 1.0 - (c_hoehe - a_yoff - a_hoehe + l_hoehe)/c_hoehe;
   #
   if (l_hoehe > 0.0):
      if (legystart < 0.01):
         Log('# Zu viele Legendeneintraege fuer eine korrekte Darstellung');
         legystart = 0.01;
      #
      chart.legend.area.setValues(positionMethod=MANUAL, originOffset=(legxstart, legystart),
         inset=True);
#


# -------------------------------------------------------------------------------------------------
def PlotLegendeFormatieren(session, chart, curvedata, legendeneintraege, zuerstFarbenwechseln=True,
   kurvenFarben=[], kurvenStile=[]):
   """Die Legende von chart aus session mit den Kurven curvedata wird mit den Werten aus
   legendeneintraege geschrieben. Optional koennen auch kurvenFarben und kurvenStile, sowie deren
   Abfolge mit zuerstFarbenwechseln geaendert werden.
   """
   from hilfen import Log
   #
   if (not len(curvedata) == len(legendeneintraege)):
     Log('# Abbruch: Die Anzahl an Kurven muss mit der Anzahl an Legendeneintraegen uebereinstimmen');
     return;
   #
   if (kurvenFarben == []):
      kurvenFarben = StandardFarben();
   #
   if (kurvenStile == []):
      kurvenStile = _StandardLinienstile();
   #
   if (len(kurvenFarben)*len(kurvenStile) < len(curvedata)):
      Log('# Warnung: Mehr Kurven als eindeutige Darstellungsarten (Farben/Linienstile)');
   #
   vorhandeneKurven = len(chart.curves) - len(curvedata);
   maxzeichen = 0;
   for idx in range(0, len(curvedata)):
      legname = legendeneintraege[idx];
      if (len(legname) > maxzeichen):
         maxzeichen = len(legname);
      #
      firstit = (vorhandeneKurven + idx)%len(kurvenFarben);
      secondit = int((vorhandeneKurven + idx)/len(kurvenFarben));
      if (zuerstFarbenwechseln):
         color = kurvenFarben[firstit];
         style = kurvenStile[secondit];
      else:
         color = kurvenFarben[firstit];
         style = kurvenStile[secondit];
      #
      mycurve = session.curves[curvedata[idx].name];
      mycurve.setValues(useDefault=False, legendLabel=legname);
      mycurve.lineStyle.setValues(thickness=0.8, color=color, style=style);
   #
   _LegendenGroesseAendern(chart=chart);
#


# -------------------------------------------------------------------------------------------------
def _ExistiertFieldOutput(session, odbname, ausgabename, komponente=''):
   """Ueberprueft die odb namens odbname aus session, auf Existenz eines FieldOutputs namens
   ausgabename und deren komponente. (Dazu wird nur der erste Frame aus dem ersten Schritt der odb
   ueberprueft).
   """
   existiert = False;
   odb = session.odbs[odbname];
   Schritte = odb.steps.keys();
   if (odb.steps[Schritte[0]].frames[0].fieldOutputs.has_key(ausgabename)):
      if (komponente == ''):
         existiert = True;
      else:
         for kom_label in odb.steps[Schritte[0]].frames[0].fieldOutputs[ausgabename].componentLabels:
            if (kom_label == komponente):
               existiert = True;
               break;
   #
   return existiert;
#


# -------------------------------------------------------------------------------------------------
def _ExistiertHistoryOutput(session, odbname, ausgabename):
   """Ueberprueft die odb namens odbname aus session auf Existenz eines HistoryOutputs namens
   ausgabename.
   """
   existiert = False;
   odbdata = session.odbData[odbname];
   if (ausgabename in odbdata.historyVariables.keys()):
      existiert = True;
   #
   return existiert;
#


# -------------------------------------------------------------------------------------------------
def _VollstaendigeHistoryOutputBezeichnung(session, odbname, instanzname, bezeichnung):
   """Ueberprueft die odb namens odbname aus session, auf Existenz eines HistoryOutputs der an
   instanzname erzeugt worden ist und die spezifische bezeichnung hat.
   """
   from hilfen import Log
   #
   odbdata = session.odbData[odbname];
   vollstaendige_bezeichnung = '';
   treffer = 0
   for refbezeichnung in odbdata.historyVariables.keys():
      if ((instanzname.upper() in refbezeichnung) and (bezeichnung.upper() in refbezeichnung)):
         vollstaendige_bezeichnung = refbezeichnung;
         treffer += 1;
   #
   if (treffer == 0):
      Log('# Fehler: Kein History-Output zu den uebergebenen Parametern');
      return '--nicht-vorhanden--';
   elif (not (treffer == 1)):
      Log('# Fehler: History-Output nicht eindeutig aus den uebergebenen Parametern');
      return '--nicht-vorhanden--';
   #
   return vollstaendige_bezeichnung;
#


# -------------------------------------------------------------------------------------------------
def HistoryOutputVorbereiten(session, odbname, var, varname):
   """Extrahiere die XY-Daten eines History-Outputs aus einer odb namens odbname aus session mit dem
   exakten Namen var oder var=[Instanzname, Ausgabevariable]. Im letzten Fall wird der Name des
   dazugehoerigen Outputs automatisch bestimmt. Falls Ausgaben fuer das ganze Modell ohne komplette
   Namensnennung erforderlich sind, kann Instanzname auch leer bleiben (bspw. ['', 'ETOTAL']).
   Speichere die Daten intern unter dem Namen varname.
   """
   import visualization
   from hilfen import Log
   #
   ausgabename = var;
   if isinstance(var, (list)):
      ausgabename = _VollstaendigeHistoryOutputBezeichnung(session=session, odbname=odbname,
         instanzname=var[0], bezeichnung=var[1]);
   else:
      ausgabename = var;
   #
   if (not (_ExistiertHistoryOutput(session=session, odbname=odbname, ausgabename=ausgabename))):
      Log('# Fehler: Kein History-Output zu den uebergebenen Parametern');
      return [];
   #
   odb = session.odbs[odbname];
   daten = session.XYDataFromHistory(odb=odb, outputVariableName=ausgabename, 
      steps=tuple(odb.steps.keys()), suppressQuery=False, name=varname);
   return [daten];
#


# -------------------------------------------------------------------------------------------------
def FieldOutputVorbereiten(session, odbname, var, varposition):
   """Extrahiere die XY-Daten eines Field-Outputs aus odb namens odbname aus session mit dem Namen
   var=[Variablenname, Komponente] und varposition=(Instanzname, [Label(s)]).
   
   Wenn mit varposition mehr als ein Label in der Liste uebergeben wird, stimmt die Reihenfolge der
   erzeugten Daten im Allgemeinen nicht mit der Reihenfolge der Labels in der Liste uebereinstimmen.
   """
   import visualization
   from abaqusConstants import NODAL, ELEMENT_CENTROID, INTEGRATION_POINT, COMPONENT
   from hilfen import Log
   #
   if (len(var) == 2):
      variablenname, komponente = var;
   else:
      variablenname = var;
      komponente = '';
   #
   if (not (_ExistiertFieldOutput(session=session, odbname=odbname, ausgabename=variablenname,
         komponente=komponente))):
      #
      return [];
   #
   odb = session.odbs[odbname];
   Schritte = odb.steps.keys();
   startframe = odb.steps[Schritte[0]].frames[0];
   ausgabeposition = startframe.fieldOutputs[variablenname].locations[0].position;
   try:
      if (len(varposition) == 1):
         setauswahl = varposition[0];
         if (ausgabeposition == NODAL):
            if (komponente == ''):
               xyList = session.xyDataListFromField(odb=odb, outputPosition=NODAL,
                  variable=((variablenname, NODAL, ), ),
                  nodeSets=(setauswahl.upper(), ));
            else:
               xyList = session.xyDataListFromField(odb=odb, outputPosition=NODAL,
                  variable=((variablenname, NODAL, ((COMPONENT, komponente), )), ),
                  nodeSets=(setauswahl.upper(), ));
         elif (ausgabeposition == INTEGRATION_POINT):
            if (komponente == ''):
               xyList = session.xyDataListFromField(odb=odb, outputPosition=ELEMENT_CENTROID,
                  variable=((variablenname, INTEGRATION_POINT, ), ),
                  elementSets=(setauswahl.upper(), ));
            else:
               xyList = session.xyDataListFromField(odb=odb, outputPosition=ELEMENT_CENTROID,
                  variable=((variablenname, INTEGRATION_POINT, ((COMPONENT, komponente), )), ),
                  elementSets=(setauswahl.upper(), ));
         else:
            Log('# Fehler: Ausgabepunkt nicht bekannt - aktuell nur NODAL und INTEGRATION_POINT implementiert');
            return [];
      #
      elif (len(varposition) == 2):
         refinstance, selectedElements = varposition;
         if (ausgabeposition == NODAL):
            if (komponente == ''):
               xyList = session.xyDataListFromField(odb=odb, outputPosition=NODAL, 
                  variable=((variablenname, NODAL, ), ),
                  nodeLabels=((refinstance.upper(), tuple(selectedElements), ), ));
            else:
               xyList = session.xyDataListFromField(odb=odb, outputPosition=NODAL, 
                  variable=((variablenname, NODAL, ((COMPONENT, komponente), )), ),
                  nodeLabels=((refinstance.upper(), tuple(selectedElements), ), ));
         elif (ausgabeposition == INTEGRATION_POINT):
            if (komponente == ''):
               xyList = session.xyDataListFromField(odb=odb, outputPosition=ELEMENT_CENTROID, 
                  variable=((variablenname, INTEGRATION_POINT, ), ),
                  elementLabels=((refinstance.upper(), tuple(selectedElements), ), ));
            else:
               xyList = session.xyDataListFromField(odb=odb, outputPosition=ELEMENT_CENTROID, 
                  variable=((variablenname, INTEGRATION_POINT, ((COMPONENT, komponente), )), ),
                  elementLabels=((refinstance.upper(), tuple(selectedElements), ), ));
         else:
            Log('# Fehler: Ausgabepunkt nicht bekannt - aktuell nur NODAL und INTEGRATION_POINT implementiert');
            return [];
      else:
         print(str(len(varposition)) + ' und ' + str(varposition))
         Log('# Fehler: Ungueltige Bezeichnung in varposition');
         return [];
   except:
      #FIXME: VisError unbekannt, wenn nicht from visualization import *
      #       sonst besser: except VisError:
      #Log('VisError: No xy data was extracted using the provided options.');
      Log('# Fehler: Abaqus konnte mit den uebergebenen Angaben keine XYDaten extrahieren - sind Label/Setnamen richtig?');
      return [];
   #
   curvedata = session.curveSet(xyData=xyList);
   daten = [session.xyDataObjects[curve.name] for curve in curvedata];
   return daten;
#


# -------------------------------------------------------------------------------------------------
def PlotOutput(session, odbname, yvar, yvarposition=[], ylabel='', ylimit=[], posydir=True, xvar=[],
   xvarposition=[], xlabel='', xlimit=[], posxdir=True, titel='', legendeneintraege=[],
   plothinzufuegen=False):
   """Plotte die angegebenen yvar der Auswahl yvarposition ueber xvar an xvarposition der odb namens
   odbname aus session. Falls xvar nicht definiert ist, wird diese Achse zur Zeitachse. Es koennen
   mehrere Daten (bspw. mehrere Elemente) fuer die y-Richtung uebergeben werden, aber fuer die
   x-Richtung darf es nur ein einziger Datensatz sein.
   
   Optional koennen auch xlabel und ylabel zur Achsenbeschriftung sowie xlimit und ylimit zur
   Beschraenkung der Zeichenebene uebergeben werden. Die Richtung der Werte kann optional ueber
   posxdir oder posydir invertiert werden. Optional kann ausserdem ein titel fuer den Plot und die
   Bezeichnung der legendeneintraege uebergeben werden. Falls bereits ein Plot existiert, steuert
   plothinzufuegen, ob er ueberschrieben oder ergaenzt wird.
    
   Erwartet wird bei FieldOuptut-Variablen ein Vektor var=(Variablenname, Komponente) und entweder
   die Variablenposition mit yvarposition=(odb-Setname) oder (Instanzname, [Label(s)]).
    
   Bei HistoryOutput-Variablen wird nur ein Vektor var=([Instanzname, Ausgabevariable]) oder
   var=(Ausgabenname) erwartet (varposition entfaellt). Im Fall var=([Instanzname, Ausgabevariable])
   wird der Name des dazugehoerigen Outputs automatisch bestimmt. Falls Ausgaben fuer das ganze
   Modell ohne komplette Namensnennung erforderlich sind, kann Instanzname auch leer bleiben
   (bspw. ['', 'ETOTAL']).
   """
   from hilfen import Log, GueltigenNamenFinden
   #
   # Die aktuelle odb muss sichtbar sein, damit xyDaten extrahiert werden koennen (sonst viserror)
   viewport = session.viewports[session.currentViewportName];
   odb = session.odbs[odbname];
   viewport.setValues(displayedObject=odb);
   #
   xfac = 1;
   yfac = 1;
   if (not posxdir):
      xfac = -1;
   #
   if (not posydir):
      yfac = -1;
   #
   xdaten = [];
   ydaten = [];
   #
   # Sicherstellen, dass die Variablen als tuple gespeichert werden,
   # da argument=('string') als argument='string' gespeichert wird
   if (not isinstance(xvarposition, (list, tuple))):
      xvarposition = tuple([xvarposition]);
   #
   if (not isinstance(yvarposition, (list, tuple))):
      yvarposition = tuple([yvarposition]);
   #
   # y-Variablen muss vorhanden sein
   if (yvarposition == []):
      # HistoryOutput
      ydaten = HistoryOutputVorbereiten(session=session, odbname=odbname,
         var=yvar, varname='y_xyData');
   else:
      # FieldOutput
      ydaten = FieldOutputVorbereiten(session=session, odbname=odbname,
         var=yvar, varposition=yvarposition);
   #
   if (ydaten == []):
      Log('# Fehler: Konnte keine y-Daten aus uebergebenen Werten extrahieren');
      return None;
   # x-Variablen sind optional
   if (not (xvar == [])):
      if (xvarposition == []):
         # HistoryOutput
         xdaten = HistoryOutputVorbereiten(session=session, odbname=odbname,
            var=xvar, varname='x_xyData');
      else:
         # FieldOutput
         xdaten = FieldOutputVorbereiten(session=session, odbname=odbname,
            var=xvar, varposition=xvarposition);
   #
   if (xdaten == []):
      xykombiniert = yfac*ydaten;
      xydatenname = 'xyData_time-' + yvar[1];
   else:
      try:
         if ((len(xdaten) > 1) and (len(ydaten) > 1)):
            Log('# Fehler: Entweder X- oder Y-Daten koennen mehrere Dimensionen haben, aber nicht beide');
            return None;
         elif (len(xdaten) > 1):
            xykombiniert = [combine(xfac*temp_xdaten, yfac*ydaten[0]) for temp_xdaten in xdaten];
         elif (len(ydaten) > 1):
            xykombiniert = [combine(xfac*xdaten[0], yfac*temp_ydaten) for temp_ydaten in ydaten];
         else:
            xykombiniert = [combine(xfac*xdaten[0], yfac*ydaten[0])];
      except:
         #FIXME: XypError unbekannt, wenn nicht from visualization import *
         #       sonst besser: except XypError:
         #Log('XypError: X value is not monotonic and interpolation is undefined.');
         Log('# Fehler: Darstellung nicht moeglich: Daten koennen so nicht grafisch in Abaqus ausgegeben werden - einzeln plotten?');
         return None;
      #
      xydatenname = 'xyData_' + xvar[1] + '-' + yvar[1];
   #
   xyList = []
   for datensatz in xykombiniert:
      neuername = GueltigenNamenFinden(umgebung=session.xyDataObjects, namensvorschlag=xydatenname);
      session.xyDataObjects.changeKey(fromName=datensatz.name, toName=neuername);
      xyList += [session.xyDataObjects[neuername]];
   #
   PlotXYDaten(session=session, xyListe=xyList, ylimit=ylimit, ylabel=ylabel, xlimit=xlimit,
      xlabel=xlabel, titel=titel, legendeneintraege=legendeneintraege, plothinzufuegen=plothinzufuegen);
   return xyList;
#


# -------------------------------------------------------------------------------------------------
def PlotXYDaten(session, xyListe, ylimit=[], ylabel='', xlimit=[], xlabel='', titel='',
   legendeneintraege=[], plothinzufuegen=False):
   """Plotte die in der xyListe angegebenen XYDaten. Optional koennen xlabel und ylabel zur
   Achsenbeschriftung sowie xlimit und ylimit zur Beschraenkung der Zeichenebene uebergeben werden.
   Optional kann ausserdem ein titel fuer den Plot und die Bezeichnung der legendeneintraege
   uebergeben werden. Falls bereits ein Plot existiert, steuert plothinzufuegen, ob er
   ueberschrieben oder ergaenzt wird.
   """
   import visualization
   #
   if (not session.xyPlots.has_key('XYplot')):
      xyplot = session.XYPlot('XYplot');
   else:
      xyplot = session.xyPlots['XYplot'];
   #
   # Die Kurven der xyListe ausgeben
   curvedata = session.curveSet(xyData=xyListe);
   #
   viewport = session.viewports[session.currentViewportName];
   viewport.setValues(displayedObject=xyplot);
   chart = session.charts[session.charts.keys()[0]];
   if (plothinzufuegen):
      chart.setValues(curvesToPlot=curvedata, appendMode=True);
   else:
      chart.setValues(curvesToPlot=curvedata, appendMode=False);
   #
   # Darstellung anpassen
   PlotFormatieren(xyplot=xyplot, chart=chart, titel=titel, xlabel=xlabel, ylabel=ylabel);
   if (not(legendeneintraege == [])):
      PlotLegendeFormatieren(session=session, chart=chart, curvedata=curvedata,
         legendeneintraege=legendeneintraege);
   #
   if (not (xlimit == [])):
      chart.axes1[0].axisData.setValues(minAutoCompute=False, maxAutoCompute=False,
         minValue=xlimit[0], maxValue=xlimit[1]);
   #
   if (not (ylimit == [])):
      chart.axes2[0].axisData.setValues(minAutoCompute=False, maxAutoCompute=False,
         minValue=ylimit[0], maxValue=ylimit[1]);
   #
   return curvedata;
#


# -------------------------------------------------------------------------------------------------
def ViewportBemassung(db, viewport, bezeichnung, punkt1, punkt2, offset, groesse=180):
   """Bemasse eine Laenge eines Bauteils einer odb (db=odb.userData) oder mdb (db=mdb) im viewport
   zwischen punkt1 und punkt2. Die Bemassung benoetigt ein offset zur Bemassungslinie und bekommt
   intern die angegebene bezeichnung zugewiesen. Optional kann die groesse der Schrift der Bemassung
   angepasst werden. Gibt die Namen der vier erzeugten Annotationen zurueck.
   """
   from math import sqrt
   import annotationToolset
   from abaqusConstants import FILLED_ARROW, DOTTED, NONE, CENTER
   from hilfen import abapys_tol
   #
   pfeil = db.Arrow(name='Pfeil_' + bezeichnung, startHeadStyle=FILLED_ARROW, color='#29359A',
      startAnchor=(punkt1[0]+offset[0], punkt1[1]+offset[1], punkt1[2]+offset[2]),
      endAnchor=(punkt2[0]+offset[0], punkt2[1]+offset[1], punkt2[2]+offset[2]));
   viewport.plotAnnotation(annotation=pfeil);
   if ((abs(offset[0]) > abapys_tol) or (abs(offset[1]) > abapys_tol) or (abs(offset[2]) > abapys_tol)):
      offsetfaktor = 1.3;
      hl1 = db.Arrow(name='HL1_' + bezeichnung,
         endHeadStyle=NONE, color='#A0A0A0', lineStyle=DOTTED,
         startAnchor=(punkt1[0], punkt1[1], punkt1[2]),
         endAnchor=(punkt1[0]+offsetfaktor*offset[0],
                    punkt1[1]+offsetfaktor*offset[1],
                    punkt1[2]+offsetfaktor*offset[2]));
      viewport.plotAnnotation(annotation=hl1);
      hl2 = db.Arrow(name='HL2_' + bezeichnung,
         endHeadStyle=NONE, color='#A0A0A0', lineStyle=DOTTED,
         startAnchor=(punkt2[0], punkt2[1], punkt2[2]),
         endAnchor=(punkt2[0]+offsetfaktor*offset[0],
                    punkt2[1]+offsetfaktor*offset[1],
                    punkt2[2]+offsetfaktor*offset[2]));
      viewport.plotAnnotation(annotation=hl2);
   #
   textoffsetfaktor = 1.8;
   laenge = sqrt((punkt2[0]-punkt1[0])**2 + (punkt2[1]-punkt1[1])**2 + (punkt2[2]-punkt1[2])**2);
   text = db.Text(name='Text_' + bezeichnung, text=str(laenge).format(6) + 'm',
      anchor=((punkt2[0]+punkt1[0])/2.0+textoffsetfaktor*offset[0],
              (punkt2[1]+punkt1[1])/2.0+textoffsetfaktor*offset[1],
              (punkt2[2]+punkt1[2])/2.0+textoffsetfaktor*offset[2]),
      referencePoint=CENTER, font='-*-liberation sans-medium-r-normal-*-*-' + str(groesse) + '-*-*-p-*-*-*');
   viewport.plotAnnotation(annotation=text);
   #return [pfeil, text, hl1, hl2];
   return ['Pfeil_' + bezeichnung, 'Text_' + bezeichnung, 'HL1_' + bezeichnung, 'HL2_' + bezeichnung];
#


# -------------------------------------------------------------------------------------------------
def LetzterOutputStepUndFrame(session, odbname):
   """Ermittle aus der Ausgabedatei odbname in der aktuellen session den letzten Step und
   darin den letzten Frame, in dem Outputs geschrieben worden sind.
   """
   letzterStep = 0;
   letzterFrame = 0;
   mySteps = session.odbData[odbname].steps.keys();
   for steps, stepname in enumerate(mySteps):
      letzterStep = len(mySteps) - (steps + 1);
      if (len(session.odbs[odbname].steps[mySteps[letzterStep]].frames) > 0):
         letzterFrame = len(session.odbs[odbname].steps[mySteps[letzterStep]].frames) - 1;
         break;
   #
   return [letzterStep, letzterFrame];
#


# -------------------------------------------------------------------------------------------------
def _SichtfeldGitterVerschieben(viewport, anordnung=[1, 1], position=0, zurueck=False):
   """Verschiebe den aktuellen Bildausschnitt aus dem viewport auf die gewuenschte position der
   anordnung der Bilder oder optional von dort auf die Ursprungsposition zurueck.
   """
   kanaele = anordnung[0]*anordnung[1];
   xpos = position % anordnung[0];
   ypos = int(position*anordnung[1]/kanaele);
   if (zurueck):
      viewport.view.pan(xFraction=xpos, yFraction=-ypos);
   else:
      viewport.view.pan(xFraction=-xpos, yFraction=ypos);
#


# -------------------------------------------------------------------------------------------------
def BildSpeichern(dateiname, session, dateityp='png', bildgroesse=[], hintergrund=False):
   """Speichern die Darstellung des aktiven Viewports aus session als Bilddatei mit dem Namen
   dateiname. Optional kann der dateityp ('png' oder 'eps') und die bildgroesse (als Vektor mit
   Bildbreite und Bildhoehe in Pixeln) angepasst werden.
   """
   from abaqusConstants import ON, OFF, AS_DISPLAYED, DPI_300, EPS, PNG
   from hilfen import Log, ViewportPixelGroesseExtrahieren, ViewportGroesseAendern
   #
   # Allgemeine Ausgabeeinstellungen
   session.printOptions.setValues(vpDecorations=OFF);
   #
   viewport = session.viewports[session.currentViewportName];
   # Bildgroesse sollte am besten schon vor Aufruf dieser Funktion angepasst werden, damit das Bild
   # gespeichert wird, das am Bildschirm zu sehen war. Ansonsten wird die Anpassung hier vorgenommen
   # und nach der Bearbeitung wieder zurueckgesetzt
   if (len(bildgroesse) == 2):
      originalgroesse = ViewportPixelGroesseExtrahieren(viewport=viewport);
      ViewportGroesseAendern(viewport=viewport, bildgroesse=bildgroesse);
   #
   alterHintergrund = session.printOptions.vpBackground;
   if (hintergrund):
      session.printOptions.setValues(vpBackground=ON);
   else:
      session.printOptions.setValues(vpBackground=OFF);
   #
   if   ((dateityp.lower() == 'png') or (dateityp.lower() == '.png')):
      session.printOptions.setValues(reduceColors=False);
      dateiname = dateiname + '.png';
      session.printToFile(fileName=dateiname, format=PNG, canvasObjects=(viewport, ));
      Log('# Gespeichert als ' + dateiname);
   elif ((dateityp.lower() == 'eps') or (dateityp.lower() == '.eps')):
      # Bei eps-Bildern muss die Bildgroesse nochmal explizit gegeben werden,
      # damit auch tatsaechlich die richtige Groesse ausgegeben wird.
      [viewportpixelbreite, viewportpixelhoehe] = ViewportPixelGroesseExtrahieren(viewport=viewport);
      session.epsOptions.setValues(resolution=DPI_300, fontType=AS_DISPLAYED,
         imageSize=(round(viewportpixelbreite)/72.0, round(viewportpixelhoehe)/72.0));
      dateiname = dateiname + '.eps';
      session.printToFile(fileName=dateiname, format=EPS, canvasObjects=(viewport, ));
      Log('# Gespeichert als ' + dateiname);
   else:
      Log('# WARNUNG: Bild ' + dateiname + ' NICHT gespeichert');
   #
   if (len(bildgroesse) == 2):
      # Bildgroesse vor Aufruf der Funktion wiederherstellen
      ViewportGroesseAendern(viewport=viewport, bildgroesse=originalgroesse);
   #
   session.printOptions.setValues(vpBackground=alterHintergrund);
#


# -------------------------------------------------------------------------------------------------
def MultiBildSpeichern(dateiname, session, anordnung=[1, 1], zeitstempel=[], zeitstempelkanal=0,
   legendenkanal=0, mehrfachmodus=False, autozoom=False):
   """Speichere Dateien mit dem Titel dateiname aus dem aktiven Viewport der Session session und odb
   namens odbname. Optional kann statt einem Bild mehrere Teilbilder nach der Anordnung anordnung
   ausgegeben werden. Falls SINGLE und OVERLAY-Modus gespeichert werden sollen, kann mehrfachmodus
   aktiviert werden.
   Optional kann mit autozoom der Zoom innerhalb der Funktion abhaengig vom uebergebenen sichtbaren
   Bereich und der Aufteilung in anordnung durchgefuehrt werden.
   """
   from abaqusConstants import ABSOLUTE, ON, OFF, SINGLE, OVERLAY
   from hilfen import Log
   #
   auswahlbuchstaben = 'abcdefghijklmnopqrstuvwx';
   viewport = session.viewports[session.currentViewportName];
   #
   kanaele = anordnung[0]*anordnung[1];
   if (kanaele >= len(auswahlbuchstaben)):
      Log('Abbruch: MultiBildAusgabe unterstuetzt nur maximal ' + str(len(auswahlbuchstaben)) + ' Teilbilder');
      return;
   #
   if (not (zeitstempel == [])):
      viewport.hideAnnotation(annotation=zeitstempel);
   #
   if (not mehrfachmodus):
      kanaloffset = 0;
   else:
      kanaloffset = kanaele;
   #
   zoom = 1.0;
   pan = [0.0, 0.0];
   if (autozoom):
      camTar = viewport.view.cameraTarget;
      camPos = viewport.view.cameraPosition;
      camUp = viewport.view.cameraUpVector;
      camFov = viewport.view.fieldOfViewAngle;
      camNear = viewport.view.nearPlane;
      #
      zoom = min(anordnung[0], anordnung[1]);
      pan = [(anordnung[0]-1.0)/2.0, -(anordnung[1]-1.0)/2.0];
      viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
      viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
   #
   restoreMode = viewport.displayMode;
   aktiveLegende = viewport.viewportAnnotationOptions.legend;
   for idxKanal in range(kanaele):
      viewport.viewportAnnotationOptions.setValues(legend=OFF);
      if ((idxKanal == legendenkanal) and (aktiveLegende == ON)):
         viewport.viewportAnnotationOptions.setValues(legend=ON);
      #
      if (mehrfachmodus or (restoreMode == SINGLE)):
         viewport.setValues(displayMode=SINGLE);
         if (idxKanal == 0):
            viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung, position=idxKanal);
         if ((not (zeitstempel == [])) and (idxKanal == zeitstempelkanal)):
            viewport.plotAnnotation(annotation=zeitstempel);
            BildSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal+kanaloffset],
               session=session);
            viewport.hideAnnotation(annotation=zeitstempel);
         else:
            BildSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal+kanaloffset],
               session=session);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung,
            position=idxKanal, zurueck=True);
         if (idxKanal == kanaele-1):
            viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
         #
      if (mehrfachmodus or (restoreMode == OVERLAY)):
         viewport.setValues(displayMode=OVERLAY);
         if (idxKanal == 0):
            viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung, position=idxKanal);
         if ((not (zeitstempel == [])) and (idxKanal == zeitstempelkanal)):
            viewport.plotAnnotation(annotation=zeitstempel);
            BildSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal], session=session);
            viewport.hideAnnotation(annotation=zeitstempel);
         else:
            BildSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal], session=session);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung,
            position=idxKanal, zurueck=True);
         if (idxKanal == kanaele-1):
            viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
   #
   viewport.setValues(displayMode=restoreMode);
   if (autozoom):
      viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
      viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
      #
      viewport.view.setValues(cameraTarget=camTar);
      viewport.view.setValues(cameraPosition=camPos);
      viewport.view.setValues(cameraUpVector=camUp);
      viewport.view.setValues(fieldOfViewAngle=camFov);
      viewport.view.setValues(nearPlane=camNear);
   #
   viewport.viewportAnnotationOptions.setValues(legend=aktiveLegende);
#


# -------------------------------------------------------------------------------------------------
def VideobilderSpeichern(dateiname, session, odbname, dateityp='png', numzahlen=3, zeitstempel=None,
   startstep=0, startframe=0, stopstep=-1, stopframe=-1, erstedateinummer=None):
   """Gebe im aktiven viewport von session alle frames aus allen steps als Bilddaten mit dem
   Basisnamen name im Format dateityp aus. Bildbreite und Bildhoehe wird von der aktuellen
   Einstellung uebernommen.
   
   Um nur eine Unterauswahl an Bildern zu speichern kann ein Intervall mit startstep/startframe
   sowie stopstep/stopframe definiert werden. Vorallem dann kann es sich auch anbieten, die
   Dateiausgabe nicht bei ihrem natuerlichen Start, sondern bei 0 starten zu lassen, indem
   erstedateinummer=0 gesetzt wird.
   """
   import animation
   from abaqusConstants import TIME_HISTORY
   from hilfen import _VersionAbaqus, Log
   #
   # Bis Abaqus 2018 wird animationController mit allen Einstellungen aus session genutzt
   # Ab Abaqus 2020 wird der animationController aus viewport verwendet und die Einstellungen aus
   # einem animationPlayer-Objekt
   abaqusVersion = _VersionAbaqus();
   if (abaqusVersion is None):
      Log('# Warnung: Keine gueltige Abaqus-Version hinterlegt - InitialisiereAbapys() vergessen?');
      return;
   elif (abaqusVersion == '2020'):
      viewport = session.viewports[session.currentViewportName];
      animationssteuerung = viewport.animationController;
      animationssteuerung.setValues(animationType=TIME_HISTORY);
      viewport.animationPlayer.playerOptions.setValues(frameCounter=False);
   else:
      animationssteuerung = session.animationController
      animationssteuerung.setValues(animationType=TIME_HISTORY, viewports=(session.currentViewportName, ));
      animationssteuerung.animationOptions.setValues(frameCounter=False);
   #
   animationssteuerung.showFirstFrame();
   idx = -1;
   nummeroffset = 0;
   #
   vorzeitigBeenden = False;
   gestartet = False;
   mySteps = session.odbData[odbname].steps.keys();
   letzterStep, letzterFrame = LetzterOutputStepUndFrame(session=session, odbname=odbname);
   if (startstep == -1):
      startstep = letzterStep;
   #
   if (stopstep == -1):
      stopstep = letzterStep;
   #
   for istep in range(len(mySteps)):
      myFrames = session.odbData[odbname].steps[mySteps[istep]].frames.keys();
      temp_startframe = startframe;
      if (startframe == -1):
         temp_startframe = letzterFrame;
      #
      temp_stopframe = stopframe;
      if (stopframe == -1):
         temp_stopframe = letzterFrame;
      #
      totalsteptime = session.odbs[odbname].steps[mySteps[istep]].totalTime;
      for iframe in range(len(myFrames)):
         idx = idx+1;
         if (istep < startstep):
            continue;
         #
         if (istep == startstep):
            if (iframe < temp_startframe):
               continue;
         #
         if (not gestartet):
            gestartet = True;
            animationssteuerung.showFrame(frame=idx);
            if (not (erstedateinummer is None)):
               nummeroffset = idx - erstedateinummer;
         #
         bildname = dateiname + str(idx-nummeroffset).zfill(numzahlen);
         if (zeitstempel is not None):
            frameinfo = session.odbs[odbname].steps[mySteps[istep]].frames[iframe].description;
            aktuellezeit = filter(None, frameinfo.split(" "))[-1];
            aktuelleinfo = "{:8.3f}".format(float(aktuellezeit) + totalsteptime);
            zeitstempel.setValues(text=aktuelleinfo);
         #
         BildSpeichern(dateiname=bildname, session=session, dateityp=dateityp);
         animationssteuerung.incrementFrame();
         #
         if (((istep == stopstep) and (iframe == temp_stopframe)) or (istep > stopstep)):
            vorzeitigBeenden = True;
            break;
         #
      #
      if (vorzeitigBeenden):
         break;
   #
   animationssteuerung.stop();
#


# -------------------------------------------------------------------------------------------------
def MultiVideobilderSpeichern(dateiname, session, odbname, anordnung=[1, 1], zeitstempel=[],
   zeitstempelkanal=0, legendenkanal=0, mehrfachmodus=False, autozoom=False):
   """Speichere Dateien mit dem Basisnamen dateiname aus der Ausgabedatei odbname, die im aktiven
   Viewport der session dargestellt ist. Optional koennen statt einem Bild mehrere Teilbilder in der
   gegebenen anordnung (Teilbilder horizontal und vertikal) ausgegeben werden. Optional kann
   ausserdem ein zeitstempel uebergeben werden, der nur im Teilbild zeitstempelkanal angezeigt wird.
   Auch eine moeglicherweise sichtbare Legende wird nur im legendenkanal dargestellt. Dabei hat das
   linke obere Teilbild den Wert 0 und nimmt zeilenweise von links nach rechts zu. Falls
   mehrfachmodus aktiviert ist, werden Bilder im SINGLE- und OVERLAY-Modus gespeichert.
   Optional kann mit autozoom der Zoom innerhalb der Funktion abhaengig vom uebergebenen sichtbaren
   Bereich und der Aufteilung in anordnung durchgefuert werden.
   """
   from abaqusConstants import ABSOLUTE, ON, OFF, SINGLE, OVERLAY
   from hilfen import Log
   #
   auswahlbuchstaben = 'abcdefghijklmnopqrstuvwx';
   viewport = session.viewports[session.currentViewportName];
   #
   voffset = 0;
   kanaele = anordnung[0]*anordnung[1];
   if (kanaele >= len(auswahlbuchstaben)):
      Log('Abbruch: MultiVideoAusgabe unterstuetzt nur maximal ' + str(len(auswahlbuchstaben)) + ' Teilbilder');
      return;
   #
   if (not (zeitstempel == [])):
      viewport.hideAnnotation(annotation=zeitstempel);
   #
   if (not mehrfachmodus):
      kanaloffset = 0;
   else:
      kanaloffset = kanaele;
   #
   zoom = 1.0;
   pan = [0.0, 0.0];
   if (autozoom):
      camTar = viewport.view.cameraTarget;
      camPos = viewport.view.cameraPosition;
      camUp = viewport.view.cameraUpVector;
      camFov = viewport.view.fieldOfViewAngle;
      camNear = viewport.view.nearPlane;
      #
      zoom = min(anordnung[0], anordnung[1]);
      pan = [(anordnung[0]-1.0)/2.0, -(anordnung[1]-1.0)/2.0];
      viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
      viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
   #
   restoreMode = viewport.displayMode;
   aktiveLegende = viewport.viewportAnnotationOptions.legend;
   for idxKanal in range(kanaele):
      viewport.viewportAnnotationOptions.setValues(legend=OFF);
      if ((idxKanal == legendenkanal) and (aktiveLegende == ON)):
         viewport.viewportAnnotationOptions.setValues(legend=ON);
      #
      if (mehrfachmodus or (restoreMode == SINGLE)):
         viewport.setValues(displayMode=SINGLE);
         if (idxKanal == 0):
            viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung, position=idxKanal);
         if ((not (zeitstempel == [])) and (idxKanal == zeitstempelkanal)):
            viewport.plotAnnotation(annotation=zeitstempel);
            VideobilderSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal+kanaloffset],
               session=session, odbname=odbname, zeitstempel=zeitstempel);
            viewport.hideAnnotation(annotation=zeitstempel);
         else:
            VideobilderSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal+kanaloffset],
               session=session, odbname=odbname);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung,
            position=idxKanal, zurueck=True);
         if (idxKanal == kanaele-1):
            viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
         #
      if (mehrfachmodus or (restoreMode == OVERLAY)):
         viewport.setValues(displayMode=OVERLAY);
         if (idxKanal == 0):
            viewport.view.zoom(zoomFactor=zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=pan[0], yFraction=pan[1]);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung, position=idxKanal);
         if ((not (zeitstempel == [])) and (idxKanal == zeitstempelkanal)):
            viewport.plotAnnotation(annotation=zeitstempel);
            VideobilderSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal], session=session,
               odbname=odbname, zeitstempel=zeitstempel);
            viewport.hideAnnotation(annotation=zeitstempel);
         else:
            VideobilderSpeichern(dateiname=dateiname + auswahlbuchstaben[idxKanal],
               session=session, odbname=odbname);
         #
         _SichtfeldGitterVerschieben(viewport=viewport, anordnung=anordnung,
            position=idxKanal, zurueck=True);
         if (idxKanal == kanaele-1):
            viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
            viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
   #
   viewport.setValues(displayMode=restoreMode);
   if (autozoom):
      viewport.view.pan(xFraction=-pan[0], yFraction=-pan[1]);
      viewport.view.zoom(zoomFactor=1.0/zoom, mode=ABSOLUTE);
      #
      viewport.view.setValues(cameraTarget=camTar);
      viewport.view.setValues(cameraPosition=camPos);
      viewport.view.setValues(cameraUpVector=camUp);
      viewport.view.setValues(fieldOfViewAngle=camFov);
      viewport.view.setValues(nearPlane=camNear);
   #
   viewport.viewportAnnotationOptions.setValues(legend=aktiveLegende);
#


# -------------------------------------------------------------------------------------------------
def XYDatenAnElementen(session, odbname, odbinstname, labelliste, zeitpunkt, var,
   name, beschreibung=''):
   """Erstelle xyDaten namens name (mit beschreibung) aus Daten der in der aktuellen session
   geoeffneten odb namens odbname. Die xyDaten werden aus dem FieldOutput der Variable
   var=[Variablenname, Komponente] fuer den uebergebenen zeitpunkt aus odbinstname erstellt.
   Abhaengig davon, ob var an Elementen oder Knoten definiert ist, wird in labelliste auch eine
   Auflistung von Knotenlabels oder Elementlabels erwartet, fuer die die xyDaten erstellt werden
   sollen.
   """
   import visualization
   from abaqusConstants import NUMBER
   #
   xydaten = None;
   alleDaten = [];
   pos_data = 0;
   datentyp = None;
   yvallabel = '';
   for idxLabel, elemLabel in enumerate(labelliste):
      daten = FieldOutputVorbereiten(session=session, odbname=odbname, var=var,
         varposition=(odbinstname.upper(), [elemLabel]));
      if (idxLabel == 0):
         datentyp = daten[0].axis2QuantityType;
         yvallabel = daten[0].yValuesLabel;
         idx_ref = yvallabel.find(odbinstname.upper());
         if (not (idx_ref == -1)):
            yvallabel = yvallabel[:(idx_ref + len(odbinstname))];
         #
         odbzeiten = [x[0] for x in daten[0]];
         min_zeitdiff = abs(odbzeiten[0] - zeitpunkt);
         for idxZeit, odbzeitpunkt in enumerate(odbzeiten):
            if (abs(odbzeitpunkt - zeitpunkt) < min_zeitdiff):
               pos_data = idxZeit;
      #
      alleDaten += [(idxLabel, daten[0][pos_data][1]), ];
   #
   if (not (alleDaten == [])):
      xydaten = session.XYData(name=name, data=tuple(alleDaten), contentDescription=beschreibung,
         legendLabel=name, xValuesLabel='Number of Element in List', yValuesLabel=yvallabel,
         axis1QuantityType=visualization.QuantityType(type=NUMBER), axis2QuantityType=datentyp);
   #
   return xydaten;
#


# -------------------------------------------------------------------------------------------------
def XYDatenSpeichern(dateiname, session, xydatenname, nachkommastellen=4):
   """Speichert den Datensatz xydatenname des aktiven Viewports von session als csv-Datei dateiname.
   Optional kann die Anzahl an nachkommastellen angepasst werden.
   """
   from abaqusConstants import OFF
   from hilfen import Log
   #
   reportname = dateiname + '.csv';
   if isinstance(xydatenname, list):
      xyObject = [];
      for xydatensatz in xydatenname:
         xyObject += [session.xyDataObjects[xydatensatz]];
   else:
      xyObject = [session.xyDataObjects[xydatenname]];
   #
   session.xyReportOptions.setValues(numDigits=nachkommastellen);
   session.writeXYReport(fileName=reportname, appendMode=OFF, xyData=tuple(xyObject));
   Log('# Gespeichert als ' + reportname);
#


# -------------------------------------------------------------------------------------------------
def FieldOutputSpeichern(dateiname, session, odbname, fieldOutput, step, frame):
   """Ermittle die Ausgabevariable fieldOutput im angeforderten step und frame
   (beides Zahlenwerte) der Datei odbname aus der aktuellen session. Speichere
   das Ergebnis unter dateiname.erg.
   """
   import material
   from abaqusConstants import NODAL, INTEGRATION_POINT, COMPONENT, ENGINEERING, OFF
   from hilfen import Log
   #
   odb = session.odbs[odbname];
   Schritte = odb.steps.keys();
   letzterStep, letzterFrame = LetzterOutputStepUndFrame(session=session, odbname=odbname);
   tempstep = step;
   tempframe = frame;
   if (step == -1):
      tempstep = letzterStep;
   #
   if (frame == -1):
      tempframe = letzterFrame;
   #
   bezugsframe = odb.steps[Schritte[tempstep]].frames[tempframe];
   if (not bezugsframe.fieldOutputs.has_key(fieldOutput)):
      Log('# Abbruch: Angeforderter FieldOutput existiert nicht');
      return;
   #
   ausgabeposition = bezugsframe.fieldOutputs[fieldOutput].locations[0].position;
   if (ausgabeposition == NODAL):
      position = NODAL
      sortieren = 'Node Label';
   else:
      position = INTEGRATION_POINT;
      sortieren = 'Element Label';
   #
   komponentenliste = [];
   for komponent in bezugsframe.fieldOutputs[fieldOutput].componentLabels:
      komponentenliste += [(COMPONENT, komponent),];
   #
   savevariable = ((fieldOutput, position, tuple(komponentenliste)), );
   #
   settings_numberformat = material.NumberFormat(numDigits=3, precision=0, format=ENGINEERING);
   session.fieldReportOptions.setValues(printTotal=OFF, printMinMax=OFF,
      numberFormat=settings_numberformat);
   session.writeFieldReport(fileName=dateiname + '.erg', append=OFF, sortItem=sortieren,
      odb=odb, step=tempstep, frame=tempframe, outputPosition=position, variable=savevariable); 
#


# -------------------------------------------------------------------------------------------------
def SkalarenFieldOutputErstellen(name, session, odbname, referenzAusgabe, beschreibung='',
   bedingung='data11'):
   """Fuege einen neuen FieldOutput name zur Ausgabedatei odbname der session mit Daten aus
   referenzAusgabe hinzu. Die Daten im FieldOutput referenzAusgabe koennen skalare Werte oder
   Tensoren sein. Optional kann die Beschreibung angepasst werden. Optional kann ausserdem mit
   bedingung ein Kommando zur Kombination der Eintraege ausgefuehrt werden. Fuer einen Ausdruck in
   bedingung entsprechen [data11, data22, data33, data12, data13, data23] den sechs Eintraegen
   eines Tensorfeldes. Bei einem Skalar entspricht data11 dem Zahlenwert.
   
   Fuer mathematische Zusammenhaenge stehen die Funktionen sqrt, sin, cos, tan, asin, acos, atan
   zur Verfuegung.
   """
   from math import sqrt, sin, cos, tan, asin, acos, atan
   import odbAccess
   from abaqusConstants import SCALAR, INTEGRATION_POINT
   from hilfen import Log, _Eval_Basispruefung
   #
   Log('# Erstelle FieldOutput ' + name);
   mySteps = session.odbData[odbname].steps.keys();
   if (session.odbs[odbname].steps[mySteps[0]].frames[0].fieldOutputs.has_key(name)):
      Log('# Abbruch: FieldOutput ' + name + ' existiert bereits');
      return;
   #
   if (not session.odbs[odbname].steps[mySteps[0]].frames[0].fieldOutputs.has_key(referenzAusgabe)):
      Log('# Abbruch: FieldOuptut ' + referenzAusgabe + ' benoetigt, aber nicht verfuegbar');
      return;
   #
   if (session.odbs[odbname].isReadOnly):
      Log('# Abbruch: Kein Schreibzugriff auf die odb moeglich - read only deaktivieren');
      return;
   #
   if (not _Eval_Basispruefung(code=bedingung,
      zusatz_erlaubt=['data11', 'data22', 'data33', 'data12', 'data23', 'data13'])):
      Log('# Abbruch: Uebergebene bedingung ist ungueltig');
      return;
   #
   useScalar = False;
   if (session.odbs[odbname].steps[mySteps[0]].frames[0].fieldOutputs[referenzAusgabe].type == SCALAR):
      useScalar = True;
   #
   for istep in range(len(mySteps)):
      myFrames = session.odbData[odbname].steps[mySteps[istep]].frames.keys();
      for iframe in range(len(myFrames)):
         Log('#  Status ' + str(istep+1) + '/' + str(len(mySteps)) + ' (' + str(iframe+1) + '/' + str(len(myFrames)) + ')', True);
         tempframe = session.odbs[odbname].steps[mySteps[istep]].frames[iframe];
         refDaten = tempframe.fieldOutputs[referenzAusgabe];
         neuesFeld = tempframe.FieldOutput(name=name, description=beschreibung, type=SCALAR);
         daten = [];
         bezeichnungen = [];
         if useScalar:
            for element in refDaten.values:
               data11 = element.data;
               neueDaten = eval(bedingung);
               daten = daten + [(neueDaten,)];
               bezeichnungen = bezeichnungen + [element.elementLabel];
         else:
            for elements in refDaten.values:
               data11 = elements.data[0];
               data22 = elements.data[1];
               data33 = elements.data[2];
               data12 = elements.data[3];
               # Die letzten beiden Komponenten sind nur fuer 3D-Tensoren verfuegbar
               try:
                  data13 = elements.data[4];
                  data23 = elements.data[5];
               except IndexError:
                  pass;
               #
               neueDaten = eval(bedingung);
               daten = daten + [(neueDaten,)];
               bezeichnungen = bezeichnungen + [elements.elementLabel];
         #
         neuesFeld.addData(position=INTEGRATION_POINT, instance=refDaten.values[0].instance,
            labels=tuple(bezeichnungen), data=tuple(daten));
   #
   Log('# FieldOutput ' + name + ' hinzugefuegt', True);
   Log('');
#


# -------------------------------------------------------------------------------------------------
def DehnungsInvarianteAlsFieldOutput(name, session, odbname, beschreibung='Dehungsinvariante'):
   """Fuege einen neuen FieldOutput namens name zur Ausgabedatei odbname der session mit der
   Dehnungsinvariante hinzu. Optional kann die Beschreibung angepasst werden.
   """
   SkalarenFieldOutputErstellen(name=name, beschreibung=beschreibung, session=session,
      odbname=odbname, referenzAusgabe='ER',
      bedingung='sqrt(4.0/9.0*(data11**2 + data22**2 + data33**2 - data11*data22 - data11*data33 - data22*data33) + 2.0*(data12**2 + data13**2 + data23**2))');
   # siehe dazu auch D. Kolymbas (2011): Geotechnik, S. 251
#


# -------------------------------------------------------------------------------------------------
def SpannungsSpurAlsFieldOutput(name, session, odbname, spannungstyp='SVAVG',
   beschreibung='Spur des Spannungstensors'):
   """Fuege einen neuen FieldOutput namens name zur Ausgabedatei odbname der session mit der
   Spur des Spannungstensors hinzu. Als spannungstyp kann zwischen 'S' und 'SVAVG'
   unterschieden werden. Optional kann ausserdem die Beschreibung angepasst werden.
   """
   SkalarenFieldOutputErstellen(name=name, beschreibung=beschreibung, session=session,
      odbname=odbname, referenzAusgabe=spannungstyp, bedingung='data11 + data22 + data33');
#
