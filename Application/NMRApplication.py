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
from sys import stdout
from GUI.NMRGUI import NMRGUI
import Core.MolecularViewerInterface as MVI
from GUI.Panels.appDefaults import defaultForParameter
from NMRCLI import NMRCLI


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI"):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.NMRCLI = NMRCLI(Core)
        if app == "NoGUI":
            stdout.write("Starting PyNMR CLI ...\n")
        else:
            stdout.write("Starting PyNMR GUI ...\n")
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
        self.NMRInterface.preferencesPanel.setDefaults()
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(defaultForParameter("cutOff"))
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = MVI.getModelsNames(defaultForParameter('SatisfactionMarker'), defaultForParameter('UnSatisfactionMarker'))
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self
        self.NMRInterface.preferencesPanel.mainApp = self
