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

from os import getcwd, chdir
from sys import stderr
from os.path import exists
#Needed to upload custom modules
INSTALL_DIR = "/Users/olivier/Pymol_scripts/PyNMR/"
WORKING_DIR = getcwd()
chdir(INSTALL_DIR)

from Application.Core.NMRCore import NMRCore
from Application.NMRApplication import NMRApplication

chdir(WORKING_DIR)

#Loading Core Functions
Core = NMRCore()

pyNMR = NMRApplication(Core)

def __init__(self):
    """
    Init PyMOL, by adding APBSTools to the GUI under Plugins
    
    Creates the APBS widget/notebook.  Once the event is received,
    we create a new instance of APBSTools2 which is a Pmw, which upon
    creation shows itself.
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command = lambda s=self: NMRApplication(Core, s))

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
            Core.showSticks(managerName, pdb, colors, radius)
        else:
            stderr.write("Please check constraints filename.\n")


def loadNOE(filename="", consDef=""):
    """load NMR distance constraints, call for the correct file format (CNS/CYANA),
    """
    if exists(filename):
        Core.loadNOE(filename, consDef.upper())
    else:
        stderr.write("File : " + filename + " has not been found.\n")


def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method='sum6', colors=pyNMR.defaults["gradient"]):
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
            Core.showNOEDensity(managerName, pdb, colors)
        else:
            stderr.write("Please check constraints filename.\n")


def loadAndShow(filename, consDef, pdb='', residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
    """
    """
    loadNOE(filename, consDef)
    showNOE(pdb,filename, residuesList, dist_range, violationState, violCutoff, method, radius, colors)


def cleanScreen(filename):
    if filename in Core.ManagersList:
        Core.cleanScreen(filename)

if __name__ == "__main__":
    pyNMR.startGUI()
    #pyNMR.NMRInterface.mainloop()

try:
    from pymol.cmd import extend
    extend("loadNOE", loadNOE)
    extend("showNOE", showNOE)
    extend("showNOEDensity", showNOEDensity)
    extend("loadAndShow", loadAndShow)

except ImportError:
    stderr.write("Demo mode.\n")
