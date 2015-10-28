PyNMR
=====
Attempt to add [NMR](http://en.wikipedia.org/wiki/Nuclear_magnetic_resonance) abilities to molecular viewer [Pymol](http://pymol.org).

NMR can provide useful information to create molecular models, such as distance between atoms (usually protons in biomolecuar biology).
This plugin allows to display those informations, called "distance contraints" directly onto the molecular skeleton of proteins.
It can do so in two different ways :

- Display distance constraints as sticks between atoms / group of atoms with color code

![NOESticks](pictures/sticks.tiff)

- Display distance constraint density as a color gradient on the molecular skeleton

![NOEDensity](pictures/density.tiff)

I believe this could help a lot in the tedious process of determining whether the 
constraints extracted from the nmr spectrum make sens or not.

Additional Possibilities :
---
- Import popular data format [CNS](http://cns-online.org) or [CYANA](http://www.cyana.org)
- Command line and GUI
- Download NMR restraints file from the [PDB](http://www.rcsb.org/pdb/home/home.do)
- Choose method of distance calculation between atoms (in case of ambiguous restraints)
- Colors and size of NOE representations

Installation :
------------
###For development version :
- Copy all files into a single directory anywhere on your disk

###For user friendly version :
- Download "PyNMRPG.py"

For both versions, use the Pymol standard plugin install in the main menu

Start plugin :
------------

Start PyNMR from the plugin menu.

Usage :
-----
The GUI is quite straightforward for NMR people I think. For CLI, read pymolNMR.py.

![Interface](pictures/mainWindow.tiff) ![Preferences](pictures/preferences.tiff)

Possible future features :
------------------------

* Display of angular, dihedral and h-bonds constraints
* Text list of constraints with :
    * Color code
    * Link to 3D display
    * Real-time edit / display
* Increase speed

Known difficulties :
------------------
* When displaying a large number of constraints as sticks, Pymol performances decrease rapidly :
    * Avoid to draw all constraints if not necessary
    * Remove them before any other action if you can