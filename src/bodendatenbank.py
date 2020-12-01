# -*- coding: utf-8 -*-
"""
bodendatenbank.py   v1.0 (2020-09)
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
def _Name_Aktuellste_Materialdatenbank():
   import os
   from hilfen import Log, _PfadZusatzdateien
   #
   dateien = os.listdir(_PfadZusatzdateien());
   kandidaten = [];
   for datei in dateien:
      if (datei.startswith('Materialdatenbank')):
         kandidaten += [datei];
   #
   kandidaten.sort();
   if (len(kandidaten) == 0):
      Log('# Fehler: Konnte keine Materialdatenbank finden');
      return None;
   else:
      return os.path.join(_PfadZusatzdateien(), kandidaten[-1]);
#


# -------------------------------------------------------------------------------------------------
def _Bodenparameter_Aus_Tabelle(name, bezeichnung='labor'):
   """Lade fuer den Boden name die Bodenparameter nach dem stoffgesetz aus der hinterlegten Datei
   "Materialdatenbank.xlsx". Gibt [eintragVorhanden, bodenwerte, standardwerte] zurueck.
   """
   from hilfen import Log
   dateiname = _Name_Aktuellste_Materialdatenbank();
   if (dateiname is None):
      return [[], [], []];
   #
   try:
      from openpyxl import load_workbook
   except:
      Log('# Fehler: openpyxl (und Abhaengigkeiten) zum Laden von xlsx-Dateien nicht gefunden');
      return [[], [], []];
   #
   try:
      xlsxfile = load_workbook(filename=dateiname, read_only=True);
   except:
      Log('# Fehler: Konnte Materialdatenbank ' + dateiname + ' nicht laden');
      return [[], [], []];
   #
   xlsxsheet = xlsxfile['Materialdatenbank'];
   eintragVorhanden = False;
   #
   anzahlZellen = 39;
   standardwerte = anzahlZellen * [''];
   bodenwerte = anzahlZellen * [''];
   for zeile in xlsxsheet.rows:
      zeile_bodenname = zeile[0].value;
      if (zeile_bodenname is None):
         continue;
      #
      if (zeile_bodenname == 'Standardparameter'):
         for iZelle in range(anzahlZellen):
            standardwerte[iZelle] = zeile[iZelle].value;
      #
      if (str(zeile_bodenname) == name):
         zeile_bezeichnung = zeile[1].value;
         if ((str(zeile_bezeichnung) == bezeichnung) or
            (((bezeichnung == 'labor') or (bezeichnung == '')) and
            ((zeile_bezeichnung is None) or (zeile_bezeichnung == 'labor')))):
            #
            eintragVorhanden = True;
            for iZelle in range(anzahlZellen):
               bodenwerte[iZelle] = zeile[iZelle].value;
            #
            break;
   #
   return [eintragVorhanden, bodenwerte, standardwerte];
#


# -------------------------------------------------------------------------------------------------
def Bodenparameter(name, stoffgesetz, bezeichnung='labor'):
   """Lade fuer den Boden name die Bodenparameter nach dem stoffgesetz. Die in der dazugehoerigen
   Materialdatenbank gespeicherten Eintraege koennen mithilfe ihres Namens - und optional bei
   mehreren gleichnamigen Eintraegen mit einer zusaetzlichen bezeichnung - geladen werden.
   Gibt die dazugehoerigen bodenparameter zurueck.
   """
   from hilfen import grad2rad, Log
   #
   parameter = None;
   eintragVorhanden, bodenwerte, standardwerte = _Bodenparameter_Aus_Tabelle(name, bezeichnung=bezeichnung);
   if (eintragVorhanden == []):
      return None;
   #
   if (not eintragVorhanden):
      Log('# Warnung: Keine Parameter fuer Eintrag >' + name + '< in der Materialdatenbank gefunden');
      return None;
   # Alle fehlenden Eintraege des Datensatzes durch Standardwerte ersetzen
   for iWert, kennwert in enumerate(bodenwerte):
      if (kennwert is None):
         bodenwerte[iWert] = standardwerte[iWert];
   #
   idx_basis = 3;
   idx_hypo = 8;
   idx_visco = 16;
   idx_erw = 24;
   idx_mc = 30;
   #
   stoffgesetz_klein = stoffgesetz.lower();
   basisparameter = bodenwerte[idx_basis:idx_basis+2] + [grad2rad*bodenwerte[idx_basis+2]];
   if   ((stoffgesetz_klein == 'elastisch') or (stoffgesetz_klein == 'elastic')):
      parameter = basisparameter +   bodenwerte[idx_mc:idx_mc+2];
      #           0: min. Dichte     3: E-Modul
      #           1: max. Dichte     4: Querdehnzahl
      #           2: krit.Reibwinkel 
   #
   elif (stoffgesetz_klein == 'mohr-coulomb'):
      parameter = basisparameter   + bodenwerte[idx_mc:idx_mc+2] + [bodenwerte[idx_basis+2]] + bodenwerte[idx_mc+2:idx_mc+5];
      #           0: min. Dichte     3: E-Modul                    5: Reibungswert             6: Dilatanzwinkel
      #           1: max. Dichte     4: Querdehnzahl                                           7: Koh.-Fliessspg.
      #           2: krit.Reibwinkel                                                           8: Plast.Dehnung
   #
   elif (('viskohypoplasti' in stoffgesetz_klein) or ('viscohypoplasti' in stoffgesetz_klein)):
      #           0: min. Dichte    3: 100-Porenzahl          4: Querdehnzahl          5: Kompr-Beiwert                      9: Ref.-Dehnung
      #           1: max. Dichte                                                       6: Schwellbeiwert
      #           2: krit.Reibwinkel                                                   7: Belast.-Flaeche
      #                                                                                8: I_v
      parameter = basisparameter +  [bodenwerte[idx_visco]] + [bodenwerte[idx_mc+1]] + bodenwerte[idx_visco+1:idx_visco+5] + [0.000001*bodenwerte[idx_visco+5]] + \
         [0.0]   +   bodenwerte[idx_erw:idx_erw+2] + [0.000001*bodenwerte[idx_erw+2]] + bodenwerte[idx_erw+3:idx_erw+5] + [bodenwerte[idx_visco+6]];
      #  10: [leer]  11: Faktor m_T                  13: Konstante R_max                14: Exponent alpha                16: Ueberkons-grad
      #              12: Faktor m_R                                                     15: Exponent beta
   #
   elif ('hypoplasti' in stoffgesetz_klein):
      #           0: min. Dichte    3: Querdehnzahl          4: Granulathaerte             5: Exponent n
      #           1: max. Dichte                                                           6: dicht.Porenzahl
      #           2: krit.Reibwinkel                                                       7: lock.Porenzahl
      #                                                                                    8: krit.Porenzahl
      #                                                                                    9: Exponent alpha
      #                                                                                    10: Exponent beta
      parameter = basisparameter +  [bodenwerte[idx_mc+1]] + [1000*bodenwerte[idx_hypo]] + bodenwerte[idx_hypo+1:idx_hypo+7] + \
         bodenwerte[idx_erw:idx_erw+2] + [0.000001*bodenwerte[idx_erw+2]] + bodenwerte[idx_erw+3:idx_erw+5];
      #  11: Faktor m_T                  13: Konstante R_max                14: Exponent beta_R
      #  12: Faktor m_R                                                     15: Exponent chi
   #
   else:
      parameter = None;
      Log('# Warnung: Kein passenden Satz an Bodenparametern fuer Stoffgesetz >' + stoffgesetz + '< gefunden');
      return None;
   #
   # Falls Standardwerte fuer erweiterte hypoplastische Parameter verwendet oder alle ignoriert
   # werden sollen
   if ('stdig' in stoffgesetz_klein):
      # "Standardwerte" der erweiterten hypoplastischen Parameter
      #
      #                  Faktor    Faktor    Konstante   Exponent     Exponent
      #                  m_T [-]   m_R [-]   R_max [-]   beta_R [-]   chi [-]
      #                |---------|---------|-----------|------------|----------|
      parameter[11:16] = [ 2.0,      5.0,      1e-4,       0.5,         5.0      ];
   #
   if ('ohneig' in stoffgesetz_klein):
      # "Deaktivierung" der erweiterten hypoplastischen Parameter durch m_T und m_R < 2.0
      #
      #                  Faktor    Faktor    Konstante   Exponent     Exponent
      #                  m_T [-]   m_R [-]   R_max [-]   beta_R [-]   chi [-]
      #                |---------|---------|-----------|------------|----------|
      parameter[11:16] = [ 1.0,      1.0,      1.0,        1.0,         1.0      ];
   #
   return parameter;
#
