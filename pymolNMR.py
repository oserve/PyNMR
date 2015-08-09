"""Main module declaring the module for pymol
contains interface for command line functions
"""
# Copyright Notice
# ================
#
# The PyMOL Plugin source code in this file is copyrighted, but you can
# freely use and copy it as long as you don't change or remove any of
# the copyright notices.
#
# ----------------------------------------------------------------------
#               This PyMOL Plugin is Copyright (C) 2013 by
#                 olivier serve <olivier dot serve at gmail dot com>
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name(s) of the author(s) not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# THE AUTHOR(S) DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------

# from os import getcwd, chdir
from sys import stderr
from os.path import exists
import Tkinter as Tk
# Needed to upload custom modules
# INSTALL_DIR = "/Users/olivier/Pymol_scripts/PyNMR/"
# WORKING_DIR = getcwd()
# chdir(INSTALL_DIR)

from Application.Core.NMRCore import NMRCore
from Application.NMRApplication import NMRApplication

# chdir(WORKING_DIR)

# Loading Core Functions
Core = NMRCore()

pyNMR = NMRApplication(Core)


def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=lambda s=self: NMRApplication(Core, s))


def showNOE(pdb='', managerName="", residuesList='all', dist_range='all',
            violationState='all', violCutoff=pyNMR.defaults["cutOff"],
            method="sum6", radius=pyNMR.defaults["radius"],
            colors=pyNMR.defaults["colors"],
            UnSatisfactionMarker=pyNMR.defaults["UnSatisfactionMarker"],
            SatisfactionMarker=pyNMR.defaults["SatisfactionMarker"]):
    """Command to display NMR restraints as sticks on protein structure with
    different parameters : filtering according to distance, restraints display
    options
    """
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method)
            Core.showSticks(managerName, pdb, colors, radius, UnSatisfactionMarker,
                            SatisfactionMarker)
        else:
            stderr.write("Please check constraints filename.\n")


def loadNOE(filename="", consDef=""):
    """load NMR distance constraints, call for the correct file format
    (CNS/CYANA),
    """
    if exists(filename):
        Core.loadNOE(filename, consDef.upper())
    else:
        stderr.write("File : " + filename + " has not been found.\n")


def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all',
                   violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                   method='sum6', colors=pyNMR.defaults["gradient"]):
    """Command to display NMR restraints as color map on protein structure with
    different parameters : filtering according to distance, restraints display
    options
    """
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method)
            Core.showNOEDensity(managerName, pdb, colors)
        else:
            stderr.write("Please check constraints filename.\n")


def loadAndShow(filename, consDef, pdb='', residuesList='all', dist_range='all',
                violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                method="sum6", radius=pyNMR.defaults["radius"],
                colors=pyNMR.defaults["colors"]):
    """Combine two previous defined functions : load and display"""
    loadNOE(filename, consDef)
    showNOE(pdb, filename, residuesList, dist_range, violationState, violCutoff,
            method, radius, colors)


def cleanScreen(filename):
    """Call the command to clear the screen from all NMR
    restraints
    """
    if filename in Core.ManagersList:
        Core.cleanScreen(filename)

if __name__ == "__main__":
    MainWin = Tk.Tk()
    pyNMR.startGUI()
    MainWin.mainloop()

try:
    from pymol.cmd import extend
    extend("loadNOE", loadNOE)
    extend("showNOE", showNOE)
    extend("showNOEDensity", showNOEDensity)
    extend("loadAndShow", loadAndShow)

except ImportError:
    stderr.write("Demo mode.\n")
