# -*- coding: utf-8 -*-
"""
zahnrad.py   v0.8 (2019-08)
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
def Zahnrad_zylindernuten(modell, name, dicke, r_innen, r_aussen, r_zylinder, numZylinder,
   r_aussparung=0.0):
   """Erzeuge im modell ein Zahnrad (Part) name mit gegebener dicke, Innen- und Aussendurchmesser
   r_innen und r_aussen sowie numZylinder zylindrischen Aussparungen (und Zaehnen). Der Radius der
   Aussparungen betraegt r_zylinder. Optional kann eine eine zylindrische Aussparung mit Radius
   r_aussparung hinzugefuegt werden. Gibt [part<name>, inst<name>] zurueck.
   """
   from math import sin, cos, acos, atan, sqrt
   import sketch
   import part
   import assembly
   from abaqusConstants import ON, CLOCKWISE, COUNTERCLOCKWISE, THREE_D, DEFORMABLE_BODY
   from zeichnung import KreisbogenPunkte, Kreis
   from hilfen import grad2rad, Log
   #
   # Ueberpruefungen
   mitSpitze = False;
   mitEvolventenwand = True;
   #
   winkel = 360.0/numZylinder*grad2rad;
   phi = winkel/2.0;
   zylindermpabstand = 2.0 * (r_innen+r_zylinder)*sin(phi);
   #
   r_spitze = (r_innen+r_zylinder)*cos(phi) + \
      sqrt((zylindermpabstand-r_zylinder)**2 - (zylindermpabstand/2.0)**2);
   if (r_aussen > r_spitze):
      Log('Warnung: r_aussen zu gross, verkuerze auf r_spitze');
      r_aussen = r_spitze;
      beta = 0.0;
      mitSpitze = True;
   else:
      beta = acos((r_aussen**2 + (r_innen + r_zylinder)**2 - (zylindermpabstand-r_zylinder)**2)/ \
         (2.0*r_aussen*(r_innen + r_zylinder))) - phi;
   #
   r_kontaktloesung = sqrt(((r_innen+r_zylinder)*cos(phi))**2 + (zylindermpabstand/2.0-r_zylinder)**2);
   if (r_aussen < r_kontaktloesung):
      # Zahn wird naeher am Mittelpunkt abgeschnitten als Verbindungsgerade der Zylindermittelpunkte
      la = (r_innen + r_zylinder)/2.0 + (r_zylinder**2 - r_aussen**2)/(2.0*(r_innen + r_zylinder));
      psi_kontakt = acos(la/r_zylinder);
      #
      l_red = r_zylinder*sin(90*grad2rad-phi-psi_kontakt);
      h_red = zylindermpabstand/2.0-r_zylinder*cos(90*grad2rad-phi-psi_kontakt);
      beta = atan(h_red/((r_innen+r_zylinder)*cos(phi)-l_red));
      mitEvolventenwand = False;
   else:
      psi_kontakt = 90*grad2rad - phi;
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=2.0*r_aussen);
   zeichnung = modell.sketches['__profile__'];
   for idxBereich in range(numZylinder):
      bemasst = False;
      if (idxBereich == 0):
         bemasst = True;
      #
      offsetwinkel = (idxBereich+0.5)*winkel;
      # Jeder Bereich wird in vier Teilstrecken unterteilt, um die Kontur zu zeichnen
      mittelpunkt_aktuell = ((r_innen+r_zylinder)*sin(offsetwinkel),
                             (r_innen+r_zylinder)*cos(offsetwinkel));
      mittelpunkt_naechster = ((r_innen+r_zylinder)*sin(offsetwinkel+winkel),
                               (r_innen+r_zylinder)*cos(offsetwinkel+winkel));
      # 1) Auflageflaeche der Zylinder am Zahnrad
      punkta = (mittelpunkt_aktuell[0] - r_zylinder*sin(offsetwinkel+psi_kontakt),
                mittelpunkt_aktuell[1] - r_zylinder*cos(offsetwinkel+psi_kontakt));
      punktb = (mittelpunkt_aktuell[0] - r_zylinder*sin(offsetwinkel-psi_kontakt),
                mittelpunkt_aktuell[1] - r_zylinder*cos(offsetwinkel-psi_kontakt));
      KreisbogenPunkte(zeichnung=zeichnung, mittelpunkt=mittelpunkt_aktuell,
         punkt1=punkta, punkt2=punktb, richtung=COUNTERCLOCKWISE, bemasst=bemasst);
      # 2) Erste Evolventenwand, falls vorhanden
      if (mitEvolventenwand):
         punkta = punktb;
         punktb = ((r_aussen)*sin(offsetwinkel+phi-beta), (r_aussen)*cos(offsetwinkel+phi-beta));
         KreisbogenPunkte(zeichnung=zeichnung, mittelpunkt=mittelpunkt_naechster,
            punkt1=punkta, punkt2=punktb, richtung=CLOCKWISE, bemasst=bemasst);
      # 3) Aussenlaeche, falls keine Spitze
      if (not mitSpitze):
         punkta = punktb;
         punktb = ((r_aussen)*sin(offsetwinkel+phi+beta), (r_aussen)*cos(offsetwinkel+phi+beta));
         KreisbogenPunkte(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0),
            punkt1=punkta, punkt2=punktb, richtung=CLOCKWISE, bemasst=bemasst);
      # 4) Zweite Evolventenwand, falls vorhanden
      if (mitEvolventenwand):
         punkta = punktb;
         punktb = (mittelpunkt_naechster[0] - r_zylinder*sin(offsetwinkel+winkel+psi_kontakt),
                   mittelpunkt_naechster[1] - r_zylinder*cos(offsetwinkel+winkel+psi_kontakt));
         KreisbogenPunkte(zeichnung=zeichnung, mittelpunkt=mittelpunkt_aktuell, punkt1=punkta,
            punkt2=punktb, richtung=CLOCKWISE, bemasst=bemasst);
   #
   if (r_aussparung > 0.0):
      Kreis(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=r_aussparung);
   #
   partZahnrad = modell.Part(dimensionality=THREE_D, name=name, type=DEFORMABLE_BODY);
   partZahnrad.BaseSolidExtrude(depth=dicke, sketch=zeichnung);
   del zeichnung;
   instname = 'inst' + name;
   instZahnrad = modell.rootAssembly.Instance(dependent=ON, name=instname, part=modell.parts[name]);
   return [partZahnrad, instZahnrad];
#
