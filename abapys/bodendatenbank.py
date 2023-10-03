# -*- coding: utf-8 -*-
"""
bodendatenbank.py   v1.0 (2020-09)
"""

# Copyright 2020-2021 Dominik Zobel.
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
   idx_hypo = 9;
   idx_visco = 17;
   idx_erw = 25;
   idx_mc = 31;
   #
   stoffgesetz_klein = stoffgesetz.lower();
   basisparameter = bodenwerte[idx_basis:idx_basis+3] + [grad2rad*bodenwerte[idx_basis+3]];
   if   ((stoffgesetz_klein == 'elastisch') or (stoffgesetz_klein == 'elastic')):
      parameter = basisparameter +   bodenwerte[idx_mc:idx_mc+2];
      #           0: Korndichte      4: E-Modul
      #           1: min. Dichte     5: Querdehnzahl
      #           2: max. Dichte    
      #           3: krit.Reibwinkel
   #
   elif (stoffgesetz_klein == 'mohr-coulomb'):
      parameter = basisparameter   + bodenwerte[idx_mc:idx_mc+2] + [bodenwerte[idx_basis+3]] + bodenwerte[idx_mc+2:idx_mc+5];
      #           0: Korndichte      4: E-Modul                    6: Reibungswert             7: Dilatanzwinkel
      #           1: min. Dichte     5: Querdehnzahl                                           8: Koh.-Fliessspg.
      #           2: max. Dichte                                                               9: Plast.Dehnung
      #           3: krit.Reibwinkel
   #
   elif (('viskohypoplasti' in stoffgesetz_klein) or ('viscohypoplasti' in stoffgesetz_klein)):
      #           0: Korndichte     4: 100-Porenzahl          5: Querdehnzahl          6: Kompr-Beiwert                      10: Ref.-Dehnung
      #           1: min. Dichte                                                       7: Schwellbeiwert
      #           2: max. Dichte                                                       8: Belast.-Flaeche
      #           3: krit.Reibwinkel                                                   9: I_v
      parameter = basisparameter +  [bodenwerte[idx_visco]] + [bodenwerte[idx_mc+1]] + bodenwerte[idx_visco+1:idx_visco+5] + [0.000001*bodenwerte[idx_visco+5]] + \
         [0.0]   +   bodenwerte[idx_erw:idx_erw+2] + [0.000001*bodenwerte[idx_erw+2]] + bodenwerte[idx_erw+3:idx_erw+5] + [bodenwerte[idx_visco+6]];
      #  11: [leer]  12: Faktor m_T                  14: Konstante R_max                15: Exponent alpha                16: Ueberkons-grad
      #              13: Faktor m_R                                                     16: Exponent beta
   #
   elif ('hypoplasti' in stoffgesetz_klein):
      #           0: Korndichte     4: Querdehnzahl          5: Granulathaerte             6: Exponent n
      #           1: min. Dichte                                                           7: dicht.Porenzahl
      #           2: max. Dichte                                                           8: lock.Porenzahl
      #           3: krit.Reibwinkel                                                       9: krit.Porenzahl
      #                                                                                    10: Exponent alpha
      #                                                                                    11: Exponent beta
      parameter = basisparameter +  [bodenwerte[idx_mc+1]] + [1000*bodenwerte[idx_hypo]] + bodenwerte[idx_hypo+1:idx_hypo+7] + \
         bodenwerte[idx_erw:idx_erw+2] + [0.000001*bodenwerte[idx_erw+2]] + bodenwerte[idx_erw+3:idx_erw+5];
      #  12: Faktor m_T                  14: Konstante R_max                15: Exponent beta_R
      #  13: Faktor m_R                                                     16: Exponent chi
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
      #                    Faktor    Faktor    Konstante   Exponent     Exponent
      #                    m_T [-]   m_R [-]   R_max [-]   beta_R [-]   chi [-]
      #                  |---------|---------|-----------|------------|----------|
      parameter[12:17] = [ 2.0,      5.0,      1e-4,       0.5,         5.0      ];
   #
   if ('ohneig' in stoffgesetz_klein):
      # "Deaktivierung" der erweiterten hypoplastischen Parameter durch m_T und m_R < 2.0
      #
      #                    Faktor    Faktor    Konstante   Exponent     Exponent
      #                    m_T [-]   m_R [-]   R_max [-]   beta_R [-]   chi [-]
      #                  |---------|---------|-----------|------------|----------|
      parameter[12:17] = [ 1.0,      1.0,      1.0,        1.0,         1.0      ];
   #
   return parameter;
#
