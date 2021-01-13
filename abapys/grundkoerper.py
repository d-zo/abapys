# -*- coding: utf-8 -*-
"""
grundkoerper.py   v1.3 (2020-02)
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
def Quader(modell, name, laenge, breite, hoehe, materialtyp, gittergroesse, rp=False,
   extrasets=False, xypartition=[True, True], viertel=4):
   """Erzeuge einen Quader name im modell mit den Abmessungen laenge, breite und hoehe vom Typ
   materialtyp (Abaqus-Konstante, bspw. DEFORMABLE_BODY) und der Netzgroesse gittergroesse
   (Zahlenwert oder [gitter_x, gitter_y, gitter_z]). laenge und breite koennen entweder als
   Zahlenwert für eine symmetrische Anordnung um den Ursprung (wird transformiert zu
   [-zahl/2.0, zahl/2.0]) oder direkt als (startpunkt, endpunkt) uebergeben werden. Optional kann
   ein Referenzpunkt rp oder extrasets erstellt werden. Wenn gewuenscht, kann mit xypartition die
   Erzeugung der Standardpartitionen in x- oder y-Richtung unterdrueckt werden.
   
   Neben einem Quader mit den Werten in laenge und breite kann ueber viertel auch ein (Teil-)Quader
   erzeugt werden (nur die Werte 1, 2 und 4 werden unterstuetzt). In dem Fall werden Partitionen in
   der Schnittebene nicht erzeugt (unabhaengig von den Angaben in xypartition).
   Gibt [part<name>, inst<name>] zurueck.
   """
   import assembly
   from abaqusConstants import ON
   #
   laenge, breite = _Quader_Einheitliche_Geometrieangaben(laenge=laenge, breite=breite);
   xPartition, yPartition = xypartition;
   if   (viertel == 1):
      laenge[0] = (laenge[0]+laenge[1])/2.0;
      breite[0] = (breite[0]+breite[1])/2.0;
      xPartition = False;
      yPartition = False;
   elif (viertel == 2):
      laenge[0] = (laenge[0]+laenge[1])/2.0;
      xPartition = False;
   #
   if ((laenge[0] > 0.0) or (laenge[1] < 0.0)):
      xPartition = False;
   #
   if ((breite[0] > 0.0) or (breite[1] < 0.0)):
      yPartition = False;
   #
   Quader_erstellen(modell=modell, name=name, laenge=laenge, breite=breite, hoehe=hoehe,
      materialtyp=materialtyp);
   Grundkoerper_standardpartitionen(modell=modell, name=name,
      xPartition=xPartition, yPartition=yPartition, zPartition=False, rp=rp);
   Grundkoerper_sets(modell=modell, name=name);
   if (extrasets):
      Quader_flaechensets(modell=modell, name=name, laenge=laenge, breite=breite, hoehe=hoehe);
   #
   Grundkoerper_vernetzen(modell=modell, name=name, materialtyp=materialtyp,
      gittergroesse=gittergroesse);
   #
   instname = 'inst' + name;
   modell.rootAssembly.Instance(dependent=ON, name=instname, part=modell.parts[name]);
   return [modell.parts[name], modell.rootAssembly.instances[instname]];
#


# -------------------------------------------------------------------------------------------------
def Quader_erstellen(modell, name, laenge, breite, hoehe, materialtyp):
   """Erzeuge ein quaderfoermiges Bauteil (Part) name im modell mit den Abmessungen laenge, breite
   und hoehe vom Typ materialtyp (Abaqus-Konstante, bspw. DEFORMABLE_BODY). 
   """
   import sketch
   import part
   from abaqusConstants import THREE_D
   from zeichnung import Rechteck
   #
   laenge, breite = _Quader_Einheitliche_Geometrieangaben(laenge=laenge, breite=breite);
   zeichengroesse = 2.0*max([abs(val) for val in laenge + breite]);
   modell.ConstrainedSketch(name='__profile__', sheetSize=zeichengroesse);
   zeichnung = modell.sketches['__profile__'];
   Rechteck(zeichnung=zeichnung, punkt1=(laenge[0], breite[0]), punkt2=(laenge[1], breite[1]));
   modell.Part(dimensionality=THREE_D, name=name, type=materialtyp);
   modell.parts[name].BaseSolidExtrude(depth=hoehe, sketch=zeichnung);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def Quader_flaechensets(modell, name, laenge, breite, hoehe):
   """Erzeuge Flaechensets an der Oberseite, Unterseite und allen Seiten des Quaderbauteils (Part)
   name im modell. Zur richtigen Zuordnung werden die Abmessungen laenge, breite und hoehe des
   Quaders benoetigt. laenge und breite koennen entweder als Zahlenwert für eine symmetrische
   Anordnung um den Ursprung (-zahl/2.0, zahl/2.0) oder direkt als (startpunkt, endpunkt) uebergeben
   werden. Die hoehe wird als Zahlenwert erwartet und immer von Null an gestartet.
   """
   import part
   from auswahl import BedingteAuswahl
   from hilfen import abapys_tol
   #
   laenge, breite = _Quader_Einheitliche_Geometrieangaben(laenge=laenge, breite=breite);
   partQuader = modell.parts[name];
   #
   flaechen_Unterseite = BedingteAuswahl(elemente=partQuader.faces,
      bedingung='elem.pointOn[0][2] < var[0]', var=[abapys_tol]);
   partQuader.Set(name='setUnterseite', faces=flaechen_Unterseite);
   flaechen_Oberseite = BedingteAuswahl(elemente=partQuader.faces,
      bedingung='elem.pointOn[0][2] > var[0]-var[1]', var=[hoehe, abapys_tol]);
   partQuader.Set(name='setOberseite', faces=flaechen_Oberseite);
   #
   flaechen_X = BedingteAuswahl(elemente=partQuader.faces,
      bedingung='((elem.pointOn[0][0] < var[0]+var[2]) or (elem.pointOn[0][0] > var[1]-var[2]))',
      var=[laenge[0], laenge[1], abapys_tol]);
   partQuader.Set(name='setXFlaeche', faces=flaechen_X);
   flaechen_Y = BedingteAuswahl(elemente=partQuader.faces,
      bedingung='((elem.pointOn[0][1] < var[0]+var[2]) or (elem.pointOn[0][1] > var[1]-var[2]))',
      var=[breite[0], breite[1], abapys_tol]);
   partQuader.Set(name='setYFlaeche', faces=flaechen_Y);
#


# -------------------------------------------------------------------------------------------------
def _Quader_Einheitliche_Geometrieangaben(laenge, breite):
   """
   laenge und breite koennen entweder als Zahlenwert für eine symmetrische Anordnung um den Ursprung
   (-zahl/2.0, zahl/2.0) oder als (startpunkt, endpunkt) verwendet werden. Diese Funktion stellt
   sicher, dass alle Zahlenwerte in Listen mit zwei Einträgen umgewandelt werden.
   Gibt [[laenge_start, laenge_ende], [breite_start, breite_ende]] zurueck, sofern laenge und breite
   zu Beginn entweder ein Zahlenwert oder [start, ende] waren.
   """
   if (not type(laenge) is list):
      laenge = [-laenge/2.0, laenge/2.0];
   #
   if (not type(breite) is list):
      breite = [-breite/2.0, breite/2.0];
   #
   return [laenge, breite];
#


# -------------------------------------------------------------------------------------------------
def Zylinder(modell, name, radius, hoehe, materialtyp, gittergroesse, rp=False, extrasets=False,
   r_innen=[], xypartition=[True, True], viertel=4):
   """Erzeuge einen Zylinder name im modell mit den Abmessungen radius und hoehe vom Typ materialtyp
   (Abaqus-Konstante, bspw. DEFORMABLE_BODY) und der Netzgroesse gittergroesse (Zahlenwert oder
   [gitter_r, gitter_h]). Optional kann ein Referenzpunkt rp oder extrasets erstellt werden.
   Optional kann ausserdem statt einem Zylinder ein Zylinderring erzeugt werden, wenn r_innen
   gegeben ist.
   
   Neben einem Zylinder(ring) kann auch nur ein Viertel- oder Halbzylinder(ring) ueber viertel
   erzeugt werden (nur die Werte 1, 2 und 4 werden unterstuetzt). Falls nur ein halber/viertel
   Zylinder erzeugt wird, werden Partitionen in der Schnittebene nicht erzeugt (unabhaengig von den
   Angaben in xypartition). Gibt [part<name>, inst<name>] zurueck.
   """
   from abaqusConstants import ON
   import assembly
   #
   xPartition, yPartition = xypartition;
   if   (viertel == 1):
      xPartition = False;
      yPartition = False;
   elif (viertel == 2):
      xPartition = False;
   #
   Zylinder_erstellen(modell=modell, name=name, radius=radius, hoehe=hoehe,
      materialtyp=materialtyp, r_innen=r_innen, viertel=viertel);
   Grundkoerper_standardpartitionen(modell=modell, name=name,
      xPartition=xPartition, yPartition=yPartition, zPartition=False, rp=rp);
   Grundkoerper_sets(modell=modell, name=name);
   if (extrasets):
      Zylinder_flaechensets(modell=modell, name=name, radius=radius, hoehe=hoehe,
         r_innen=r_innen, viertel=viertel);
   Grundkoerper_vernetzen(modell=modell, name=name, materialtyp=materialtyp,
      gittergroesse=gittergroesse);
   #
   instname = 'inst' + name;
   modell.rootAssembly.Instance(dependent=ON, name=instname, part=modell.parts[name]);
   return [modell.parts[name], modell.rootAssembly.instances[instname]];
#


# -------------------------------------------------------------------------------------------------
def Zylinder_erstellen(modell, name, radius, hoehe, materialtyp, r_innen=[], viertel=4):
   """Erzeuge ein zylindrisches Bauteil (Part) name im modell mit den Abmessungen radius und hoehe
   vom Typ materialtyp (Abaqus-Konstante, bspw. DEFORMABLE_BODY). Falls r_innen gegeben ist, wird
   statt einem Zylinder ein Zylinderring mit dem Aussparungsradius r_innen erzeugt.
   
   Neben einem Zylinder(ring) kann auch nur ein Viertel- oder Halbzylinder(ring) ueber viertel
   erzeugt werden. Fuer viertel werden nur die Werte 1,2 und 4 unterstuetzt.
   """
   import sketch
   import part
   from abaqusConstants import CLOCKWISE, THREE_D
   from zeichnung import Kreis, Linie, KreisbogenWinkel
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=4.0*radius);
   zeichnung = modell.sketches['__profile__'];
   if   (viertel == 1):
      hilfspunkt = 0.0;
      if (not (r_innen == [])):
         hilfspunkt = r_innen;
         KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=r_innen,
            startwinkel=0.0, endwinkel=90.0, richtung=CLOCKWISE);
      #
      Linie(zeichnung=zeichnung, punkt1=(radius, 0.0), punkt2=(hilfspunkt, 0.0));
      Linie(zeichnung=zeichnung, punkt1=(0.0, hilfspunkt), punkt2=(0.0, radius));
      KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=radius,
         startwinkel=0.0, endwinkel=90.0, richtung=CLOCKWISE);
   elif (viertel == 2):
      hilfspunkt = -radius;
      if (not (r_innen == [])):
         hilfspunkt = r_innen;
         KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=r_innen,
            startwinkel=0.0, endwinkel=180.0, richtung=CLOCKWISE);
         Linie(zeichnung=zeichnung, punkt1=(0.0, -radius), punkt2=(0.0, -r_innen));
      #
      Linie(zeichnung=zeichnung, punkt1=(0.0, hilfspunkt), punkt2=(0.0, radius));
      KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=radius,
         startwinkel=0.0, endwinkel=180.0, richtung=CLOCKWISE);
   else:
      Kreis(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=radius);
      if (not (r_innen == [])):
         Kreis(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=r_innen);
   #
   modell.Part(dimensionality=THREE_D, name=name, type=materialtyp);
   modell.parts[name].BaseSolidExtrude(depth=hoehe, sketch=zeichnung);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def Zylinder_flaechensets(modell, name, radius, hoehe, r_innen=[], viertel=4):
   """Erzeuge Flaechensets an der Oberseite, Unterseite und Mantel des Zylinderbauteils (Part) name
   im modell. Zur richtigen Zuordnung werden radius und hoehe des Zylinders benoetigt. Falls nur ein
   Viertel-/Halbzylinder erzeugt werden soll, werden zusaetzliche Sets erstellt.
   """
   import part
   from auswahl import BedingteAuswahl
   from hilfen import abapys_tol
   #
   partZylinder = modell.parts[name];
   #
   flaechen_Unterseite = BedingteAuswahl(elemente=partZylinder.faces,
      bedingung='elem.pointOn[0][2] < var[0]', var=[abapys_tol]);
   partZylinder.Set(name='setUnterseite', faces=flaechen_Unterseite);
   flaechen_Oberseite = BedingteAuswahl(elemente=partZylinder.faces,
      bedingung='elem.pointOn[0][2] > var[0]-var[1]', var=[hoehe, abapys_tol]);
   partZylinder.Set(name='setOberseite', faces=flaechen_Oberseite);
   #
   flaechen_Mantel = BedingteAuswahl(elemente=partZylinder.faces,
      bedingung='sqrt(elem.pointOn[0][0]**2 + elem.pointOn[0][1]**2) > var[0]-var[1]',
      var=[radius, abapys_tol]);
   partZylinder.Set(name='setMantelflaeche', faces=flaechen_Mantel);
   if ((viertel == 1) or (viertel == 2)):
      if (viertel == 1):
         flaechen_Y = BedingteAuswahl(elemente=partZylinder.faces,
            bedingung='(elem.pointOn[0][1] < var[0])', var=[abapys_tol]);
         partZylinder.Set(name='setYFlaeche', faces=flaechen_Y);
      #
      flaechen_X = BedingteAuswahl(elemente=partZylinder.faces,
         bedingung='(elem.pointOn[0][0] < var[0])', var=[abapys_tol]);
      partZylinder.Set(name='setXFlaeche', faces=flaechen_X);
   #
   if (not r_innen == []):
      flaechen_Mantelinnen = BedingteAuswahl(elemente=partZylinder.faces,
         bedingung='sqrt(elem.pointOn[0][0]**2 + elem.pointOn[0][1]**2) < var[0]+var[1]',
         var=[r_innen, abapys_tol]);
      partZylinder.Set(name='setMantelinnen', faces=flaechen_Mantelinnen);
#


# -------------------------------------------------------------------------------------------------
def Kugel(modell, name, radius, materialtyp, gittergroesse, rp=False, extrasets=False, r_innen=[]):
   """Erzeuge eine Kugel name im modell mit dem uebergebenem radius vom Typ materialtyp
   (Abaqus-Konstante, bspw. DEFORMABLE_BODY) und der Netzgroesse gittergroesse (Zahlenwert).
   Optional kann ein Referenzpunkt rp oder extrasets erstellt werden. Optional kann ausserdem statt
   einer Vollkugel eine Hohlkugel erzeugt werden, wenn r_innen gegeben ist.
   Gibt [part<name>, inst<name>] zurueck.
   """
   import part
   import assembly
   from abaqusConstants import TET, FREE, ON
   from auswahl import BedingteAuswahl
   from hilfen import abapys_tol
   #
   Kugel_erstellen(modell=modell, name=name, radius=radius,
      materialtyp=materialtyp, r_innen=r_innen);
   partKugel = modell.parts[name];
   Grundkoerper_standardpartitionen(modell=modell, name=name, rp=rp);
   Grundkoerper_sets(modell=modell, name=name);
   if (extrasets):
      flaechen_Mantel = BedingteAuswahl(elemente=partKugel.faces,
         bedingung='sqrt(elem.pointOn[0][0]**2 + elem.pointOn[0][1]**2 + elem.pointOn[0][2]**2)) > var[0]-var[1]',
         var=[radius, abapys_tol]);
      partKugel.Set(name='setMantelflaeche', faces=flaechen_Mantel);
   #
   # FIXME: Immer notwendig, Kugeln als TET zu diskretisieren?
   partKugel.setMeshControls(elemShape=TET, regions=partKugel.cells, technique=FREE);
   Grundkoerper_vernetzen(modell=modell, name=name, materialtyp=materialtyp,
      gittergroesse=gittergroesse);
   #
   instname = 'inst' + name;
   modell.rootAssembly.Instance(dependent=ON, name=instname, part=partKugel);
   return [partKugel, modell.rootAssembly.instances[instname]];
#


# -------------------------------------------------------------------------------------------------
def Kugel_erstellen(modell, name, radius, materialtyp, r_innen=[]):
   """Erzeuge eine Kugel (Part) name im Modell modell mit uebergebenem radius und vom Typ
   materialtyp (Abaqus-Konstante, bspw. DEFORMABLE_BODY). Erzeuge eine Hohlkugel, falls r_innen
   gegeben ist.
   """
   import sketch
   import part
   from abaqusConstants import CLOCKWISE, THREE_D, OFF
   from zeichnung import Linie, KreisbogenWinkel
   #
   modell.ConstrainedSketch(name='__profile__', sheetSize=4.0*radius);
   zeichnung = modell.sketches['__profile__'];
   zeichnung.ConstructionLine(point1=(0.0, -radius), point2=(0.0, radius));
   zeichnung.FixedConstraint(entity=zeichnung.geometry.findAt((0.0, 0.0), ));
   #
   KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=radius,
      startwinkel=0.0, endwinkel=180.0, richtung=CLOCKWISE);
   if (not (r_innen == [])):
      Linie(zeichnung=zeichnung, punkt1=(0.0, radius), punkt2=(0.0, r_innen));
      KreisbogenWinkel(zeichnung=zeichnung, mittelpunkt=(0.0, 0.0), radius=r_innen,
         startwinkel=0.0, endwinkel=180.0, richtung=CLOCKWISE);
      Linie(zeichnung=zeichnung, punkt1=(0.0, -radius), punkt2=(0.0, -r_innen));
   else:
      Linie(zeichnung=zeichnung, punkt1=(0.0, radius), punkt2=(0.0, -radius));
   #
   modell.Part(dimensionality=THREE_D, name=name, type=materialtyp);
   modell.parts[name].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=zeichnung);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def Rotationsprofil_erstellen(modell, name, punkte, materialtyp, viertel=4):
   """Erzeuge durch eine Drehung um viertel*90 Grad ein Bauteil (Part) name im modell aus den
   Koordinaten aus punkte vom Typ materialtyp (Abaqus-Konstante, bspw. DEFORMABLE_BODY). Die in
   punke uebergebenen Tupel an x- und y-Koordinaten bilden eine Linie, wobei der letzte Punkt
   automatisch mit dem ersten verbunden wird. Fuer die Drehung (um die y-Achse der Zeichnung)
   muessen alle x-Koordinaten der Punkte >= 0 sein.
   Fuer viertel werden nur die Werte 1,2 und 4 unterstuetzt.
   """
   import sketch
   import part
   from abaqusConstants import CLOCKWISE, THREE_D, ON
   from zeichnung import Linienzug
   #
   maxwert = max([max(abs(x), abs(y)) for x, y in punkte]);
   zeichnung = modell.ConstrainedSketch(name='__profile__', sheetSize=2.0*maxwert,
      transform=(1.0, 0.0, 0.0,  0.0, 0.0, 1.0,  0.0, -1.0, 0.0,  0.0, 0.0, 0.0));
   zeichnung.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0));
   Linienzug(zeichnung=zeichnung, punkte=punkte, geschlossen=True);
   modell.Part(dimensionality=THREE_D, name=name, type=materialtyp);
   modell.parts[name].BaseSolidRevolve(sketch=zeichnung, angle=viertel*90.0, flipRevolveDirection=ON);
   del zeichnung;
#


# -------------------------------------------------------------------------------------------------
def Grundkoerper_standardpartitionen(modell, name, xPartition=True, yPartition=True, zPartition=True,
   rp=False):
   """Erstelle die typischen Datums und Partitionen am Bauteil (Part) name im modell. Optional kann
   die Erstellung einzelner Partitionen mit (x-/y-/z-Partition) unterdrueckt werden. Wenn rp=True
   uebergeben wird, wird zusaetzlich einen Referenzpunkt im Ursprung erstellt.
   """
   import part
   from abaqusConstants import XAXIS, YAXIS, ZAXIS
   #
   partGrundkoerper = modell.parts[name];
   #
   partGrundkoerper.DatumPointByCoordinate(coords=(0.0, 0.0, 0.0));
   partGrundkoerper.features.changeKey(fromName='Datum pt-1', toName='datum_Ursprung');
   datumid = partGrundkoerper.features['datum_Ursprung'].id;
   #
   partGrundkoerper.DatumAxisByPrincipalAxis(principalAxis=XAXIS);
   partGrundkoerper.features.changeKey(fromName='Datum axis-1', toName='xAchse');
   xachsenid = partGrundkoerper.features['xAchse'].id;
   partGrundkoerper.DatumAxisByPrincipalAxis(principalAxis=YAXIS);
   partGrundkoerper.features.changeKey(fromName='Datum axis-1', toName='yAchse');
   yachsenid = partGrundkoerper.features['yAchse'].id;
   partGrundkoerper.DatumAxisByPrincipalAxis(principalAxis=ZAXIS);
   partGrundkoerper.features.changeKey(fromName='Datum axis-1', toName='zAchse');
   zachsenid = partGrundkoerper.features['zAchse'].id;
   #
   if (xPartition):
      partGrundkoerper.PartitionCellByPlanePointNormal(cells=partGrundkoerper.cells,
         normal=partGrundkoerper.datums[xachsenid], point=partGrundkoerper.datums[datumid]);
   #
   if (yPartition):
      partGrundkoerper.PartitionCellByPlanePointNormal(cells=partGrundkoerper.cells,
         normal=partGrundkoerper.datums[yachsenid], point=partGrundkoerper.datums[datumid]);
   #
   if (zPartition):
      partGrundkoerper.PartitionCellByPlanePointNormal(cells=partGrundkoerper.cells,
         normal=partGrundkoerper.datums[zachsenid], point=partGrundkoerper.datums[datumid]);
   #
   if (rp):
      partGrundkoerper.ReferencePoint(point=(0.0, 0.0, 0.0));
      partGrundkoerper.features.changeKey(fromName='RP', toName='RP_' + name);
#


# -------------------------------------------------------------------------------------------------
def Grundkoerper_sets(modell, name):
   """Erstelle die Hauptsets fuer das Bauteil (Part) name im modell.
   """
   import part
   #
   partGrundkoerper = modell.parts[name];
   partGrundkoerper.Set(cells=partGrundkoerper.cells, name='setAll');
   rpname = 'RP_' + name;
   if (partGrundkoerper.features.has_key(rpname)):
      rpid = partGrundkoerper.features[rpname].id;
      partGrundkoerper.Set(name='setRP', referencePoints=(partGrundkoerper.referencePoints[rpid], ));
#


# -------------------------------------------------------------------------------------------------
def Grundkoerper_vernetzen(modell, name, materialtyp, gittergroesse):
   """Erzeuge ein Standardnetz fuer das Bauteil (Part) name im modell. materialtyp wird fuer die
   Zuweisung der korrekten Elemente benoetigt (Abaqus-Konstante, bspw. DEFORMABLE_BODY). Das Mesh
   kann ueber gittergroesse (Zahlenwert, [gitter_r, gitter_h] oder [gitter_x, gitter_y, gitter_z])
   angepasst werden.
   """
   import part
   import mesh
   from abaqusConstants import EULERIAN, EXPLICIT, OFF, EC3D8R, UNKNOWN_TET, UNKNOWN_WEDGE, DEFAULT
   from abaqusConstants import C3D8R, AVERAGE_STRAIN, C3D6, C3D4, FINER
   from auswahl import ZweifachbedingteKantenAuswahl
   #
   partGrundkoerper = modell.parts[name];
   #
   if (materialtyp == EULERIAN):
      partGrundkoerper.setElementType(elemTypes=(
         mesh.ElemType(elemCode=EC3D8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF),
         mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT),
         mesh.ElemType(elemCode=UNKNOWN_TET, elemLibrary=EXPLICIT)),
         regions=partGrundkoerper.sets['setAll']);
   else:
      partGrundkoerper.setElementType(elemTypes=(
         mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
         kinematicSplit=AVERAGE_STRAIN, hourglassControl=DEFAULT, 
         distortionControl=DEFAULT), mesh.ElemType(elemCode=C3D6, elemLibrary=EXPLICIT, 
         secondOrderAccuracy=OFF, distortionControl=DEFAULT), mesh.ElemType(
         elemCode=C3D4, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
         distortionControl=DEFAULT)), regions=partGrundkoerper.sets['setAll']);
   #
   if (isinstance(gittergroesse, list)):
      if (len(gittergroesse) == 2):
         gitter_r, gitter_h = gittergroesse;
         # Initialisiere mit Mittelwert aus allen drei Werten
         partGrundkoerper.seedPart(size=(gitter_r + gitter_h)/2.0, deviationFactor=0.1,
            minSizeFactor=0.1);
         kanten_r, kanten_h = ZweifachbedingteKantenAuswahl(elemente=partGrundkoerper,
            bedingung3='(vert1.pointOn[0][2] == vert2.pointOn[0][2])');
         partGrundkoerper.seedEdgeBySize(constraint=FINER, deviationFactor=0.1, edges=kanten_r,
            minSizeFactor=0.1, size=gitter_r);
         partGrundkoerper.seedEdgeBySize(constraint=FINER, deviationFactor=0.1, edges=kanten_h,
            minSizeFactor=0.1, size=gitter_h);
      else:
         gitter_x, gitter_y, gitter_z = gittergroesse;
         # Initialisiere mit Mittelwert aus allen drei Werten
         partGrundkoerper.seedPart(size=(gitter_x + gitter_y + gitter_z)/3.0, deviationFactor=0.1,
            minSizeFactor=0.1);
         kanten_x = ZweifachbedingteKantenAuswahl(elemente=partGrundkoerper,
            bedingung2='(vert1.pointOn[0][1] == vert2.pointOn[0][1]) and (vert1.pointOn[0][2] == vert2.pointOn[0][2])');
         partGrundkoerper.seedEdgeBySize(constraint=FINER, deviationFactor=0.1, edges=kanten_x[0],
            minSizeFactor=0.1, size=gitter_x);
         kanten_y = ZweifachbedingteKantenAuswahl(elemente=partGrundkoerper,
            bedingung2='(vert1.pointOn[0][0] == vert2.pointOn[0][0]) and (vert1.pointOn[0][2] == vert2.pointOn[0][2])');
         partGrundkoerper.seedEdgeBySize(constraint=FINER, deviationFactor=0.1, edges=kanten_y[0],
            minSizeFactor=0.1, size=gitter_y);
         kanten_z = ZweifachbedingteKantenAuswahl(elemente=partGrundkoerper,
            bedingung2='(vert1.pointOn[0][0] == vert2.pointOn[0][0]) and (vert1.pointOn[0][1] == vert2.pointOn[0][1])');
         partGrundkoerper.seedEdgeBySize(constraint=FINER, deviationFactor=0.1, edges=kanten_z[0],
            minSizeFactor=0.1, size=gitter_z);
   else:
      partGrundkoerper.seedPart(size=gittergroesse, deviationFactor=0.1, minSizeFactor=0.1);
   #
   partGrundkoerper.generateMesh();
#
