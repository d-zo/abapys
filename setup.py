# -*- coding: utf-8 -*-
"""
setup.py  v0.1 (2020-11)
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

from setuptools import setup

setup(
   name='abapys',
   version='0.6.4',
   author='Dominik Zobel',
   author_email='dominik.zobel@tuhh.de',
   description='Special purpose Python functions for Abaqus',
   long_description='abapys is a collection of special purpose Python functions using the commercial Finite-Element-Analysis software Abaqus. It is centered around model creation and output processing for simulations of soil samples and soil-structure interaction.',
   license='GPL',
   url='https://github.com/d-zo/abapys',
   install_requires=['openpyxl'],
   )
   
