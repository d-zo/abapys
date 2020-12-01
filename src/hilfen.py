# -*- coding: utf-8 -*-
"""
hilfen.py   v3.3 (2020-11)
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


# Oeffentliche globale Hilfsvariablen
abapys_tol = 1e-6;
grad2rad = 3.141592653589793/180.0;
g = 9.81; # m/s^2


# Interne globale Hilfsvariablen
_abapysInitialisiert = False;
_abaqusGUIStarted = False;
_abaqusVersion = None;
_abapysPfadZusatzdateien = '';
_abaqusOS = '';

_ppi = 96.0/25.4; # dpi/inch
_xSkalierung = 1.0;
_ySkalierung = 1.0;


# -------------------------------------------------------------------------------------------------
def InitialisiereAbapys(session, version=2018, pfad='/exports/all/intern/abapys/', xSkalierung=None,
   ySkalierung=None):
   """Erkenne und speichere, ob sich die aktuelle session in der GUI oder Konsole befindet und
   welche version von Abaqus verwendet wird. Dazu werden die internen Variablen von Abaqus
   uebergeben, so dass session und version nicht manuell definiert werden muessen. Normalerweise
   koennen also die Argumente (session=session, version=version) uebergeben werden.
   
   Falls nicht der Standardpfad fuer zusaetzliche Dateien (bspw. Bibliotheken oder Materialtabelle)
   genutzt werden soll, kann der Pfad explizit ueber pfad angegeben werden. In dieser Funktion
   werden Skalierungswerte fuer den Viewport bei einer Bildausgabe berechnet, die aber durch
   Uebergabe der Faktoren xSkalierung und ySkalierung ueberschrieben werden koennen.
   """
   import os
   #
   global _abapysInitialisiert;
   _abapysInitialisiert = True;
   #
   global _abaqusGUIStarted;
   _abaqusGUIStarted = session.attachedToGui;
   #
   global _abaqusVersion;
   _abaqusVersion = version;
   #
   global _abapysPfadZusatzdateien;
   _abapysPfadZusatzdateien = pfad;
   #
   global _abaqusOS;
   global _xSkalierung;
   global _ySkalierung;
   # platform.system() funtioniert in der untersuchten Windows 10/Abaqus 2018-Kombination nicht.
   # Deshalb wird aus Kompatibilitaet os.name verwendet
   if (os.name == 'nt'):
      _abaqusOS = 'Windows';
      _xSkalierung = 0.9990166;
      _ySkalierung = 1.0004557;
   elif (os.name == 'posix'):
      _abaqusOS = 'Linux';
      _xSkalierung = 1.0;
      _ySkalierung = 1.0026315;
   else:
      Log('# Warnung: Betriebssystem nicht unterstuetzt');
      _abaqusOS = '?';
   #
   if (xSkalierung is not None):
      _xSkalierung = xSkalierung;
   #
   if (ySkalierung is not None):
      _ySkalierung = ySkalierung;
#


# -------------------------------------------------------------------------------------------------
def _PfadZusatzdateien():
   """Um im Modul ausserhalb der Datei auf eine globale Variable zugreifen zu koennen, die sich
   aendern koennte, wird diese Hilfsfunktion verwendet. Gibt den Pfad zu abapys-Zusatzdateien
   zurueck.
   """
   return _abapysPfadZusatzdateien;
#


# -------------------------------------------------------------------------------------------------
def _VersionAbaqus():
   """Gibt die Version von Abaqus zurueck, sofern abapys entsprechend initialisiert worden ist.
   Ansonsten None
   """
   return _abaqusVersion;
#


# -------------------------------------------------------------------------------------------------
def BibliothekLaden(dateiname):
   """Lade eine kompilierte Bibliothek (.so unter Linux und .dll unter Windows) und gebe die mit
   ctypes geoeffnete Bibliothek zurueck. dateiname ist ohne Endung (d.h. ohne .so/.dll) anzugeben.
   Die Bibliothek wird aus dem Verzeichnis von abapys bzw. dem ueber das pfad-Argument im Befehl
   InitialisiereAbapys() geladen. Gibt den ctypes-Zugriffspunkt auf die bibliothek zurueck.
   """
   from os import path
   #
   bibliothek = None;
   # Annahme: Linux oder Windows
   if (_abaqusOS == 'Linux'):
      from ctypes import cdll
      #
      name_bibliothek = path.join(_PfadZusatzdateien(), dateiname + '.so');
      Log('# Lade Bibliothek: ' + name_bibliothek);
      try:
         bibliothek = cdll.LoadLibrary(name_bibliothek);
      except:
         pass;
   elif (_abaqusOS == 'Windows'):
      from ctypes import WinDLL
      #
      # Unter Windows wird die Endung automatisch hinzugefuegt
      name_bibliothek = path.join(_PfadZusatzdateien(), dateiname);
      Log('# Lade Bibliothek: ' + name_bibliothek + '.dll');
      try:
         bibliothek = WinDLL(name_bibliothek);
      except:
         pass;
   else:
      Log('# Warnung: Betriebssystem zum Laden von Bibliotheken nicht unterstuetzt - InitialisiereAbapys() vergessen?');
   #
   return bibliothek;
#


# -------------------------------------------------------------------------------------------------
def ViewportGroesseAendern(viewport, bildgroesse):
   """Aendere die Groesse von viewport zu bildgroesse (in Pixel).
   """
   from abaqusConstants import ON
   #
   # Die Rahmenbreite beruecksichtigen
   bildgroesse[0] += 10; # 10px breiter
   bildgroesse[1] += 31; # 31px hoeher
   #
   bildbreite = bildgroesse[0]/_ppi/_xSkalierung;
   bildhoehe = bildgroesse[1]/_ppi/_ySkalierung;
   try:
      viewport.restore();
      viewport.setValues(width=bildbreite, height=bildhoehe);
   except: # RangeError:
      Log('# Warnung: Ungueltige Bildgroesse (nichts geaendert)');
#


# -------------------------------------------------------------------------------------------------
def ViewportPixelGroesseExtrahieren(viewport):
   """Gibt die Groesse von viewport in Pixeln [breite, hoehe] zurueck.
   """
   from abaqusConstants import OFF
   #
   bildbreite = round(viewport.currentWidth*_ppi*_xSkalierung);
   bildhoehe = round(viewport.currentHeight*_ppi*_ySkalierung);
   #
   # Die Rahmenbreite beruecksichtigen
   bildbreite -= 10;
   bildhoehe -= 31;
   #
   return [bildbreite, bildhoehe];
#


# -------------------------------------------------------------------------------------------------
def ErstelleLabelsortierteGeomlist(geomliste):
   """Gibt ein Dictionary mit den labels und den indizes der uebergebenen geomliste zurueck, um
   anschliessend schnell ueber die Labels statt Indizes auf die Eintraege aus geomliste zugreifen
   zu koennen.
   """
   templist = [];
   idx = 0;
   for geom in geomliste:
      templist += [(geom.label, idx),];
      idx += 1;
   #
   return dict(templist);
#


# -------------------------------------------------------------------------------------------------
def ErstelleElementLabelsortierteGeomlist(geomliste):
   """Gibt ein Dictionary mit den elementLabels und den indizes der uebergebenen geomliste zurueck,
   um anschliessend schnell ueber die elementLabels statt Indizes auf die Eintraege aus geomliste
   zugreifen zu koennen.
   """
   templist = [];
   idx = 0;
   for geom in geomliste:
      templist += [(geom.elementLabel, idx),];
      idx += 1;
   #
   return dict(templist);
#


# -------------------------------------------------------------------------------------------------
def ErstelleNodeLabelsortierteGeomlist(geomliste):
   """Gibt ein Dictionary mit den nodeLabels und den indizes der uebergebenen geomliste zurueck,
   um anschliessend schnell ueber die nodeLabels statt Indizes auf die Eintraege aus geomliste
   zugreifen zu koennen.
   """
   templist = [];
   idx = 0;
   for geom in geomliste:
      templist += [(geom.nodeLabel, idx),];
      idx += 1;
   #
   return dict(templist);
#


# -------------------------------------------------------------------------------------------------
def ElementeMitZielwert(elemliste, zielwert):
   """Pruefe alle Elemente in elemliste, ob deren Wert (elemliste[#].data) dem zielwert entspricht.
   Gibt [Labels] der Elemente zurueck, fuer die das gilt.
   """
   idxZielwert = [];
   for elem in elemliste:
      if (elem.data == zielwert):
         idxZielwert = idxZielwert + [elem.elementLabel];
   #
   return idxZielwert;
#


# -------------------------------------------------------------------------------------------------
def ElementAusOdb(element):
   """Pruefe anhand des uebergebenen element, aus welchem Kontext das element stammt. Gibt True
   zurueck, wenn ein Bezug zu session.odbs[...].rootAssembly.instances[...].elements vorhanden ist,
   ansonsten False
   """
   # unterstuetzte mdb-Bezuege sind mdb.models[...].rootAssembly.instances[...].elements und
   # mdb.models[...].parts[...].elements, nach denen aber nicht explizit geprueft wird.
   istOdb = True;
   try:
      # Versuche herauszufinden, ob es sich um odb-elemente oder mdb-elemente handelt. instanceNames
      # scheint nur in odb-elementen zu existieren. Alternativ waere es denkbar, mithilfe von
      # elements[0].__subclasshook__ und einer Filterung nach odb zu pruefen
      tempNames = element.instanceNames;
   except AttributeError:
      istOdb = False;
   #
   return istOdb;
#


# -------------------------------------------------------------------------------------------------
def Einheitsvektor(dim, idxEins):
   """Erstelle einen Vektor der Groesse dim, der ueberall Nullen hat und eine Eins an der Stelle
   idxEins. Gibt den Einheitsvektor zurueck.
   """
   if ((not isinstance(dim, (int, long))) or (not isinstance(dim, (int, long)))):
      #Log('# Abbruch: dim und idxEins muessen ganzzahlige Werte sein');
      return [];
   #
   if (dim <= 0):
      #Log('# Abbruch: Ungueltige Dimension (muss >0 sein)');
      return [];
   #
   if ((idxEins < 0) or (idxEins >= dim)):
      #Log('# Abbruch: Ungueltiger Index fuer den Einsereintrag (muss <dim sein)');
      return [];
   #
   vektor = [0,] * dim;
   vektor[idxEins] = 1;
   return tuple(vektor);
#


# -------------------------------------------------------------------------------------------------
def GueltigenNamenFinden(umgebung, namensvorschlag):
   """Waehle basierend auf dem namensvorschlag einen eindeutigen Namen, der in der uebergebenen
   umgebung noch nicht existiert. Dazu wird der namensvorschlag geprueft und mit einer Zahl von
   000-900 erweitert, bis er eindeutig ist. Gibt den (ggfs. ueberarbeiteten) namensvorschlag zurueck.
   """
   name = namensvorschlag;
   for idx in range(900):
      name = namensvorschlag + '_' + str(idx).zfill(3);
      if (not (umgebung.has_key(name))):
         break;
   #
   return name;
#


# -------------------------------------------------------------------------------------------------
def OrdnerPruefen(ordnername):
   """Prueft die Existenz eines Ordners ordnername und erstellt ihn, falls er nicht vorhanden ist.
   """
   from os import path
   from os import makedirs
   #
   if (not path.isdir(ordnername)):
      Log('# Ordner ' + ordnername + ' existiert nicht und wird erstellt');
      # Schlaegt fehl, wenn Datei mit dem gleichen Namen existiert oder Ordner
      # existiert wenn makedirs aufgerufen wird
      makedirs(ordnername);
#


# -------------------------------------------------------------------------------------------------
def BlockAusgabe(ausgabeliste, eintraegeProZeile=8, trennung=', '):
   """Die ausgabeliste wird pro Zeile auf eintraegeProZeile begrenzt und der Rest in
   einer oder mehreren Folgezeilen ausgegeben. Dabei wird die trennung zwischen jeden der Eintraege
   eingefuegt. Gibt einen String zurueck, der nach allen eintraegeProZeile ein '\n' enthaelt.
   """
   idx_Zeilenende = eintraegeProZeile;
   numEintraege = len(ausgabeliste);
   if (numEintraege < eintraegeProZeile):
      idx_Zeilenende = numEintraege;
   #
   ausgabe = trennung.join(str(x) for x in ausgabeliste[0:idx_Zeilenende]) + '\n';
   while (idx_Zeilenende < numEintraege):
      idx_Zeilenstart = idx_Zeilenende;
      idx_Zeilenende += eintraegeProZeile;
      if (numEintraege < idx_Zeilenende):
         idx_Zeilenende = numEintraege;
      #
      ausgabe += trennung.join(str(x) for x in ausgabeliste[idx_Zeilenstart:idx_Zeilenende]) + '\n';
   #
   return ausgabe;
#


# -------------------------------------------------------------------------------------------------
def _Eval_Basispruefung(code, zusatz_erlaubt):
   """Prueft den uebergebenen code auf bekannte Schluesselwoerter fuer Auswahlen aus Abaqus
   (inklusive denen aus der uebergebenen Liste zusatz_erlaubt). Falls unbekannte/unerlaubte
   Schluesselwoerter in code vorkommen, wird False zurueckgegeben, ansonsten True.
   
   HINWEIS: Auch durch diese Ueberpruefung von Code, der bei Erfolg in eval ausgefuehrt wird, ist
   ein mutwilliger Missbrauch von eval nicht ausgeschlossen!
   """
   from re import compile as re_compile
   from re import search as re_search
   #
   # Alle erlaubten Bezeichnungen im Code
   erlaubt = ['True', 'False', 'and', 'or', 'not', # Logische Operatoren
              '==', '<', '<=', '>', '>=', 'in', # Vergleichsoperatoren
              'pi', 'sqrt', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'abs']; # Mathematische Operatoren
   #
   # Attribute von Abaqus-Elementen: vertices/edges/faces/cells (mdb) sowie nodes und elements
   erlaubt += ['coordinates', 'connectivity', 'featureName', 'index', 'instanceName',
      'instanceNames', 'isReferenceRep', 'pointOn', 'sectionCategory', 'label', 'type'];
   #
   erlaubt += zusatz_erlaubt;
   #
   # Strings ignorieren
   string_idx = [];
   temp_idx = 0;
   while (True):
      temp_idx = code.find('\'', temp_idx+1);
      if (temp_idx == -1):
         break;
      #
      string_idx += [temp_idx];
   #
   if ((len(string_idx) % 2) != 0):
      Log('# Abbruch: Ungueltige Anzahl an Anfuehrungszeichen');
      return False;
   #
   if (len(string_idx) > 1):
      for idx in range(len(string_idx)//2):
         code = code[:string_idx[2*idx]] +  ' ' * (string_idx[2*idx+1]-string_idx[2*idx]+1) + code[string_idx[2*idx+1]+1:];
   #
   # Der Rest sollten nur normale Zahlen sein
   remuster = re_compile('^[0-9.]*$');
   #
   # Den code in einzelne Segmente aufteilen und einzeln ueberpruefen.
   codeteile = code.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ') \
      .replace('.', ' ').replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split();
   for einzelteil in codeteile:
      if (einzelteil not in erlaubt):
         if (not (re_search(remuster, einzelteil))):
            Log('# Abbruch: Ungueltige Zeichenkette in eval: >' + einzelteil + '<');
            return False;
   #
   return True;
#


# -------------------------------------------------------------------------------------------------
def Log(ausgabe, ueberschreiben=False):
   """Die uebergebene ausgabe entweder in Abaqus behalten oder in die Konsole umleiten, falls abapys
   initialisiert worden ist und die GUI nicht aktiv ist. Optional kann ein ueberschreiben der
   Ausgabe aktiviert werden (z.B. fuer Status-/Prozentangaben).
   """
   from sys import __stdout__
   if (_abapysInitialisiert and (not _abaqusGUIStarted)):
      if (ueberschreiben):
         print >> __stdout__, "\r" + ausgabe, ;
      else:
         print >> __stdout__, ausgabe;
   else:
      if (ueberschreiben):
         print "\r" + ausgabe, ;
      else:
         print(ausgabe);
#
