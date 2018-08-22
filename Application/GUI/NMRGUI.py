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
from Application.GUI.Panels.Preferences import PreferencesPanel
from Application.GUI.Panels.MainPanel import mainPanel
from Application.GUI.Panels.About import About


class NMRGUI(Tk.Tk):
    """
    """
    def __init__(self, root):
        """
        """
        Tk.Tk.__init__(self, root)
        self.title('PymolNMR')
        self.resizable(width=False, height=False)
        self.noteBook = ttk.Notebook(self)
        self.mainPanel = mainPanel(self.noteBook)
        self.preferencesPanel = PreferencesPanel(self.noteBook)
        self.About = About(self.noteBook)
        self.panelsList = list()

    def createPanels(self):
        """Main Frames (not IBM ;-)
        """

        self.noteBook.grid(row=0, column=0)

        self.noteBook.add(self.mainPanel, text="Main")
        self.panelsList.append(self.mainPanel)

        self.panelsList.append(self.preferencesPanel)
        self.noteBook.add(self.preferencesPanel, text="Preferences")

        self.noteBook.add(self.About, text="Help")

    def startGUI(self):
        """
        """
        self.createPanels()
        self.setDelegations()

    def setDelegations(self):
        """
        """
        self.mainPanel.NOEDrawing.mainGUI = self
        self.preferencesPanel.mainGUI = self
        self.mainPanel.fileSelection.mainGUI = self

    def getInfo(self):
        """
        """
        infos = dict()
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
