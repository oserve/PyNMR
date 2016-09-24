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
from DataControllers.resiNumberListController import resiNumberListController
from DataControllers.atomTypeListController import atomTypeListController


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
        self.resiListVar_1 = Tk.StringVar()
        self.resiScrollList_1 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiListVar_1,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.resiListController_1 = resiNumberListController(dataController.displayedAtoms)
        self.resiListVar_2 = Tk.StringVar()
        self.resiScrollList_2 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiListVar_2,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.resiListController_2 = resiNumberListController(dataController.partnerAtoms)
        self.atomListVar_1 = Tk.StringVar()
        self.atomScrollList_1 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomListVar_1,
                                                          width=10)
        self.atomListController_1 = atomTypeListController()
        self.atomListVar_2 = Tk.StringVar()
        self.atomScrollList_2 = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomListVar_2,
                                                          width=10)
        self.atomListController_2 = atomTypeListController()

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

        self.resiListVar_1.set(" ".join(self.resiListController_1.resiNumberList))

    def selectResidue_1(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        residue_selection = [w.get(resi_number_index) for resi_number_index in selection]

        self.atomListVar_1.set('')
        self.atomListVar_2.set('')
        self.resiListVar_2.set('')
        selectedAtoms = list()
        for residue in residue_selection:
            selectedAtoms.extend(self.resiListController_1.resiNumberList[residue.replace(" ", "\ ")])
        if len(selection) > 0:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListController_2.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVar_2.set(" ".join(self.resiListController_2.resiNumberList))
        if len(selection) == 1:
            self.atomListController_1.selectedAtoms = selectedAtoms
            self.atomListVar_1.set(" ".join(self.atomListController_1.atomTypeList))

    def selectAtom_1(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        self.resiListVar_2.set('')
        self.atomListVar_2.set('')

        selectedAtoms = list()
        for atomType in atomType_selection:
            selectedAtoms.extend(self.atomListController_1.atomTypeList[atomType])

        if len(selection) == 1:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListController_2.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVar_2.set(" ".join(self.resiListController_2.resiNumberList))

    def selectResidue_2(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()

        if len(selection) == 1:
            self.atomListVar_2.set('')

            if len(self.atomScrollList_1.listbox.curselection()) == 1:

                residue2_selection = [w.get(resi_number_index) for resi_number_index in selection]

                selectedAtoms = list()
                for residue in residue2_selection:
                    selectedAtoms.extend(self.resiListController_2.resiNumberList[residue.replace(" ", "\ ")])

                self.NOEDataController.setSelectedAtoms(selectedAtoms)
                self.atomListController_2.selectedAtoms = selectedAtoms

                self.atomListVar_2.set(" ".join(self.atomListController_2.atomTypeList))

    @staticmethod
    def listFromTkString(TkString):
        """
        """
        return (item.replace("'","").strip() for item in TkString.get().strip("()").split(','))
