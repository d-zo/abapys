#-*- coding: utf-8 -*-
"""
zeichnung.py   v0.75 (2019-08)
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
def Linie(zeichnung, punkt1, punkt2, bemasst=True):
   """Erstelle in der zeichnung eine gerade Linie von punkt1 zu punkt2. Optional kann die Bemassung
   mit bemasst=False deaktiviert werden.
   """
   from math import sqrt
   import sketch
   #
   zeichnung.Line(point1=punkt1, point2=punkt2);
   if   (punkt1[1] == punkt2[1]):
      mittelpunktx = (punkt1[0] + punkt2[0])/2.0;
      #zeichnung.HorizontalConstraint(entity=zeichnung.geometry.findAt((mittelpunktx, punkt1[1]), ));
      if (bemasst):
         zeichnung.HorizontalDimension(textPoint=(mittelpunktx, punkt2[1]+0.25*(punkt2[0]-punkt1[0])),
            value=abs(punkt2[0] - punkt1[0]),
            vertex1=zeichnung.vertices.findAt(punkt1, ),
            vertex2=zeichnung.vertices.findAt(punkt2, ));
   elif (punkt1[0] == punkt2[0]):
      mittelpunkty = (punkt1[1] + punkt2[1])/2.0;
      #zeichnung.VerticalConstraint(entity=zeichnung.geometry.findAt((punkt1[0], mittelpunkty), ));
      if (bemasst):
         zeichnung.VerticalDimension(textPoint=(punkt1[0]+0.25*(punkt2[1]-punkt1[1]), mittelpunkty),
            value=abs(punkt2[1] - punkt1[1]),
            vertex1=zeichnung.vertices.findAt(punkt1, ),
            vertex2=zeichnung.vertices.findAt(punkt2, ));
   else:
      if (bemasst):
         if ((punkt1[0]**2 + punkt2[1]**2) > (punkt2[0]**2 + punkt1[1]**2)):
            textpunkt = (punkt1[0], punkt2[1]);
         else:
            textpunkt = (punkt2[0], punkt1[1]);
         zeichnung.ObliqueDimension(textPoint=textpunkt,
            value=sqrt((punkt2[0] - punkt1[0])**2 + (punkt2[1] - punkt1[1])**2),
            vertex1=zeichnung.vertices.findAt(punkt1, ),
            vertex2=zeichnung.vertices.findAt(punkt2, ));
#


# -------------------------------------------------------------------------------------------------
def Linienzug(zeichnung, punkte, geschlossen=False, bemasst=True):
   """Erstelle in der zeichnung einen Linienzug von/durch alle punkte. Optional kann der Linienzug
   geschlossen werden (erste Punkt wird mit letztem verbunden). Optional kann ausserdem die
   Bemassung mit bemasst=False deaktiviert werden.
   """
   for idx, aktuellerpunkt in enumerate(punkte):
      if (idx > 0):
         Linie(zeichnung=zeichnung, punkt1=punkte[idx-1], punkt2=aktuellerpunkt, bemasst=bemasst);
   #
   if (geschlossen):
      Linie(zeichnung=zeichnung, punkt1=punkte[-1], punkt2=punkte[0], bemasst=False);
#


# -------------------------------------------------------------------------------------------------
def Rechteck(zeichnung, punkt1, punkt2, bemasst=True):
   """Erstelle in der zeichnung ein Rechteck von punkt1 zu punkt2. Optional kann die Bemassung mit
   bemasst=False deaktiviert werden.
   """
   import sketch
   #
   zeichnung.rectangle(point1=punkt1, point2=punkt2);
   #zeichnung.HorizontalConstraint(entity=zeichnung.geometry.findAt(
   #   ((punkt1[0] + punkt1[0])/2.0, punkt2[1]), ));
   zeichnung.HorizontalDimension(value=abs(punkt2[0]-punkt1[0]),
      textPoint=((punkt1[0] + punkt2[0])/2.0, punkt2[1]+0.25*(punkt2[0]-punkt1[0])),
      vertex1=zeichnung.vertices.findAt((punkt1[0], punkt2[1]), ),
      vertex2=zeichnung.vertices.findAt((punkt2[0], punkt2[1]), ));
   zeichnung.VerticalDimension(value=abs(punkt2[1]-punkt1[1]),
      textPoint=(punkt1[0]+0.25*(punkt2[1]-punkt1[1]), (punkt1[1] + punkt2[1])/2.0),
      vertex1=zeichnung.vertices.findAt((punkt1[0], punkt1[1]), ),
      vertex2=zeichnung.vertices.findAt((punkt1[0], punkt2[1]), ));
#
   

# -------------------------------------------------------------------------------------------------
def Kreis(zeichnung, mittelpunkt, radius, bemasst=True):
   """Erstelle in der zeichnung einen Kreis mit gegebenem mittelpunkt und radius. Optional kann die
   Bemassung mit bemasst=False deaktiviert werden.
   """
   from math import sqrt
   import sketch
   #
   zeichnung.CircleByCenterPerimeter(center=mittelpunkt,
      point1=(mittelpunkt[0]+radius, mittelpunkt[1]));
   if (bemasst):
      zeichnung.RadialDimension(radius=radius,
         textPoint=(mittelpunkt[0]+radius/2.0, mittelpunkt[1]+radius/2.0),
         curve=zeichnung.geometry.findAt((mittelpunkt[0]+radius/sqrt(2), mittelpunkt[1]+radius/sqrt(2)), ));
#


# -------------------------------------------------------------------------------------------------
def KreisbogenWinkel(zeichnung, mittelpunkt, radius, startwinkel, endwinkel, richtung, bemasst=True):
   """Erstelle in der zeichnung einen Kreisbogen mit gegebenem mittelpunkt und radius. Startpunkt
   und Endpunkt sind ueber startwinkel, endwinkel (in Grad) und richtung definiert (richtung mit
   Abaqus-Konstante CLOCKWISE oder COUNTERCLOCKWISE). Optional kann die Bemassung mit bemasst=False
   deaktiviert werden.
   """
   from math import sin, cos
   from hilfen import grad2rad
   #
   KreisbogenPunkte(zeichnung=zeichnung, mittelpunkt=mittelpunkt, 
      punkt1=(mittelpunkt[0] + radius*sin(startwinkel*grad2rad),
              mittelpunkt[1] + radius*cos(startwinkel*grad2rad)),
      punkt2=(mittelpunkt[0] + radius*sin(endwinkel*grad2rad),
              mittelpunkt[1] + radius*cos(endwinkel*grad2rad)),
      richtung=richtung, bemasst=bemasst);
#


# -------------------------------------------------------------------------------------------------
def KreisbogenPunkte(zeichnung, mittelpunkt, punkt1, punkt2, richtung, bemasst=True):
   """Erstelle in der zeichnung einen Kreisbogen mit gegebenem mittelpunkt und radius von punkt1
   nach punkt2 in gegebener richtung (Abaqus-Konstante CLOCKWISE oder COUNTERCLOCKWISE).
   Optional kann die Bemassung mit bemasst=False deaktiviert werden.
   """
   from math import sqrt
   import sketch
   from abaqusConstants import CLOCKWISE
   #
   zeichnung.ArcByCenterEnds(center=mittelpunkt, point1=punkt1, point2=punkt2, direction=richtung);
   if (bemasst):
      # Richtung ist definiert als die Normale der Verbindungslinie
      mp_richtung = (punkt1[1] - punkt2[1], punkt2[0] - punkt1[0]);
      laenge_mp_richtung = sqrt(mp_richtung[0]**2 + mp_richtung[1]**2);
      mp_richtung = (mp_richtung[0]/laenge_mp_richtung, mp_richtung[1]/laenge_mp_richtung);
      #
      radius = sqrt((mittelpunkt[0]-punkt1[0])**2 + (mittelpunkt[1]-punkt1[1])**2);
      # Einer von zwei moeglichen Punkten liegt auf dem Kreisbogen
      if (richtung == CLOCKWISE):
         masspunkt = (mittelpunkt[0] + mp_richtung[0]*radius,
                      mittelpunkt[1] + mp_richtung[1]*radius);
      else:
         masspunkt = (mittelpunkt[0] - mp_richtung[0]*radius,
                      mittelpunkt[1] - mp_richtung[1]*radius);
      #
      textpunkt = ((mittelpunkt[0] + masspunkt[0])/2.0, (mittelpunkt[1] + masspunkt[1])/2.0);
      zeichnung.RadialDimension(curve=zeichnung.geometry.findAt(masspunkt, ), radius=radius,
         textPoint=textpunkt);
#
