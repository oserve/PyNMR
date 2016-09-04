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
import ScrolledList


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
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self, textvariable=self.constraintSelectionText)
        self.resiList_1 = Tk.StringVar()
        self.resiScrollList_1 = ScrolledList.ScrolledList(self, listvariable=self.resiList_1, selectmode=Tk.EXTENDED)
        self.resiList_2 = Tk.StringVar()
        self.resiScrollList_2 = ScrolledList.ScrolledList(self, listvariable=self.resiList_2, selectmode=Tk.EXTENDED)
        self.atomList_1 = Tk.StringVar()
        self.atomScrollList_1 = ScrolledList.ScrolledList(self, listvariable=self.atomList_1, selectmode=Tk.EXTENDED)
        self.atomList_2 = Tk.StringVar()
        self.atomScrollList_2 = ScrolledList.ScrolledList(self, listvariable=self.atomList_2, selectmode=Tk.EXTENDED)
        self.mainGUI = ""  # Must be set at run time
        self.NMRCommands = ""  # Must be set by application at run time
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.sticksButton.grid(row=0, column=0)
        self.densityButton.grid(row=0, column=1)
        self.cleanButton.grid(row=0, column=2)
        self.labelConstraints.grid(row=1, column=0, columnspan=3)
        ttk.Label(self, text='1st Residue').grid(row=2, column=0)
        self.resiScrollList_1.grid(row=3, column=0)
        ttk.Label(self, text='1st Atom').grid(row=2, column=1)
        self.atomScrollList_1.grid(row=3, column=1)
        ttk.Label(self, text='2nd Residue').grid(row=2, column=2)
        self.resiScrollList_2.grid(row=3, column=2)
        ttk.Label(self, text='2nd Atom').grid(row=2, column=3)
        self.atomScrollList_2.grid(row=3, column=3)
        self.constraintSelectionText.set('')
        self.resiScrollList_1.listbox.bind('<<ListboxSelect>>',
                                          self.selectResidue_1)
        self.atomScrollList_1.listbox.bind('<<ListboxSelect>>',
                                           self.selectAtom_1)
        self.resiScrollList_2.listbox.bind('<<ListboxSelect>>',
                                           self.selectResidue_2)

    def showSticks(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["structure"],
                                                    infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            results = self.NMRCommands.showSticks(infos["constraintFile"],
                                                  infos["structure"],
                                                  infos["colors"],
                                                  infos["radius"],
                                                  infos["UnSatisfactionMarker"],
                                                  infos["SatisfactionMarker"])

            self.constraintSelectionText.set(str(results['numberOfConstraints']) +
                                             " constraints used, involving " +
                                             str(results["numberOfResidues"]) +
                                             " residues")
            self.fillResList1()

    def showDensity(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["structure"],
                                                    infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            results = self.NMRCommands.showNOEDensity(infos["constraintFile"],
                                                      infos["structure"],
                                                      infos["gradient"])

            self.constraintSelectionText.set(str(results['numberOfConstraints']) +
                                             " constraints used, involving " +
                                             str(results["numberOfResidues"]) +
                                             " residues")
            self.fillResList1()

# All the following methods and related widgets would be better suited into a
# a separated window
# Also, they should interact with 3D representation through MVI.select()

    def fillResList1(self):
        """
        """
        managerName = self.mainGUI.getInfo()["constraintFile"]

        self.resiScrollList_1.clear()
        self.atomScrollList_1.clear()
        self.resiScrollList_2.clear()
        self.atomScrollList_2.clear()

        self.resiList_1.set(" ".join(self.NMRCommands.getDisplayedResiduesList(managerName)))

    def selectResidue_1(self, evt):
        """
        """
        managerName = self.mainGUI.getInfo()["constraintFile"]
        w = evt.widget
        selection = w.curselection()
        residue_selection = [w.get(resi_number_index) for resi_number_index in selection]

        self.atomList_1.set('')
        self.atomList_2.set('')
        self.resiList_2.set('')
        if len(selection) > 0:
            self.resiList_2.set(" ".join(str(residueNumber) for residueNumber in self.NMRCommands.getSecondResiduesList(managerName, residue_selection)))
        if len(selection) == 1:
            self.atomList_1.set(" ".join(self.NMRCommands.getAtomsForResidue(managerName, residue_selection[0])))

    def selectAtom_1(self, evt):
        """
        """
        managerName = self.mainGUI.getInfo()["constraintFile"]
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        self.atomList_2.set('')
        residue_number_indice = self.resiScrollList_1.listbox.curselection()[0]
        residue_number = [int(resi.replace("'","").strip()) for index, resi in enumerate(self.resiList_1.get().strip("()").split(',')) if index == residue_number_indice]
        atomSelection = [{"resi_number": residue_number[0], "resi_type": atomType} for atomType in atomType_selection]

        self.resiList_2.set(" ".join(str(residueNumber) for residueNumber in self.NMRCommands.getSecondResiduesForAtoms(managerName, atomSelection)))

    def selectResidue_2(self, evt):
        """
        """
        managerName = self.mainGUI.getInfo()["constraintFile"]
        w = evt.widget
        selection = w.curselection()
        if len(selection) == 1:
            self.atomList_2.set('')
            residue2_selection = [w.get(resi_number_index) for resi_number_index in selection]
            atom1ListSelection = self.atomScrollList_1.listbox.curselection()
            if len(atom1ListSelection) == 1:
                atom1_Type_indice = atom1ListSelection[0]
                atom1_Type = [atomType.replace("'","").strip() for index, atomType in enumerate(self.atomList_1.get().strip("()").split(',')) if index == atom1_Type_indice]


                residue1_number_indice = self.resiScrollList_1.listbox.curselection()[0]
                residue1_number = [int(resi.replace("'","")) for index, resi in enumerate(self.resiList_1.get().strip("()").split(',')) if index == residue1_number_indice]

                atomSelection = {"resi_number": residue1_number[0], "resi_type": atom1_Type[0]}

                self.atomList_2.set(" ".join(self.NMRCommands.getSecondAtomsinResidueForAtom(managerName, residue2_selection[0], atomSelection)))

    def cleanAll(self):
        """Remove all displayed sticks
        """
        self.resiScrollList_1.clear()
        self.atomScrollList_1.clear()
        self.resiScrollList_2.clear()
        self.atomScrollList_2.clear()

        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen(infos["constraintFile"])
        self.constraintSelectionText.set("0 constraints used.")

    def infoCheck(self, infos):
        """
        """
        check = 1
        for item in infos.values():
            if item == "":
                check = 0
                break
        return check
