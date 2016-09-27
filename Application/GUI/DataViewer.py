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
from DataControllers import atomTypeList, resiNumberList


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
        self.resiListVarDisplayed = Tk.StringVar()
        self.resiScrollListDisplayed = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiListVarDisplayed,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.resiListVarPartner = Tk.StringVar()
        self.resiScrollListPartner = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.resiListVarPartner,
                                                          selectmode=Tk.EXTENDED,
                                                          width=10)
        self.atomListVarDisplayed = Tk.StringVar()
        self.atomScrollListDisplayed = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomListVarDisplayed,
                                                          width=10)
        self.atomListVarPartner = Tk.StringVar()
        self.atomScrollListPartner = ScrolledList.ScrolledList(self.labelFrame,
                                                          listvariable=self.atomListVarPartner,
                                                          width=10)

        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.labelFrame.grid(row=0, column=0)
        self.labelConstraints.grid(row=0, column=0, columnspan=4)
        ttk.Label(self.labelFrame, text='1st Residue').grid(row=1, column=0)
        self.resiScrollListDisplayed.grid(row=2, column=0)
        ttk.Label(self.labelFrame, text='1st Atom').grid(row=1, column=1)
        self.atomScrollListDisplayed.grid(row=2, column=1)
        ttk.Label(self.labelFrame, text='2nd Residue').grid(row=1, column=2)
        self.resiScrollListPartner.grid(row=2, column=2)
        ttk.Label(self.labelFrame, text='2nd Atom').grid(row=1, column=3)
        self.atomScrollListPartner.grid(row=2, column=3)
        self.resiScrollListDisplayed.listbox.bind('<<ListboxSelect>>',
                                           self.selectResidueDisplayed)
        self.atomScrollListDisplayed.listbox.bind('<<ListboxSelect>>',
                                           self.selectAtomDisplayed)
        self.resiScrollListPartner.listbox.bind('<<ListboxSelect>>',
                                           self.selectResiduePartner)
        self.fillResListDisplayed()
        self.constraintSelectionText.set(str(len(self.NOEDataController)) +
                                         " constraints used, involving " +
                                         str(len([residue for residue in self.NOEDataController.getResiduesList()])) +
                                         " residues")

    def fillResListDisplayed(self):
        """
        """

        self.resiScrollListDisplayed.clear()
        self.atomScrollListDisplayed.clear()
        self.resiScrollListPartner.clear()
        self.atomScrollListPartner.clear()

        self.resiListVarDisplayed.set(" ".join(resiNumberList(self.NOEDataController.displayedAtoms)))

    def selectResidueDisplayed(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        residue_selection = [w.get(resi_number_index) for resi_number_index in selection]

        self.atomListVarDisplayed.set('')
        self.atomListVarPartner.set('')
        self.resiListVarPartner.set('')

        selectedAtoms = list()
        for residue in residue_selection:
            selectedAtoms.extend(resiNumberList(self.NOEDataController.displayedAtoms)[residue.replace(" ", "\ ")])
        if len(selection) > 0:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListVarPartner.set(" ".join(resiNumberList(self.NOEDataController.partnerAtoms)))
        if len(selection) == 1:
            self.atomListVarDisplayed.set(" ".join(atomTypeList(selectedAtoms)))

    def selectAtomDisplayed(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        self.resiListVarPartner.set('')
        self.atomListVarPartner.set('')

        selectedAtoms = list()
        for atomType in atomType_selection:
            selectedAtoms.extend(atomTypeList(self.NOEDataController.displayedAtoms)[atomType])

        if len(selection) == 1:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListVarPartner.set(" ".join(resiNumberList(self.NOEDataController.partnerAtoms)))

    def selectResiduePartner(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()

        if len(selection) == 1:
            self.atomListVarPartner.set('')

            if len(self.atomScrollListDisplayed.listbox.curselection()) == 1:

                residue2_selection = [w.get(resi_number_index) for resi_number_index in selection]

                selectedAtoms = list()
                for residue in residue2_selection:
                    selectedAtoms.extend(resiNumberList(self.NOEDataController.partnerAtoms)[residue.replace(" ", "\ ")])

                self.NOEDataController.setSelectedAtoms(selectedAtoms)

                self.atomListVarPartner.set(" ".join(atomTypeList(selectedAtoms)))
