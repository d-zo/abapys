
abapys 0.6.6
============

[abapys](https://github.com/d-zo/abapys) is a collection of special purpose Python functions 
for creating parametrized models or postprocessing simulation results with
the commercial Finite-Element-Analysis software
[Abaqus](https://www.3ds.com/products-services/simulia/products/abaqus/ "SIMULIA Abaqus").
It was created alongside work at the Institute of Geotechnical Engineering
at the Hamburg University of Technology.
Therefore it is centered around model creation and output processing for simulations of
soil samples and soil-structure interaction.
All functions were tested for Abaqus versions between 6.14-2 (2015) and Abaqus 2020.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4467987.svg)](https://doi.org/10.5281/zenodo.4467987)



Installation
------------

abapys requires the commercial Finite-Element-Analysis software
[Abaqus](https://www.3ds.com/products-services/simulia/products/abaqus/ "SIMULIA Abaqus")
and uses its Python interpreter.
Although it could be integrated within Abaqus' Python environment,
it can also be included in the module path and imported.
Therefore it can be stored in an arbitrary folder and loaded by

```
abapys_dir = r'C:\path\to\abapys' # For Windows-based systems
abapys_dir = '/path/to/abapys'    # For Linux-based systems
sys.path.insert(0, abapys_dir);

from abapys import *
```

abapys can use material parameters from Spreadsheets (`.xlsx`-files).
To read those files [openpyxl](https://openpyxl.readthedocs.io)
and its dependencies [et_xmlfile](https://pypi.org/project/et_xmlfile/)
and [jdcal](https://github.com/phn/jdcal) are used as external dependencies
and have to be provided.
One possible solution is to install abapys and those dependencies in one folder,
which has to be included in the module path. The structure should look like the following

```
abapys/
   +- abapys/
   |      +- __init__.py
   |      +- ausgabe.py
   |      +- beautify.py
   |      + ...
   |
   +- Materialdatenbank_20####.xlsx
   +- gewichtung.dll
   +- gewichtung.so
   |
   +- openpyxl/
   |      +- cell/
   |      +- chart/
   |      +- chartsheet/
   |      + ...
   |
   +- et_xmlfile/
   |      +- tests/
   |      +- __init__.py
   |      +- xmlfile.py
   |
   +- jdcal.py
```



Usage and Documentation
-----------------------

A simple function documentation (in german) created with pydoc can be found
[here](https://d-zo.github.io/abapys/abapys.html "abapys documentation").
The functions can either be called in the Abaqus command prompt for interactive results or
put in scripts with other commands to record a sequence of instructions.
The basic usage and some examples are given in the ”Abaqus scripting with abapys“ tutorial.
A html-version of the tutorial can be found
[here](https://d-zo.github.io/abapys/abapysscripting.html "Abaqus scripting with abapys [html]")
and a pdf-version
[here](https://d-zo.github.io/abapys/abapysscripting.pdf "Abaqus scripting with abapys [pdf]").

Another project called [SimpleScriptGenerator](https://github.com/d-zo/SimpleScriptGenerator)
can help to create scripts with abapys functions.
[SimpleScriptGenerator](https://github.com/d-zo/SimpleScriptGenerator) is providing
a user interface for intuitive and interactive script creation.
The logic and content of it can be adjusted with different configuration files.
So a preconfigured configuration named _abapys_front_ can be used
to create scripts with Abaqus commands and abapys functions.
Abaqus and abapys are not necessary to create these scripts.
In order to run the scripts however, both tools are required.

If you have no or very little knowledge of Abaqus,
you may want to have a look at some tutorials (and the resulting Python code) first.
There is also a tutorial called ”Pile jacking example in Abaqus“,
which can help getting started with Abaqus and Python.
An html-version of the tutorial can be found
[here](https://d-zo.github.io/abapys/pilejackingexample.html "Pile jacking example in Abaqus [html]")
and an pdf-version
[here](https://d-zo.github.io/abapys/pilejackingexample.pdf "Pile jacking example in Abaqus [pdf]").



Structure
---------

Originally all abapys functions were written in Python.
Due to speed issues a library for finding points in elements and their weighting
was converted to C++ (_gewichtung.dll_ and _gewichtung.so_).
The functions are saved in different files,
but those with similar scope are usually saved in the same file:

 - _ausgabe.py_: Adjust/saving the viewport and extracting/plotting/saving simulation results
 - _auswahl.py_: Selection of geometric entities by condition/labels
 - _beautify.py_: Subjective viewport beautification function
 - _boden.py_: Create soil body and assign stress states
 - _bodendatenbank.py_: Load soil material parameters from spreadsheet
 - _bohrprofil.py_: Create screw and full displacement pile parts
 - _erstellung.py_: Connector constraints and reference point coupling
 - _gewichtung.cpp_: Weighting of one set of elements/nodes in regard to another set of elements/nodes
 - _grundkoerper.py_: Create basic geometric parts
 - _hilfen.py_: Initialisation and general-purpose functions
 - _punktinelement.py_: Point localisation/weighting and volume calculation of elements
 - _uebertragung.py_: Initialise/transfer state variables from one mesh to another
 - _zahnrad.py_: Create a gear wheel part (lantern pinion)
 - _zeichnung.py_: Create sketches for part extrusion or revolution



Contributing
------------

**Bug reports**

If you found a bug, make sure you can reproduce it with the latest version of abapys.
Please check that the expected results can actually be achieved by other means
and are not considered invalid operations in Abaqus and its Python interpreter.
Please give detailed and reproducible instructions in your report including

 - the abapys version
 - the expected result
 - the result you received
 - the command(s) used as a _minimal working example_

Note: The bug should ideally be reproducible by the _minimal working example_ alone.
Please keep the example code as short as possible (minimal).
Try not to load additional files like `.cae` or `.odb` if possible.
If it can't be avoided make them as small and simple as possible.


**Feature requests**

If you have an idea for a new feature, consider searching the
[open issues](https://github.com/d-zo/abapys/issues) and
[closed issues](https://github.com/d-zo/abapys/issues?q=is%3Aissue+is%3Aclosed) first.
Afterwards, please submit a report in the
[Issue tracker](https://github.com/d-zo/abapys/issues) explaining the feature and especially

 - why this feature would be useful (use cases)
 - what could possible drawbacks be (e.g. compatibility, dependencies, ...)



Similar software
----------------

There is a project called [abapy](https://github.com/lcharleux/abapy) which also provides
a collection of Python functions for use in Abaqus.
But the intention and focus of the functions are completely different.



License
-------

abapys is released under the
[GPL](https://www.gnu.org/licenses/gpl-3.0.html "GNU General Public License"),
version 3 or greater (see also [LICENSE](https://github.com/d-zo/abapys/blob/master/LICENSE) file).
It is provided without any warranty.

