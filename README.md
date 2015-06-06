PyNMR
=====
Attempt to add [NMR](http://en.wikipedia.org/wiki/Nuclear_magnetic_resonance) abilities to molecular viewer [Pymol](http://pymol.org).

NMR can provide useful information to create molecular model, such as distance between atoms (usually protons in biomolecuar biology).
This plugin allows to display those informations, called "distance contraints" directly onto the molecular skeleton of proteins.
It can do so in two different ways :
- Display distance constraints as sticks between atoms / group of atoms with color code

![NOESticks](pictures/sticks.tiff)

- Display distance constraint density as a color gradient on the molecular skeleton

![NOEDensity](pictures/density.tiff)

I believe this could help a lot in the tedious process of determining whether the 
constraints extracted from the nmr spectrum make sens or not.

The plugins offers the following possibilities :

- Method of distance calculation (ambiguous restraints)
- Colors and size of NOE representations
- Import popular data format [CNS](http://cns-online.org) or [CYANA](http://www.cyana.org)
- Command line and GUI (using Tk)

This plugin actually works quite well, although some work is remaining.

Installation :
------------
###For development version :
- Copy the files into a single directory anywhere on your disk
- Edit variable "installDir" in pymolNMR.py using your favorite text editor (Hopefully this should not be needed in the future)

###For user friendly version :
- Download "PyNMRPG.py"

For both versions, use the Pymol standard plugin install in the main menu

Start plugin :
------------

Start PyNMR from the plugin menu.

Usage :
-----
The GUI is quite straightforward for NMR people I think. For CLI, read pymolNMR.py.

![Interface](pictures/mainWindow.tiff)

Possible future features :
------------------------

* Display of angular, dihedral and h-bonds constraints
* Text list of constraints with :
    * Color code
    * Link to 3D display
    * Real-time edit / display
* Increase speed
* Download restraints from pdb.org (almost here hang on)

Known difficulties :
------------------
* When displaying a large number of constraints as sticks, Pymol performances decrease rapidly :
    * Avoid to draw all constraints if not necessary
    * Remove them before any other action if you can