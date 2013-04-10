PyNMR
=====
Attempt to add [NMR](http://en.wikipedia.org/wiki/Nuclear_magnetic_resonance) abilities to molecular viewer [Pymol](http://pymol.org), including :

- Display distance constraints as sticks between atoms / group of atoms with color code

![NOESticks](pictures/sticks.tiff)

- Display distance constraint density as a color gradient on the molecular skeleton

![NOEDensity](pictures/density.tiff)

- Possibility to choose :
	- Method of distance calculation (ambiguous restraints)
	- Colors and size of NOE representations
- [CNS](http://cns-online.org) or [CYANA](http://www.cyana.org) format available
- Command line and GUI (using Tk and [Pmw](http://pmw.sourceforge.net))

This plugin actually works quite well, although some work is remaining.

Installation :
------------
###For development version :
- Copy the files into a single directory anywhere on your disk
- Edit .pymolrc in your home directory and add "run /path/to/files/pymolNMR.py"
- Edit variable "installDir" in pymolNMR.py (Hopefully this should not be needed in the future)

###For user friendly version :
- Download "PyNMRPG.py"
- Use the Pymol standard plugin install in the main menu

Start plugin :
------------

###For development version :

It is not a standard pymol plugin, so you have to type in the command line (or add in .pymolrc) : pyNMR.startGUI()

###For user friendly version :

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

Known difficulties :
------------------
* When displaying a large number of constraints as sticks, Pymol performances decrease rapidly :
	* Avoid to draw all constraints if not necessary
	* Remove them before any other action if you can
* The listbox behaviour is a bit eratic for now, use it just before the display buttons.
