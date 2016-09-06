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
from Panels import ScrolledList

class NOEDataViewer(Tk.Toplevel):
    """
    """
    def __init__(self, dataController):
        """
        """
        Tk.Toplevel.__init__(self)
        self.labelFrame = ttk.LabelFrame(self, text='Select NOE residue and / or atom to see their counterparts :')
        self.NOEDataController = dataController
        self.title("NOE from " + dataController.name)
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self.labelFrame,
                                          textvariable=self.constraintSelectionText,
                                          justify=Tk.CENTER)
        self.resiList_1 = Tk.StringVar()
        self.resiScrollList_1 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiList_1,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.resiList_2 = Tk.StringVar()
        self.resiScrollList_2 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiList_2,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.atomList_1 = Tk.StringVar()
        self.atomScrollList_1 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomList_1,
                                                          width=10)
        self.atomList_2 = Tk.StringVar()
        self.atomScrollList_2 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomList_2,
                                                          width=10)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.labelFrame.grid(row=0, column=0)
        self.labelConstraints.grid(row=0, column=0, columnspan=4)
        ttk.Label(self.labelFrame, text='1st Residue').grid(row=1, column=0)
        self.resiScrollList_1.grid(row=2, column=0)
        ttk.Label(self.labelFrame, text='1st Atom').grid(row=1, column=1)
        self.atomScrollList_1.grid(row=2, column=1)
        ttk.Label(self.labelFrame, text='2nd Residue').grid(row=1, column=2)
        self.resiScrollList_2.grid(row=2, column=2)
        ttk.Label(self.labelFrame, text='2nd Atom').grid(row=1, column=3)
        self.atomScrollList_2.grid(row=2, column=3)
        self.resiScrollList_1.listbox.bind('<<ListboxSelect>>',
                                           self.selectResidue_1)
        self.atomScrollList_1.listbox.bind('<<ListboxSelect>>',
                                           self.selectAtom_1)
        self.resiScrollList_2.listbox.bind('<<ListboxSelect>>',
                                           self.selectResidue_2)
        self.fillResList1()
        self.constraintSelectionText.set(str(len(self.NOEDataController)) +
                                         " constraints used, involving " +
                                         str(len([residue for residue in self.NOEDataController.getResiduesList()])) +
                                         " residues")


    def fillResList1(self):
        """
        """

        self.resiScrollList_1.clear()
        self.atomScrollList_1.clear()
        self.resiScrollList_2.clear()
        self.atomScrollList_2.clear()

        self.resiList_1.set(" ".join(self.NOEDataController.getDisplayedResiduesList()))

    def selectResidue_1(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        residue_selection = [w.get(resi_number_index) for resi_number_index in selection]

        self.atomList_1.set('')
        self.atomList_2.set('')
        self.resiList_2.set('')
        if len(selection) > 0:
            self.resiList_2.set(" ".join(str(residueNumber) for residueNumber in self.NOEDataController.getSecondResiduesList(residue_selection)))
        if len(selection) == 1:
            self.atomList_1.set(" ".join(self.NOEDataController.getAtomsForResidue(residue_selection[0])))

    def selectAtom_1(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        self.atomList_2.set('')
        residue_number_indice = self.resiScrollList_1.listbox.curselection()[0]
        residue_number = [int(resi) for index, resi in enumerate(self.listFromTkString(self.resiList_1)) if index == residue_number_indice]
        atomSelection = [{"resi_number": residue_number[0], "resi_type": atomType} for atomType in atomType_selection]

        self.resiList_2.set(" ".join(str(residueNumber) for residueNumber in self.NOEDataController.getSecondResiduesForAtoms(atomSelection)))

    def selectResidue_2(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        if len(selection) == 1:
            self.atomList_2.set('')
            residue2_selection = [w.get(resi_number_index) for resi_number_index in selection]
            atom1ListSelection = self.atomScrollList_1.listbox.curselection()
            if len(atom1ListSelection) == 1:
                atom1_Type_indice = atom1ListSelection[0]
                atom1_Type = [atomType for index, atomType in enumerate(self.listFromTkString(self.atomList_1)) if index == atom1_Type_indice]

                residue1_number_indice = self.resiScrollList_1.listbox.curselection()[0]
                residue1_number = [int(resi) for index, resi in enumerate(self.listFromTkString(self.resiList_1)) if index == residue1_number_indice]

                atomSelection = {"resi_number": residue1_number[0], "resi_type": atom1_Type[0]}

                self.atomList_2.set(" ".join(self.NOEDataController.getSecondAtomsinResidueForAtom(residue2_selection[0], atomSelection)))

    @staticmethod
    def listFromTkString(TkString):
        """
        """
        return (item.replace("'","").strip() for item in TkString.get().strip("()").split(','))
