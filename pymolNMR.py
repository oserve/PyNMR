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
from sys import stderr, version_info
if version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

from Application.Core.NMRCore import NMRCore
from Application.NMRApplication import NMRApplication

import Application.GUI.Panels.appDefaults as appDefaults

appDefaults.loadDefaults()

Core = NMRCore()

pyNMR = NMRApplication(Core)

def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=NMR_GUI)


PyNMRCLI = pyNMR.NMRCLI

def showNOE(structure='', managerName="", residuesList='all',
            dist_range='all', violationState='all',
            violCutoff=appDefaults.defaultForParameter("cutOff"),
            method=appDefaults.defaultForParameter('method'),
            radius=appDefaults.defaultForParameter("radius"),
            colors=appDefaults.defaultForParameter("colors"),
            rangeCutOff=appDefaults.defaultForParameter("rangeCutOff"),
            UnSatisfactionMarker=appDefaults.defaultForParameter("UnSatisfactionMarker"),
            SatisfactionMarker=appDefaults.defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.showNOE(structure, managerName, residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker)

def LoadConstraints(filename=""):
    """
    """
    PyNMRCLI.LoadConstraints(filename)

def showNOEDensity(structure='', managerName="", residuesList='all',
                   dist_range='all', violationState='all',
                   violCutoff=appDefaults.defaultForParameter("cutOff"),
                   rangeCutOff=appDefaults.defaultForParameter("rangeCutOff"),
                   method=appDefaults.defaultForParameter('method'),
                   colors=appDefaults.defaultForParameter("gradient")):
    """
    """
    PyNMRCLI.showNOEDensity(structure, managerName, residuesList,
                            dist_range, violationState, violCutoff, rangeCutOff,
                            method, colors)

def loadAndShow(filename, structure='', residuesList='all', dist_range='all',
                violationState='all',
                violCutoff=appDefaults.defaultForParameter("cutOff"),
                method=appDefaults.defaultForParameter('method'),
                rangeCutOff=appDefaults.defaultForParameter("rangeCutOff"),
                radius=appDefaults.defaultForParameter("radius"),
                colors=appDefaults.defaultForParameter("colors"),
                UnSatisfactionMarker=appDefaults.defaultForParameter("UnSatisfactionMarker"),
                SatisfactionMarker=appDefaults.defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.loadAndShow(filename, structure, residuesList, dist_range,
                         violationState, violCutoff, method, rangeCutOff,
                         radius, colors, UnSatisfactionMarker,
                         SatisfactionMarker)

def downloadNMR(pdbCode, url=appDefaults.defaultForParameter("urlPDB")):
    """
    """
    PyNMRCLI.downloadNMR(pdbCode, url)

def cleanScreen(filename):
    """
    """
    PyNMRCLI.cleanScreen(filename)

def NMR_GUI():
    from pymol import plugins
    root = plugins.get_tk_root()
    app = plugins.get_pmgapp()
    pyNMR.startGUI(Tk.Toplevel(root))


if __name__ == "__main__":
    MainWin = Tk.Tk()
    pyNMR.startGUI(MainWin)
    MainWin.mainloop()
try:
    from pymol.cmd import extend
    extend("load_Constraints", LoadConstraints)
    extend("showNOE", showNOE)
    extend("showNOEDensity", showNOEDensity)
    extend("loadAndShow", loadAndShow)
    extend("downloadNMR", downloadNMR)
    extend("cleanScreen", cleanScreen)
    extend("NMR_GUI", NMR_GUI)
except ImportError:
    stderr.write("Demo mode.\n")
