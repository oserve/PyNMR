from GUI.NMRGUI import NMRGUI
from Core.MolecularViewerInterface import get_names


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI"):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.defaults = {
            "radius": 0.03, "cutOff": 0.3,
            "colors": {
                'notViolated': [1, 1, 1, 1, 1, 1],
                'tooFar': [1, 0, 0, 1, 0, 0],
                'tooClose': [0, 0, 1, 0, 0, 1]
                },
            'gradient': "blue_white_red", "method": "sum6"
            }
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
        self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(self.defaults["cutOff"])
        #self.NMRInterface.preferencesPanel.methodSelection.setvalue(self.defaults["method"])
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = self.getModelsNames()
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self

    def getModelsNames(self):
        """
        """
        results = []
        objectsLists = get_names()
        for name in objectsLists:
            if len(self.NMRCommands.ManagersList):
                for managerName in self.NMRCommands.ManagersList.keys():
                    if name.find(managerName) < 0:
                        if name not in results:
                            results.append(name)
            else:
                if name not in results:
                    results.append(name)
        return results
