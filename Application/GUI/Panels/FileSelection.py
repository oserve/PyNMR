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

import tkFileDialog
from Panel import Panel
import Tkinter as Tk
from ScrolledList import ScrolledList
import urllib2
import zipfile
import os

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
        self.loadFileButton = Tk.Button(self, text="Load file",
                                        command=self.loadFile)
        self.removeFileButton = Tk.Button(self, text="Remove selected file",
                                          command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        self.downloadButton = Tk.Button(self, text="Download from PDB",
                                        command=self.downloadRestraintFileWin)
        self.PDBCode = Tk.StringVar()
        self.widgetCreation()
        self.NMRCommands = ""  #Must be set by application at run time

    def widgetCreation(self):
        """
        """
        self.constraintsList.listbox.exportselection = 0
        self.constraintsList.grid(row=0, column=1, rowspan=2)
        position = 0
        for constraintType in self.constraintsDefTypes:
            Tk.Radiobutton(self, text=constraintType,
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
        #self.constraintsList.setlist(self.NMRCommands.ManagersList.keys())

    def fileList(self):
        """
        """
        return self.constraintsFileList.get().rstrip(')').lstrip('(').replace("'","").split(',')

    def selectedFile(self):
        """
        """
        if len(self.constraintsList.listbox.curselection()):
            return self.fileList()[self.constraintsList.listbox.curselection()[0]]

    def downloadRestraintFileWin(self):
        """
        """
        downloadWin = Tk.Toplevel(self)
        downloadWin.title="Download Restraint File ..."
        Tk.Label(downloadWin, text="PDB Code :").grid(row=0, column=0)
        Tk.Entry(downloadWin, textvariable=self.PDBCode).grid(row=0, column=1)
        Tk.Button(downloadWin, text="Download from PDB",
                  command=self.downloadFileFromPDB).grid(row=1, column=0)
        Tk.Button(downloadWin, text="Cancel").grid(row=1, column=1)

    def downloadFileFromPDB(self):
        """
        """
        url = "http://www.rcsb.org/ pdb/files/"+self.PDBCode.get().upper()+".mr.gz"

        file_name = url.split('/')[-1]
        PDBurl = urllib2.urlopen(url)
        downloadedFile = open(file_name, 'wb')
        meta = PDBurl.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            FileBuffer = PDBurl.read(block_sz)
            if not FileBuffer:
                break

            file_size_dl += len(FileBuffer)
            downloadedFile.write(FileBuffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        zippedFile = zipfile.ZipFile(downloadedFile)
        for name in zippedFile.namelist():
            outfile = open(name, 'wb')
            outfile.write(zippedFile.read(name))
            outfile.close()
        downloadedFile.close()

        constraintDefinition = "CYANA"
        restraintFile = open(self.PDBCode.get().upper()+".mr")
        for line in restraintFile:
            if line.upper().find('ASSI') > 0:
                constraintDefinition = "CNS"
                break
        restraintFile.close()

        self.NMRCommands.loadNOE(self.PDBCode.get().upper() + ".mr", constraintDefinition)
        self.updateFilelist()

        for name in zippedFile.namelist():
            os.remove(name)
        os.remove(downloadedFile)

    def getInfo(self):
        """
        """
        if len(self.fileList()):
            return {"constraintFile": self.selectedFile()}
        else:
            return {"constraintFile": ""}
