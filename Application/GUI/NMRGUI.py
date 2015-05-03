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
import Tkinter as Tk
import ttk
#import Pmw

from Panels.Preferences import PreferencesPanel
from Panels.FileSelection import FileSelectionPanel
from Panels.ConstraintSelection import ConstraintSelectionPanel
from Panels.NOEDrawing import NOEDrawingPanel

class NMRGUI(Tk.Tk):
    def __init__ (self):
        Tk.Tk.__init__(self)
        self.title('PymolNMR')
        self.panelsList = []

    def createPanels(self):
        #Main Frames (not IBM ;-)
        self.mainFrame = Tk.Frame(self).pack()
        self.noteBook = ttk.Notebook(self.mainFrame)
        # self.mainPage = self.noteBook.add("Main")
        self.noteBook.grid(row=0, column=0)
        self.constraintSelectionManagement = ConstraintSelectionPanel(self.noteBook)
        self.noteBook.add(self.constraintSelectionManagement, text = "Selection")
        self.panelsList.append(self.constraintSelectionManagement)

        self.constraintFilesManagement = FileSelectionPanel(self.noteBook)
        self.panelsList.append(self.constraintFilesManagement,)
        self.noteBook.add(self.constraintFilesManagement, text = "Management") 
        self.NOEDrawingManagement = NOEDrawingPanel(self.noteBook)
        self.panelsList.append(self.NOEDrawingManagement)
        self.noteBook.add(self.NOEDrawingManagement, text = "Drawings")
        # self.preferencesPage = self.noteBook.add("Preferences")

        self.preferencesPanel = PreferencesPanel(self.noteBook)
        self.panelsList.append(self.preferencesPanel)
        self.noteBook.add(self.preferencesPanel, text = "Preferences")
        
        # self.constraintFilesManagement.grid(row=0, column=0)
        # self.constraintSelectionManagement.grid(row=1, column=0)
        # self.NOEDrawingManagement.grid(row=2, column=0)
        # self.preferencesPanel.grid(row=0, column=0)
        # self.noteBook.setnaturalsize()

    def startGUI(self):
        self.createPanels()
        self.setDelegations()

    def setDelegations(self):
        self.NOEDrawingManagement.mainApp = self

    def getInfo(self):
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
