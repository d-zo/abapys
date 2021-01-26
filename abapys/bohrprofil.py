# -*- coding: utf-8 -*-
"""
bohrprofil.py   v1.7 (2021-01)
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
def Bohrprofil_VVBP(modell, name, laenge, r_aussen, r_innen, spitzenwinkel, rundwinkel,
   schraublaenge1, profillaenge1, schraublaenge2, profillaenge2, laenge12, ganghoehe, wendeldicke,
   gitter_werkzeug):
   """Erstelle ein Vollverdraengungsbohrprofil name im Modell modell aus den in der folgenden
   Skizze dargestellten Parametern. Die fehlende Groesse gitter_werkzeug gibt die Gitterfeinheit
   bei der Vernetzung des Modells an. Gibt [part<name>, inst<name>] zurueck.
   
   =============        r_aussen  r_innen
   =  V V B P  =       _|________|____|_
   =============        |        |    |
                        |                __________________________|_
                        |   +----+----+                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                        |   |    .    |                            |
                 _|_______  |    .    |     _|_                    |
                  |         |    .    |xxxx _|_wendeldicke         |
                  |     xxxx|    .    |      |                     |
   schraublaenge2 |         |    .    |   ______|_                 |
                  |        /     .     \ xx     |                  |
                  |     xx/      .      \       | profillaenge2    |
            _|____|___   /       .       \   ___|_                 |
             |    |     |        .        |     |                  | laenge
             |          |        .        |                        |
    laenge12 |          |        .        |                        |
             |          |        .        |                        |
            _|____|___  |        .        |  ___|_                 |
                  |     x\       .       /      |                  |
                  |       \      .      /xx     | profillaenge1    |
                  |        \     .     /  ______|_                 |
   schraublaenge1 |     xxxx|    .    |         |                  |
                  |         |    .    |xxxx ________|_             |
                  |         |    .    |             |              |
                  |     xxxx|    .    |             | ganghoehe    |
                 _|_______  |    .    |xxxx _|______|______________|_
                  |          \   .   /       |      |              |
                         --.  \  .  /        | 
                 rundwinkel \  \ . /         | spitzenlaenge = r_innen*tan(grad2rad*spitzenwinkel)
                             |  \./  ________|_
                                 '           |
   
   Zusaetzlich muss gelten: 0 <= spitzenwinkel < 90 und 0 <= rundwinkel <= 90 - 2*|45-spitzenwinkel|
   """
   import part
   import assembly
   from abaqusConstants import GEOMETRY, DELETE, ON
   from erstellung import NamePartInstance
   #
   nameSeele = NamePartInstance(modell=modell, namensvorschlag='Seele');
   # Seele des VVBP erzeugen
   _Bohrprofil_vvbpstange(modell=modell, name=nameSeele, laenge=laenge, r_aussen=r_aussen,
      r_innen=r_innen, spitzenwinkel=spitzenwinkel, rundwinkel=rundwinkel,
      schraublaenge1=schraublaenge1, profillaenge1=profillaenge1, schraublaenge2=schraublaenge2,
      profillaenge2=profillaenge2, laenge12=laenge12);
   # Verschiedene Wendeln erzeugen
   nameWendelVorn = NamePartInstance(modell=modell, namensvorschlag='WendelVorn');
   _Bohrprofil_wendelstueck(modell=modell, name=nameWendelVorn, r_aussen=r_aussen, r_innen=r_innen,
      ganghoehe=ganghoehe, wendeldicke=wendeldicke, hoehe=schraublaenge1);
   nameWendelHalb = NamePartInstance(modell=modell, namensvorschlag='WendelHalb');
   _Bohrprofil_wendelstueck(modell=modell, name=nameWendelHalb, r_aussen=r_aussen, r_innen=r_innen,
      ganghoehe=ganghoehe, wendeldicke=wendeldicke, hoehe=0.5*ganghoehe);
   nameWendelRueck = NamePartInstance(modell=modell, namensvorschlag='WendelRueck');
   _Bohrprofil_wendelstueck(modell=modell, name=nameWendelRueck, r_aussen=r_aussen, r_innen=r_innen,
      ganghoehe=-ganghoehe, wendeldicke=wendeldicke, hoehe=schraublaenge2);
   nameinstSeele = 'inst' + nameSeele;
   nameinstWendelVorn = 'inst' + nameWendelVorn;
   nameinstWendelHalb = 'inst' + nameWendelHalb;
   nameinstWendelRueck = 'inst' + nameWendelRueck;
   # Alle Bestandteile ausrichten
   #
   modell.rootAssembly.Instance(dependent=ON, name=nameinstSeele, part=modell.parts[nameSeele]);
   modell.rootAssembly.Instance(dependent=ON, name=nameinstWendelVorn,
      part=modell.parts[nameWendelVorn]);
   modell.rootAssembly.Instance(dependent=ON, name=nameinstWendelHalb,
      part=modell.parts[nameWendelHalb]);
   modell.rootAssembly.Instance(dependent=ON, name=nameinstWendelRueck,
      part=modell.parts[nameWendelRueck]);
   #
   modell.rootAssembly.rotate(angle=-90.0, axisDirection=(-1.0, 0.0, 0.0), axisPoint=(1.0, 0.0, 0.0),
      instanceList=(nameinstSeele, nameinstWendelHalb, nameinstWendelVorn, nameinstWendelRueck));
   modell.rootAssembly.rotate(angle=(360.0*schraublaenge1/ganghoehe)%360.0,
      axisDirection=(0.0, 0.0, 1.0), axisPoint=(0.0, 0.0, 1.0),
      instanceList=(nameinstWendelVorn, nameinstWendelRueck, ));
   modell.rootAssembly.translate(instanceList=(nameinstWendelHalb, ),
      vector=(0.0, 0.0, wendeldicke+0.5*ganghoehe));
   modell.rootAssembly.translate(instanceList=(nameinstWendelVorn, ),
      vector=(0.0, 0.0, wendeldicke+schraublaenge1));
   modell.rootAssembly.translate(instanceList=(nameinstWendelRueck, ),
      vector=(0.0, 0.0, schraublaenge1+laenge12));
   #
   modell.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(
      modell.rootAssembly.instances[nameinstSeele],
      modell.rootAssembly.instances[nameinstWendelVorn],
      modell.rootAssembly.instances[nameinstWendelHalb],
      modell.rootAssembly.instances[nameinstWendelRueck]), 
      name=name, originalInstances=DELETE);
   nameabqinstFinal = name + '-1';
   nameinstFinal = 'inst' + name;
   modell.rootAssembly.features.changeKey(fromName=nameabqinstFinal, toName=nameinstFinal);
   # Aufraeumen
   del modell.parts[nameSeele];
   del modell.parts[nameWendelVorn];
   del modell.parts[nameWendelHalb];
   del modell.parts[nameWendelRueck];
   del modell.rootAssembly.features[nameinstFinal];
   #
   partWerkzeug = modell.parts[name];
   partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge1+laenge12+schraublaenge2));
   partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Gewindeende');
   if (not schraublaenge2 == profillaenge2):
      partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge1+laenge12+profillaenge2));
      partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Profilendeb');
   #
   partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge1-profillaenge1));
   partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Profilendea');
   partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge1));
   partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Gewindeendea');
   partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge1+laenge12));
   partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Gewindeendeb');
   #
   partWerkzeug.ReferencePoint(point=(0.0, 0.0, laenge));
   #
   _Bohrprofil_partitionieren(modell=modell, name=name, spitzenwinkel=spitzenwinkel);
   _Bohrprofil_vernetzen(modell=modell, name=name, gitter=gitter_werkzeug);
   instWerkzeug = _Bohrprofil_positionieren(modell=modell, name=name, typ='VVBP', radius=r_innen,
      spitzenwinkel=spitzenwinkel);
   return [partWerkzeug, instWerkzeug];
#


# -------------------------------------------------------------------------------------------------
def Bohrprofil_SOBP(modell, name, laenge, r_aussen, r_innen, spitzenwinkel, rundwinkel,
   schraublaenge, ganghoehe, wendeldicke, gitter_werkzeug):
   """Erstelle ein Bohrprofil name im Modell modell aus den in der folgenden Skizze dargestellten
   Parametern. Die fehlende Groesse gitter_werkzeug gibt die Gitterfeinheit bei der Vernetzung des
   Modells an. Gibt [part<name>, inst<name>] zurueck.

   =============       r_aussen  r_innen
   =  S O B P  =      _|________|____|_
   =============       |        |    |
                       |                ______________________|_
                       |   +----+----+                        |
                       |   |    .    |                        |
                       |   |    .    |                        |
                       |   |    .    |                        |
                       |   |    .    |                        |
                           |    .    |                        |
                _|____ xxxx|    .    |     _|_                |
                 |         |    .    |xxxx _|_wendeldicke     |
                 |         |    .    |      |                 |
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx                    |
                 |         |    .    |                        |
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx                    |
                 |         |    .    |                        | laenge
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx                    |
   schraublaenge |         |    .    |                        |
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx                    |
                 |         |    .    |                        |
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx                    |
                 |         |    .    |                        |
                 |     xxxx|    .    |                        |
                 |         |    .    |xxxx _____|_            |
                 |         |    .    |          |             |
                 |     xxxx|    .    |          | ganghoehe   |
                _|_______  |    .    |xxxx _|___|_____________|_
                 |          \   .   /       |   |             |
                        --.  \  .  /        | 
                rundwinkel \  \ . /         | spitzenlaenge = r_innen*tan(grad2rad*spitzenwinkel)
                            |  \./  ________|_
                                '           |
   
   Zusaetzlich muss gelten: 0 <= spitzenwinkel < 90 und 0 <= rundwinkel <= 90 - 2*|45-spitzenwinkel|
   """
   import part
   import assembly
   from abaqusConstants import GEOMETRY, DELETE, ON
   from erstellung import NamePartInstance
   #
   nameSeele = NamePartInstance(modell=modell, namensvorschlag='Seele');
   nameinstSeele = 'inst' + nameSeele;
   # Seele erzeugen
   _Bohrprofil_stange(modell=modell, name=nameSeele, laenge=laenge, r_aussen=r_innen,
      spitzenwinkel=spitzenwinkel, rundwinkel=rundwinkel);
   # Fuer jedes 10fache von Ganghoehe mehrere Segmente erstellen und zusammensetzen,
   # da die maximale Verdrehung ab dem 10fachen zu Problemen fuehren scheint
   schraubeninfos = [int(schraublaenge/ganghoehe/10.0 + 1.0), (schraublaenge/ganghoehe)%10.0];
   #
   nameWendel = NamePartInstance(modell=modell, namensvorschlag='Wendel');
   nameinstWendel = 'inst' + nameWendel;
   _Bohrprofil_wendelstueck(modell=modell, name=nameWendel, r_aussen=r_aussen, r_innen=r_innen,
      ganghoehe=ganghoehe, wendeldicke=wendeldicke, hoehe=schraubeninfos[1]*ganghoehe);
   #
   if (schraubeninfos[0] >= 2):
      nameWendelZehn = NamePartInstance(modell=modell, namensvorschlag='Wendel10');
      nameinstWendelZehn = 'inst' + nameWendelZehn;
      _Bohrprofil_wendelstueck(modell=modell, name=nameWendelZehn, r_aussen=r_aussen,
         r_innen=r_innen, ganghoehe=ganghoehe, wendeldicke=wendeldicke, hoehe=10.0*ganghoehe);
      #
      # Wendel zusammenstecken
      wendelinstances = ();
      schraubenteile = int(schraubeninfos[0]);
      for wendelnummer in range(0, schraubenteile):
         wendelpartname = nameWendelZehn;
         wendelinstname = 'inst' + nameWendel + str(wendelnummer);
         if (wendelnummer == schraubenteile-1):
            wendelpartname = nameWendel;
         #
         modell.rootAssembly.Instance(dependent=ON,
            name=wendelinstname, part=modell.parts[wendelpartname]);
         modell.rootAssembly.rotate(angle=-90.0, axisDirection=(-1.0, 0.0, 0.0),
            axisPoint=(1.0, 0.0, 0.0), instanceList=(wendelinstname, ));
         if (wendelnummer == schraubenteile-1):
            modell.rootAssembly.translate(instanceList=(wendelinstname, ),
               vector=(0.0, 0.0, wendeldicke + wendelnummer * 10 * ganghoehe + schraubeninfos[1]*ganghoehe));
            modell.rootAssembly.rotate(axisDirection=(0.0, 0.0, 1.0), axisPoint=(0.0, 0.0, 1.0),
               angle=(360.0*schraubeninfos[1])%360.0, instanceList=(wendelinstname, ));
         else:
            modell.rootAssembly.translate(instanceList=(wendelinstname, ),
               vector=(0.0, 0.0, wendeldicke + (wendelnummer+1) * 10.0 * ganghoehe));
         #
         wendelinstances = wendelinstances + (modell.rootAssembly.instances[wendelinstname],);
      #
      nameGanzeWendel = NamePartInstance(modell=modell, namensvorschlag='GanzeWendel');
      modell.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=wendelinstances, 
         name=nameGanzeWendel, originalInstances=DELETE);
      nameabqinstGanzeWendel = nameGanzeWendel + '-1';
      nameinstGanzeWendel = 'inst' + nameGanzeWendel;
      modell.rootAssembly.features.changeKey(fromName=nameabqinstGanzeWendel,
         toName=nameinstGanzeWendel);
      del modell.parts[nameWendel];
      del modell.parts[nameWendelZehn];
   else:
      nameGanzeWendel = nameWendel;
      nameinstGanzeWendel = nameinstWendel;
      modell.rootAssembly.Instance(dependent=ON, name=nameinstGanzeWendel,
         part=modell.parts[nameGanzeWendel]);
      modell.rootAssembly.rotate(angle=-90.0, axisDirection=(-1.0, 0.0, 0.0),
         axisPoint=(1.0, 0.0, 0.0), instanceList=(nameinstGanzeWendel, ));
      modell.rootAssembly.translate(instanceList=(nameinstGanzeWendel, ),
         vector=(0.0, 0.0, wendeldicke + schraubeninfos[1]*ganghoehe));
      modell.rootAssembly.rotate(angle=(360.0*schraubeninfos[1])%360.0, axisDirection=(0.0, 0.0, 1.0),
         axisPoint=(0.0, 0.0, 1.0), instanceList=(nameinstGanzeWendel, ));
   #
   # Bohrwerkzeuge anfertigen
   modell.rootAssembly.Instance(dependent=ON, name=nameinstSeele, part=modell.parts[nameSeele]);
   modell.rootAssembly.rotate(angle=90.0, axisDirection=(1.0, 0.0, 0.0), axisPoint=(0.0, 0.0, 0.0),
      instanceList=(nameinstSeele, ));
   modell.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(
      modell.rootAssembly.instances[nameinstSeele], 
      modell.rootAssembly.instances[nameinstGanzeWendel]), 
      keepIntersections=ON, name=name, originalInstances=DELETE);
   nameabqinstFinal = name + '-1';
   nameinstFinal = 'inst' + name;
   modell.rootAssembly.features.changeKey(fromName=nameabqinstFinal, toName=nameinstFinal);
   # Aufraeumen
   del modell.parts[nameSeele];
   del modell.parts[nameGanzeWendel];
   del modell.rootAssembly.features[nameinstFinal];
   #
   partWerkzeug = modell.parts[name];
   if (schraublaenge < laenge):
      partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, schraublaenge+wendeldicke));
      partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Gewindeende');
   #
   partWerkzeug.ReferencePoint(point=(0.0, 0.0, laenge));
   # Beim Partitionieren die Wendel so abtrennen, dass der Abstand zur Seele
   # hoechstens gitter_werkzeug betraegt
   if ((r_aussen-r_innen)/2.0 > min(gitter_werkzeug, wendeldicke)):
      r_m = r_innen + min(gitter_werkzeug, wendeldicke);
   else:
      r_m = (r_aussen+r_innen)/2.0;
   #
   _Bohrprofil_partitionieren(modell=modell, name=name, spitzenwinkel=spitzenwinkel,
      partitionsradius=r_m);
   _Bohrprofil_vernetzen(modell=modell, name=name, gitter=gitter_werkzeug);
   instWerkzeug = _Bohrprofil_positionieren(modell=modell, name=name, typ='SOBP', radius=r_innen,
      spitzenwinkel=spitzenwinkel);
   return [partWerkzeug, instWerkzeug];
#


# -------------------------------------------------------------------------------------------------
def Bohrprofil_VBP(modell, name, laenge, r_aussen, spitzenwinkel, rundwinkel, gitter_werkzeug):
   """Erstelle ein Vollverdraengungsprofil name im Modell modell aus den in der folgenden Skizze
   dargestellten Parametern. Die fehlende Groesse gitter_werkzeug gibt die Gitterfeinheit bei der
   Vernetzung des Modells an. Gibt [part<name>, inst<name>] zurueck.

   ===========  r_aussen r_aussen
   =  V B P  =    _|____|____|_
   ===========     |    |    |
                                ___________|_
                   +----+----+             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             | laenge
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |             |
                   |    .    |  _|_________|_
                    \   .   /    |         |
                --.  \  .  /     | 
        rundwinkel \  \ . /      | spitzenlaenge = r_aussen*tan(grad2rad*spitzenwinkel)
                    |  \./  _____|_
                        '        |
   
   Zusaetzlich muss gelten: 0 <= spitzenwinkel < 90 und 0 <= rundwinkel <= 90 - 2*|45-spitzenwinkel|
   """
   import part
   #
   _Bohrprofil_stange(modell=modell, name=name, laenge=laenge, r_aussen=r_aussen,
      spitzenwinkel=spitzenwinkel, rundwinkel=rundwinkel);
   #
   partWerkzeug = modell.parts[name];
   partWerkzeug.ReferencePoint(point=(0.0, laenge, 0.0));
   #
   _Bohrprofil_partitionieren(modell=modell, name=name, spitzenwinkel=spitzenwinkel);
   _Bohrprofil_vernetzen(modell=modell, name=name, gitter=gitter_werkzeug);
   instWerkzeug = _Bohrprofil_positionieren(modell=modell, name=name, typ='VBP', radius=r_aussen,
      spitzenwinkel=spitzenwinkel);
   return [partWerkzeug, instWerkzeug];
#


# -------------------------------------------------------------------------------------------------
def _Rundwinkel_geometrie(zeichnung, spitzenlaenge, r_aussen, spitzenwinkel, rundwinkel):
   """Erstelle in der uebergebenen zeichnung die Verbindung zwischen der Spitze eines Bohrprofils
   (mit der Laenge spitzenlaenge) und dem Aussenradius (r_aussen) abhaengig vom gewaehlten
   spitzenwinkel und rundwinkel.
   """
   import sketch
   from abaqusConstants import CLOCKWISE
   from math import tan
   from hilfen import grad2rad, Log
   from zeichnung import Linie, KreisbogenPunkte
   #
   if ((rundwinkel >= 90.0) or (rundwinkel < 0.0)):
      Log('# Ungueltiger Wert fuer Rundwinkel (0 <= winkel < 90) - setze zu Null');
      rundwinkel = 0.0;
   #
   # Ziehe zusaetzlich 1 Grad vom Maximalwert ab, damit ein gueltiges Mesh entstehen kann
   # (der Winkel darf aber nicht kleiner als 0 sein).
   max_rundwinkel = 90.0 - 2.0*abs(45.0-spitzenwinkel) - 1.0;
   if (max_rundwinkel <= 0.0):
      Log('# max. Rundwinkel ist 0.0');
      rundwinkel = 0.0;
   #
   if (rundwinkel == 0.0):
      Linie(zeichnung=zeichnung, punkt1=(0.0, -spitzenlaenge), punkt2=(r_aussen, 0.0));
   else:
      if (rundwinkel >= max_rundwinkel):
         Log('# Rundwinkel zu gross - setze auf ' + str(max_rundwinkel));
         rundwinkel = max_rundwinkel;
      #
      rundungsfaktor = 0.5/tan(0.5*rundwinkel*grad2rad);
      KreisbogenPunkte(zeichnung=zeichnung, punkt1=(0.0, -spitzenlaenge), punkt2=(r_aussen, 0.0),
         mittelpunkt=(0.5*r_aussen + rundungsfaktor*spitzenlaenge,
                     -0.5*spitzenlaenge - rundungsfaktor*r_aussen), richtung=CLOCKWISE);
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_stange(modell, name, laenge, r_aussen, spitzenwinkel, rundwinkel):
   """Erstelle ein Stange mit der Bezeichnung name fuer Schraubprofil und Vollverdraengungsprofil.
   im modell mit den Parametern vom Vollverdraengungsprofil.
   """
   import sketch
   import part
   from abaqusConstants import THREE_D, DEFORMABLE_BODY, OFF
   from zeichnung import Linienzug
   #
   spitzenlaenge = _Bohrprofil_spitzenlaenge(breite=r_aussen, winkel=spitzenwinkel);
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=2.0*laenge);
   zeichnung = modell.sketches['__profile__'];
   zeichnung.ConstructionLine(point1=(0.0, -laenge), point2=(0.0, laenge));
   zeichnung.FixedConstraint(entity=zeichnung.geometry.findAt((0.0, 0.0), ));
   #
   _Rundwinkel_geometrie(zeichnung=zeichnung, spitzenlaenge=spitzenlaenge, r_aussen=r_aussen,
      spitzenwinkel=spitzenwinkel, rundwinkel=rundwinkel);
   #
   Linienzug(zeichnung=zeichnung, punkte=[
      (r_aussen, 0.0),
      (r_aussen, laenge),
      (0.0, laenge),
      (0.0, -spitzenlaenge)], geschlossen=False);
   modell.Part(dimensionality=THREE_D, name=name, type=DEFORMABLE_BODY);
   modell.parts[name].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=zeichnung);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_vvbpstange(modell, name, laenge, r_aussen, r_innen, spitzenwinkel, rundwinkel,
   schraublaenge1, profillaenge1, schraublaenge2, profillaenge2, laenge12):
   """Erstelle ein speziell geformte Stange mit der Bezeichnung name mit aufgeweitetem
   Verdraengungsbereich im modell mit den Parametern vom Vollverdraengungsbohrprofil.
   """
   import sketch
   import part
   from abaqusConstants import THREE_D, DEFORMABLE_BODY, OFF
   from zeichnung import Linienzug
   #
   spitzenlaenge = _Bohrprofil_spitzenlaenge(breite=r_innen, winkel=spitzenwinkel);
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=2.0*laenge);
   zeichnung = modell.sketches['__profile__'];
   zeichnung.ConstructionLine(point1=(0.0, -laenge), point2=(0.0, laenge));
   zeichnung.FixedConstraint(entity=zeichnung.geometry.findAt((0.0, 0.0), ));
   #
   _Rundwinkel_geometrie(zeichnung=zeichnung, spitzenlaenge=spitzenlaenge, r_aussen=r_aussen,
      spitzenwinkel=spitzenwinkel, rundwinkel=rundwinkel);
   #
   Linienzug(zeichnung=zeichnung, punkte=[
      (r_innen, 0.0),
      (r_innen, schraublaenge1-profillaenge1),
      (r_aussen, schraublaenge1),
      (r_aussen, schraublaenge1+laenge12),
      (r_innen, schraublaenge1+laenge12+profillaenge2),
      (r_innen, laenge),
      (0.0, laenge),
      (0.0, -spitzenlaenge)], geschlossen=False);
   modell.Part(dimensionality=THREE_D, name=name, type=DEFORMABLE_BODY);
   modell.parts[name].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF,
      sketch=zeichnung);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_wendelstueck(modell, name, r_aussen, r_innen, ganghoehe, wendeldicke, hoehe):
   """Erstelle ein Wendelstueck name zum uebergebenen modell aus den in der Skizze
   dargestellten Werten.
   
                     r_aussen  r_innen
                    _|________|____|_
                     |        |    |
                     |                ________|_
               _|___     +----+----+          |
   wendeldicke _|___ xxxx|    .    |          |
                |        |    .    |xxxx      |
      ganghoehe |        |    .    |          | hoehe
               _|___ xxxx|    .    |          |
                |        +----+----+xxxx _____|_
                                              |
   """
   import sketch
   import part
   from abaqusConstants import THREE_D, DEFORMABLE_BODY, ON, OFF
   from zeichnung import Rechteck
   #
   flipPitch=OFF;
   if (ganghoehe < 0.0):
      ganghoehe = -ganghoehe;
      flipPitch=ON;
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=2.0*r_aussen);
   zeichnung = modell.sketches['__profile__'];
   zeichnung.ConstructionLine(point1=(0.0, 0.0), point2=(0.0, 1.0));
   zeichnung.FixedConstraint(entity=zeichnung.geometry.findAt((0.0, 0.0),));
   Rechteck(zeichnung=zeichnung, punkt1=(r_innen, 0.0), punkt2=(r_aussen, -wendeldicke));
   modell.Part(dimensionality=THREE_D, name=name, type=DEFORMABLE_BODY);
   modell.parts[name].BaseSolidRevolve(angle=360.0*hoehe/ganghoehe, pitch=ganghoehe, sketch=zeichnung,
      flipPitchDirection=flipPitch, flipRevolveDirection=OFF, moveSketchNormalToPath=OFF);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_spitzenlaenge(breite, winkel):
   """Berechne die Laenge einer Bohrspitze bei gegebener breite (Radius) und winkel der Spitze.
   Gibt die berechnete Laenge zurueck.
   """
   from math import tan
   from hilfen import grad2rad, Log
   #
   tempwinkel = winkel;
   if ((winkel >= 90.0) or (winkel < 0.0)):
      Log('# Ungueltiger Wert fuer Spitzenwinkel (0 <= winkel < 90) - setze zu Null');
      tempwinkel = 0.0;
   #
   return breite*tan(tempwinkel*grad2rad);
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_partitionieren(modell, name, spitzenwinkel, partitionsradius=None):
   """Erstelle Datums und Partitionen eines Bohrprofils am Bauteil (Part) name
   im modell mit dem uebergebenem spitzenwinkel.
   Optional kann das Gewinde bei einem uebergebenem partitionsradius partitioniert werden.
   """
   import sketch
   import part
   from abaqusConstants import XAXIS, YAXIS, ZAXIS, XYPLANE, COPLANAR_EDGES, SIDE2, RIGHT
   from auswahl import BedingteAuswahl
   from zeichnung import Kreis
   #
   partWerkzeug = modell.parts[name];
   # Datums
   partWerkzeug.DatumAxisByPrincipalAxis(principalAxis=XAXIS);
   partWerkzeug.features.changeKey(fromName='Datum axis-1', toName='xAchse');
   xachsenid = partWerkzeug.features['xAchse'].id;
   partWerkzeug.DatumAxisByPrincipalAxis(principalAxis=YAXIS);
   partWerkzeug.features.changeKey(fromName='Datum axis-1', toName='yAchse');
   yachsenid = partWerkzeug.features['yAchse'].id;
   partWerkzeug.DatumAxisByPrincipalAxis(principalAxis=ZAXIS);
   partWerkzeug.features.changeKey(fromName='Datum axis-1', toName='zAchse');
   zachsenid = partWerkzeug.features['zAchse'].id;
   #
   partWerkzeug.DatumPointByCoordinate(coords=(0.0, 0.0, 0.0));
   partWerkzeug.features.changeKey(fromName='Datum pt-1', toName='datum_Spitzenaufsatz');
   datumbeginnid = partWerkzeug.features['datum_Spitzenaufsatz'].id;
   # Partitionen
   if (partWerkzeug.features.has_key('datum_Gewindeende')):
      # Pfahltyp SOBP
      if (spitzenwinkel > 0.0):
         partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
            normal=partWerkzeug.datums[zachsenid],
            point=partWerkzeug.datums[datumbeginnid]);
      datumendeid = partWerkzeug.features['datum_Gewindeende'].id;
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumendeid]);
      # Zellen vor und nach Gewinde (falls existent)
      zellenOhneGewindebereich = BedingteAuswahl(elemente=partWerkzeug.cells,
         bedingung='(elem.pointOn[0][2] > var[0]) or (elem.pointOn[0][2] < var[1])',
         var=[partWerkzeug.features['datum_Gewindeende'].zValue,
              partWerkzeug.features['datum_Spitzenaufsatz'].zValue]);
      if (not zellenOhneGewindebereich == ()):
         partWerkzeug.PartitionCellByPlanePointNormal(cells=zellenOhneGewindebereich,
            normal=partWerkzeug.datums[xachsenid],
            point=partWerkzeug.datums[datumbeginnid]);
         zellenOhneGewindebereich = BedingteAuswahl(elemente=partWerkzeug.cells,
            bedingung='(elem.pointOn[0][2] > var[0]) or (elem.pointOn[0][2] < var[1])',
            var=[partWerkzeug.features['datum_Gewindeende'].zValue,
                 partWerkzeug.features['datum_Spitzenaufsatz'].zValue]);
         partWerkzeug.PartitionCellByPlanePointNormal(cells=zellenOhneGewindebereich,
            normal=partWerkzeug.datums[yachsenid],
            point=partWerkzeug.datums[datumbeginnid]);
      if ((not partWerkzeug.features.has_key('datum_Gewindeendea')) and
          (not (partitionsradius is None))):
         # SOBP
         # Zellen auf dem Gewinde abtrennen
         partWerkzeug.DatumPlaneByPrincipalPlane(offset=0.0, principalPlane=XYPLANE);
         partWerkzeug.features.changeKey(fromName='Datum plane-1', toName='XYEbene');
         xyebeneid = partWerkzeug.features['XYEbene'].id;
         modell.ConstrainedSketch(gridSpacing=0.01, name='__profile__', sheetSize=0.6,
            transform=partWerkzeug.MakeSketchTransform(
               sketchPlane=partWerkzeug.datums[xyebeneid], 
               sketchPlaneSide=SIDE2, 
               sketchUpEdge=partWerkzeug.datums[yachsenid],
               sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)));
         zeichnung = modell.sketches['__profile__'];
         partWerkzeug.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=zeichnung);
         Kreis(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=partitionsradius);
         partWerkzeug.PartitionFaceBySketchThruAll(faces=partWerkzeug.faces, sketch=zeichnung,
            sketchPlane=partWerkzeug.datums[xyebeneid], sketchPlaneSide=SIDE2,
            sketchUpEdge=partWerkzeug.datums[yachsenid]);
         del zeichnung;
   else:
      # Alle Pfahltypen ausser SOBP und VVBP
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[xachsenid],
         point=partWerkzeug.datums[datumbeginnid]);
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumbeginnid]);
      if (spitzenwinkel > 0.0):
         partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
            normal=partWerkzeug.datums[yachsenid],
            point=partWerkzeug.datums[datumbeginnid]);
   # VVBP mit Vorlaufgewinde
   if (partWerkzeug.features.has_key('datum_Gewindeendea')):
      datumendeid = partWerkzeug.features['datum_Gewindeendea'].id;
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumendeid]);
   # VVBP mit Ruecklaufgewinde
   if (partWerkzeug.features.has_key('datum_Gewindeendeb')):
      datumendeid = partWerkzeug.features['datum_Gewindeendeb'].id;
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumendeid]);
   # VVBP mit Anfang Verdickung
   if (partWerkzeug.features.has_key('datum_Profilendea')):
      datumendeid = partWerkzeug.features['datum_Profilendea'].id;
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumendeid]);
   # VVBP mit Ende Verdickung
   if (partWerkzeug.features.has_key('datum_Profilendeb')):
      datumendeid = partWerkzeug.features['datum_Profilendeb'].id;
      partWerkzeug.PartitionCellByPlanePointNormal(cells=partWerkzeug.cells,
         normal=partWerkzeug.datums[zachsenid],
         point=partWerkzeug.datums[datumendeid]);
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_vernetzen(modell, name, gitter):
   """Erzeuge ein Netz fuer das Bauteil (Part) name im modell mit der Netzfeinheit gitter.
   """
   import part
   import mesh
   from abaqusConstants import UNKNOWN_HEX, UNKNOWN_WEDGE, EXPLICIT, C3D10M, TET, FREE, OFF, DEFAULT
   from hilfen import Log
   #
   partWerkzeug = modell.parts[name];
   # Sets
   partWerkzeug.Set(name='setAll', cells=partWerkzeug.cells);
   partWerkzeug.Set(name='setRP', referencePoints=(
      partWerkzeug.referencePoints[partWerkzeug.features['RP'].id], ));
   # Elementtypen anpassen
   partWerkzeug.setElementType(elemTypes=(
      mesh.ElemType(elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT),
      mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT),
      mesh.ElemType(elemCode=C3D10M, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, distortionControl=DEFAULT)), 
      regions=partWerkzeug.sets['setAll']);
   # Mesh
   partWerkzeug.setMeshControls(elemShape=TET, regions=partWerkzeug.cells, technique=FREE);
   partWerkzeug.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=gitter);
   partWerkzeug.generateMesh();
   if (len(partWerkzeug.elements) == 0 ):
      Log('Warnung: Mesh-Erstellung zu ' + name + ' fehlgeschlagen');
#


# -------------------------------------------------------------------------------------------------
def _Bohrprofil_positionieren(modell, name, typ, radius, spitzenwinkel):
   """Positioniere das Profil name im Modell modell mit der Spitze (radius und spitzenwinkel) ueber
   dem Ursprung. Gibt inst<name> zurueck.
   """
   import assembly
   from abaqusConstants import ON
   #
   instname = 'inst' + name;
   modell.rootAssembly.Instance(dependent=ON, name=instname, part=modell.parts[name]);
   if (typ == 'VBP'):
      modell.rootAssembly.rotate(angle=-90.0, axisDirection=(-1.0, 0.0, 0.0),
         axisPoint=(1.0, 0.0, 0.0), instanceList=(instname, ));
   spitzenlaenge = _Bohrprofil_spitzenlaenge(breite=radius, winkel=spitzenwinkel);
   modell.rootAssembly.translate(instanceList=(instname, ), vector=(0.0, 0.0, spitzenlaenge));
   return modell.rootAssembly.instances[instname];
#
