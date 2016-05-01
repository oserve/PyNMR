"""Main module declaring the module for pymol
contains interface for command line functions :
load CNS or DYANA distances constraints files
into molecular viewer, display them on the molecule
and show unSatisfied constraints according to a cutOff
with different color (White for not unSatisfied, blue for
lower limit violation, red for upper limit violation for NOEs)
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

from sys import stderr, stdout
from os.path import exists
import Tkinter as Tk

from Application.Core.NMRCore import NMRCore
from Application.NMRApplication import NMRApplication

configFileName = "pymolNMR.cfg"

if not exists(configFileName):
    configFileName = ""

Core = NMRCore()

pyNMR = NMRApplication(Core, app="NoGUI", configFileName=configFileName)


def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=lambda s=self: NMRApplication(Core, app="GUI", configFileName=configFileName))


def showNOE(structure='', managerName="", residuesList='all', dist_range='all',
            violationState='all', violCutoff=pyNMR.defaults["cutOff"],
            method="sum6", radius=pyNMR.defaults["radius"],
            colors=pyNMR.defaults["colors"],
            rangeCutOff=pyNMR.defaults["rangeCutOff"],
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
            Core.commandsInterpretation(structure, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method, rangeCutOff)
            results = Core.showSticks(managerName, structure, colors, radius,
                            UnSatisfactionMarker, SatisfactionMarker)
            stdout.write(str(results['numberOfConstraints']) +
                             " constraints drawn on a total of " +
                             str(len(Core.ManagersList[managerName])) + "\n")

        else:
            stderr.write("Please check constraints filename.\n")


def loadNOE(filename=""):
    """load NMR distance constraints, call for the correct file format
    (CNS/CYANA),
    """
    if exists(filename):
        Core.loadNOE(filename)
    else:
        stderr.write("File : " + filename + " has not been found.\n")


def showNOEDensity(structure='', managerName="", residuesList='all', dist_range='all',
                   violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                   rangeCutOff=pyNMR.defaults["rangeCutOff"],
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
            Core.commandsInterpretation(structure, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method, rangeCutOff)
            results = Core.showNOEDensity(managerName, structure, colors)
            stdout.write(str(results["numberOfConstraints"]) +
                         " constraints used.\n")
            stdout.write(str(results["numberOfResidues"]) +
                         " residues involved.\n")
        else:
            stderr.write("Please check constraints filename.\n")


def loadAndShow(filename, consDef, structure='', residuesList='all', dist_range='all',
                violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                method="sum6", rangeCutOff=pyNMR.defaults["rangeCutOff"],
                radius=pyNMR.defaults["radius"],
                colors=pyNMR.defaults["colors"]):
    """Combine two previous defined functions : load and display"""
    loadNOE(filename)
    showNOE(structure, filename, residuesList, dist_range, violationState,
            violCutoff, method, radius, colors, rangeCutOff)


def downloadNMR(pdbCode, url = pyNMR.defaults["urlPDB"]):
    """
    """
    Core.downloadFromPDB(pdbCode, url)

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
    extend("downloadNMR", downloadNMR)

except ImportError:
    stderr.write("Demo mode.\n")
