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
from GUI.NMRGUI import NMRGUI
import Core.MolecularViewerInterface as MVI
from GUI.Panels.appDefaults import defaultForParameter


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI"):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        if app == "NoGUI":
            print "Starting PyNMR CLI ..."
        else:
            print "Starting PyNMR GUI ..."
            self.startGUI()

    def startGUI(self):
        """
        """
        self.NMRInterface = NMRGUI()
        self.NMRInterface.startGUI()
        self.GUIBindings()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection['values'] = defaultForParameter('gradientColorList')
        self.NMRInterface.preferencesPanel.densityPanel.gradient.set(defaultForParameter("gradient"))
        self.NMRInterface.preferencesPanel.sticksPanel.colors = defaultForParameter("colors")
        self.NMRInterface.preferencesPanel.sticksPanel.UnSatisfactionMarker.set(defaultForParameter("UnSatisfactionMarker"))
        self.NMRInterface.preferencesPanel.sticksPanel.SatisfactionMarker.set(defaultForParameter("SatisfactionMarker"))
        self.NMRInterface.preferencesPanel.sticksPanel.radius.set(defaultForParameter("radius"))
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(defaultForParameter("cutOff"))
        self.NMRInterface.preferencesPanel.selectedMethod.set(defaultForParameter("method"))
        self.NMRInterface.preferencesPanel.rangeCutOff.set(defaultForParameter("rangeCutOff"))
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = self.getModelsNames()
        self.NMRInterface.preferencesPanel.url.set(defaultForParameter("urlPDB"))
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self
        self.NMRInterface.preferencesPanel.mainApp = self

    def getModelsNames(self):
        """
        """
        results = []
        objectsLists = MVI.get_names()
        for name in objectsLists:
            if name.find(defaultForParameter("UnSatisfactionMarker")) >= 0 or name.find(defaultForParameter("SatisfactionMarker")) >= 0:
                pass
            else:
                results.append(name)
        return results
