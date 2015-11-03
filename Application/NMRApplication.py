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
from Core.MolecularViewerInterface import get_names
import pickle


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI", configFileName=""):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.StandardPrefDefaults = {
            "radius": 0.03, "cutOff": 0.3,
            "colors": {
                'Satisfied': [1, 1, 1, 1, 1, 1],
                'tooFar': [1, 0, 0, 1, 0, 0],
                'tooClose': [0, 0, 1, 0, 0, 1]
                },
            'gradient': "blue_white_red", "method": "sum6",
            'UnSatisfactionMarker': "_US_", 'SatisfactionMarker': '_S_',
            'rangeCutOff': 5,
            'urlPDB': "ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/"}
        self.gradientColorList = [
            "blue_green", "blue_magenta", "blue_red", "blue_white_green",
            "blue_white_magenta", "blue_white_red", "blue_white_yellow",
            "blue_yellow", "cbmr", "cyan_magenta", "cyan_red",
            "cyan_white_magenta", "cyan_white_red", "cyan_white_yellow",
            "cyan_yellow", "gcbmry", "green_blue", "green_magenta",
            "green_red", "green_white_blue", "green_white_magenta",
            "green_white_red", "green_white_yellow", "green_yellow",
            "green_yellow_red", "magenta_blue", "magenta_cyan",
            "magenta_green", "magenta_white_blue", "magenta_white_cyan",
            "magenta_white_green", "magenta_white_yellow", "magenta_yellow",
            "rainbow", "rainbow2", "rainbow2_rev", "rainbow_cycle",
            "rainbow_cycle_rev", "rainbow_rev", "red_blue", "red_cyan",
            "red_green", "red_white_blue", "red_white_cyan", "red_white_green",
            "red_white_yellow", "red_yellow", "red_yellow_green", "rmbc",
            "yellow_blue", "yellow_cyan", "yellow_cyan_white", "yellow_green",
            "yellow_magenta", "yellow_red", "yellow_white_blue",
            "yellow_white_green", "yellow_white_magenta", "yellow_white_red",
            "yrmbcg"
            ]
        if configFileName == "pymolNMR.cfg":
            configFile = open(configFileName, 'r')
            self.defaults = pickle.load(configFile)
            configFile.close()
            self.configFileName = configFileName
        else:
            self.defaults = self.StandardPrefDefaults
            self.configFileName = "pymolNMR.cfg"
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
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection['values'] = self.gradientColorList
        self.NMRInterface.preferencesPanel.densityPanel.gradient.set(self.defaults["gradient"])
        self.NMRInterface.preferencesPanel.sticksPanel.colors = self.defaults["colors"]
        self.NMRInterface.preferencesPanel.sticksPanel.UnSatisfactionMarker.set(self.defaults["UnSatisfactionMarker"])
        self.NMRInterface.preferencesPanel.sticksPanel.SatisfactionMarker.set(self.defaults["SatisfactionMarker"])
        self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(self.defaults["cutOff"])
        self.NMRInterface.preferencesPanel.selectedMethod.set(self.defaults["method"])
        self.NMRInterface.preferencesPanel.rangeCutOff.set(self.defaults["rangeCutOff"])
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = self.getModelsNames()
        self.NMRInterface.preferencesPanel.configFileName = self.configFileName
        self.NMRInterface.preferencesPanel.url.set(self.defaults["urlPDB"])
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
        objectsLists = get_names()
        for name in objectsLists:
            if name.find(self.defaults["UnSatisfactionMarker"]) >= 0 or name.find(self.defaults["SatisfactionMarker"]) >= 0:
                pass
            else:
                results.append(name)
        return results
