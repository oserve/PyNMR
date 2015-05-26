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

from os import path
import tkFileDialog
from Panel import Panel
import Tkinter as Tk
from ScrolledList import ScrolledList

class FileSelectionPanel(Panel):
    """This panel allows to import constraint file
    into the Core. Also it allows the selection of the file
    for the following calculations.
    """
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Constraints Files")
        self.constraintsDefType = Tk.StringVar()
        self.constraintsDefTypes = ["CNS/XPLOR", "CYANA/DYANA"]
        self.constraintsDefType.set(self.constraintsDefTypes[0])
        self.constraintsFileList = Tk.StringVar()
        self.widgetCreation()
        self.NMRCommands = ""  #Must be set by application at run time

    def widgetCreation(self):
        """
        """
        self.loadFileButton = Tk.Button(self, text="Load file",
                                        command=self.loadFile)
        self.removeFileButton = Tk.Button(self, text="Remove selected file",
                                          command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        #self.constraintsList.listbox.listvariable = self.constraintsFileList
        self.constraintsList.listbox.exportselection = 0
        self.constraintsList.grid(row=0, column=0, columnspan=2)
        position = 0
        for constraintType in self.constraintsDefTypes:
            Tk.Radiobutton(self, text=constraintType,
                           variable=self.constraintsDefType,
                           value=constraintType).grid(row=1, column=position)
            position = position +1
        self.loadFileButton.grid(row=2, column=0)
        self.removeFileButton.grid(row=2, column=1)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint " + self.constraintsDefType.get() + " file ")
        constraintType = ""
        if self.constraintsDefType.get() == "CNS/XPLOR":
            constraintDefinition = "CNS"
        else:
            constraintDefinition = "CYANA"
        if filename:
            self.NMRCommands.loadNOE(filename, constraintDefinition)
            self.updateFilelist()
            #self.constraintsList.setvalue(path.basename(filename))

    def updateFilelist(self):
        """
        """
        self.constraintsFileList.set(self.NMRCommands.ManagersList.keys())

    def removeFile(self):
        """
        """
        toRemove = self.constraintsList.listbox.get()
        if toRemove:
            for manager in toRemove:
                del self.NMRCommands.ManagersList[manager]
        self.updateFilelist()
        #self.constraintsList.setlist(self.NMRCommands.ManagersList.keys())

    def getInfo(self):
        """
        """
        if len(self.constraintsFileList):
            return {"constraintFile": self.constraintsList.listbox.get()[0]}
        else:
            return {"constraintFile": ""}
