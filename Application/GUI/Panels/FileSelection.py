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
import tkSimpleDialog
import tkFileDialog

import Tkinter as Tk
import ttk
from ScrolledList import ScrolledList


class FileSelectionPanel(ttk.LabelFrame):
    """This panel allows to import constraint file
    into the Core. Also it allows the selection of the file
    for the following calculations.
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text="Constraints Files")
        self.constraintsFileList = Tk.StringVar()
        self.infoLabelString = Tk.StringVar()
        self.loadFileButton = ttk.Button(self, text=u"Load file",
                                        command=self.loadFile)
        self.removeFileButton = ttk.Button(self, text=u"Remove file",
                                          command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        self.downloadButton = ttk.Button(self, text=u"Download \nfrom PDB",
                                        command=self.downloadRestraintFileWin)
        self.saveButton = ttk.Button(self, text=u'Save File',
                                     command=self.saveFile)
        self.infoLabel = ttk.Label(self, textvariable=self.infoLabelString)
        self.selectedFile = ""
        self.widgetCreation()
        self.NMRCommands = ""  # Must be set by application at run time
        self.mainGUI = ""  # Must be set at run time

    def widgetCreation(self):
        """
        """
        self.constraintsList.listbox.exportselection = 0
        self.constraintsList.grid(row=0, column=1, rowspan=4)
        self.loadFileButton.grid(row=0, column=0)
        self.removeFileButton.grid(row=1, column=0)
        self.downloadButton.grid(row=2, column=0)
        self.saveButton.grid(row=3, column=0)
        self.infoLabel.grid(row=4, column=0, columnspan=2)
        self.constraintsList.listbox.bind('<<ListboxSelect>>',
                                          self.onStructureSelect)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint file")
        if filename is not None:
            self.NMRCommands.loadNOE(filename)
            self.updateFilelist()

    def updateFilelist(self):
        """
        """
        managerList = ""
        for item in self.NMRCommands.ManagersList.keys():
            managerList = managerList + " " + item
        self.constraintsFileList.set(managerList)

    def removeFile(self):
        """
        """
        toRemove = self.selectedFile
        if toRemove:
            del self.NMRCommands.ManagersList[toRemove]
        self.updateFilelist()

    def saveFile(self):
        """
        """
        toSave = self.selectedFile
        if toSave:
            filename = tkFileDialog.asksaveasfilename(
                title="Save constraint file as", initialfile=toSave)
            if filename is not None:
                self.NMRCommands.saveConstraintsFile(toSave, filename)

    def downloadRestraintFileWin(self):
        """
        """
        pdbCode = tkSimpleDialog.askstring('PDB NMR Restraints',
                                           'Please enter a 4-digit pdb code:',
                                           parent=self)
        if pdbCode:
            infos = self.mainGUI.getInfo()
            self.NMRCommands.downloadFromPDB(pdbCode, infos["urlPDB"])
            self.updateFilelist()

    def onStructureSelect(self, evt):
        """
        """
        # Note here that Tkinter passes an event object
        w = evt.widget
        selection = w.curselection()
        if len(selection) == 1:
            index = int(selection[0])
            self.selectedFile = w.get(index)
            self.infoLabelString.set("Contains " +
                                     str(len(self.NMRCommands.ManagersList[self.selectedFile])) +
                                     " Constraints (" + self.NMRCommands.ManagersList[self.selectedFile].format + ")")

    def getInfo(self):
        """
        """
        if self.selectedFile:
            return {"constraintFile": self.selectedFile}
        else:
            return {"constraintFile": ""}
