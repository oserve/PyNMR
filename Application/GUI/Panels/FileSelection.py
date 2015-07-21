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
from Panel import Panel
import Tkinter as Tk
import ttk
from ScrolledList import ScrolledList
import urllib2
import shutil
import gzip
import os
import sys


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
        self.loadFileButton = ttk.Button(self, text="Load file",
                                        command=self.loadFile)
        self.removeFileButton = ttk.Button(self, text="Remove selected file",
                                          command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        self.downloadButton = ttk.Button(self, text="Download from PDB",
                                        command=self.downloadRestraintFileWin)
        self.widgetCreation()
        self.NMRCommands = ""  # Must be set by application at run time

    def widgetCreation(self):
        """
        """
        self.constraintsList.listbox.exportselection = 0
        self.constraintsList.grid(row=0, column=1, rowspan=2)
        position = 0
        for constraintType in self.constraintsDefTypes:
            ttk.Radiobutton(self, text=constraintType,
                           variable=self.constraintsDefType,
                           value=constraintType).grid(row=position, column=0)
            position = position + 1
        self.loadFileButton.grid(row=2, column=0)
        self.removeFileButton.grid(row=2, column=1)
        self.downloadButton.grid(row=3, column=0, columnspan=2)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint " + self.constraintsDefType.get() + " file")
        constraintType = ""
        if self.constraintsDefType.get() == "CNS/XPLOR":
            constraintDefinition = "CNS"
        else:
            constraintDefinition = "CYANA"
        if filename:
            self.NMRCommands.loadNOE(filename, constraintDefinition)
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
        toRemove = self.selectedFile()
        if toRemove:
            del self.NMRCommands.ManagersList[toRemove]
        self.updateFilelist()

    def fileList(self):
        """
        """
        return self.constraintsFileList.get().rstrip(')').lstrip('(').replace("'", "").split(',')

    def selectedFile(self):
        """
        """
        if len(self.constraintsList.listbox.curselection()):
            return self.fileList()[self.constraintsList.listbox.curselection()[0]]

    def downloadRestraintFileWin(self):
        """
        """
        pdbCode = tkSimpleDialog.askstring('PDB NMR Restraints',
                                       'Please enter a 4-digit pdb code:',
                                       parent=self)
        if pdbCode:
            self.downloadFileFromPDB(pdbCode)


    def downloadFileFromPDB(self, pdbCode):
        """
        """
        url = "ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/"
        fileName = pdbCode.lower()+".mr"
        zippedFileName = fileName+".gz"
        try:
            restraintFileRequest = urllib2.urlopen(urllib2.Request(url+zippedFileName))
            with open(zippedFileName, 'wb') as f:
                shutil.copyfileobj(restraintFileRequest, f)
            restraintFileRequest.close()
            zippedFile = gzip.open(zippedFileName, 'rb')
            decodedFile = zippedFile.read()
            restraintFile = open(fileName, 'w')
            restraintFile.write(decodedFile)
            zippedFile.close()
            os.remove(zippedFileName)
            constraintDefinition = "CYANA"
            restraintFile.close()
            restraintFile = open(fileName, 'r')
            for line in restraintFile:
                if line.upper().find('ASSI') > -1:
                    constraintDefinition = "CNS"
                    break
            restraintFile.close()
            self.NMRCommands.loadNOE(fileName, constraintDefinition)
            self.updateFilelist()
            os.remove(fileName)
        except:
            sys.stderr.write("Can not download "+pdbCode+" NMR Restraints file from PDB.\n")

    def getInfo(self):
        """
        """
        if len(self.fileList()):
            return {"constraintFile": self.selectedFile()}
        else:
            return {"constraintFile": ""}
