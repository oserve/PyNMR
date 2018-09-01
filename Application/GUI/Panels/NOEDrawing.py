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
import ttk
from Application.GUI.DataViewer.NOEDataViewer import NOEDataViewer
from Application.DataControllers import NOEDataController


class NOEDrawingPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text="NOE Representation")
        self.sticksButton = ttk.Button(self, text="Sticks",
                                       command=self.showSticks)
        self.densityButton = ttk.Button(self, text="Density",
                                        command=self.showDensity)
        self.cleanButton = ttk.Button(self, text="Clean Sticks",
                                      command=self.cleanAll)
        self.mainGUI = None  # Must be set at run time
        self.NMRCommands = None  # Must be set by application at run time
        self.dataControllers = dict()
        self.dataViewers = dict()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.sticksButton.grid(row=0, column=0)
        self.densityButton.grid(row=0, column=1)
        self.cleanButton.grid(row=0, column=2)
    
    def showSticks(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])

            self.NMRCommands.showSticks(infos["constraintFile"],
                                        infos["structure"],
                                        infos["colors"],
                                        infos["radius"],
                                        infos["UnSatisfactionMarker"],
                                        infos["SatisfactionMarker"])

            view_callback = self.destroy_dataView_callback(infos["constraintFile"])
            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands.drawer.displayedConstraintsSticks.intersection(self.NMRCommands.get(infos["constraintFile"], "")),
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]], master=self.winfo_toplevel())
            self.dataViewers[infos["constraintFile"]].protocol("WM_DELETE_WINDOW", view_callback)

    def showDensity(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            self.NMRCommands.showNOEDensity(infos["constraintFile"],
                                            infos["structure"],
                                            infos["gradient"])

            view_callback = self.destroy_dataView_callback(infos["constraintFile"])
            
            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands.drawer.displayedConstraintsDensity.intersection(self.NMRCommands.get(infos["constraintFile"], "")),
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]])
            self.dataViewers[infos["constraintFile"]].protocol("WM_DELETE_WINDOW", view_callback)

    def cleanAll(self):
        """Remove all displayed sticks
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen()
            try:
                self.dataViewers[self.mainGUI.getInfo()["constraintFile"]].destroy()
                del self.dataViewers[self.mainGUI.getInfo()["constraintFile"]]
                del self.dataControllers[self.mainGUI.getInfo()["constraintFile"]]
            except KeyError:
                pass

    def destroy_dataView_callback(self, constraintFile):
        def callback():
            self.dataViewers[constraintFile].destroy()
            del self.dataViewers[constraintFile]
            del self.dataControllers[constraintFile]
        return callback

    @staticmethod
    def infoCheck(infos):
        """
        """
        return all(item != "" for item in infos.values())

    def getInfo(self):
        """
        """
        return {}
