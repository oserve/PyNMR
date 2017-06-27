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

from Panels.ttkScrolledList import ScrolledList

from ..Core.MolecularViewerInterfaces import MolecularViewerInterface as MVI
from ..DataControllers import atomTypeListController, resiNumberListController


class NOEDataViewer(Tk.Toplevel):
    """
    """
    def __init__(self, dataController):
        """
        """
        Tk.Toplevel.__init__(self, class_='NOEDataViewer')
        self.labelFrame = ttk.LabelFrame(self, text='Select NOE residue and / or atom to see their counterparts :')
        self.NOEDataController = dataController
        self.title("NOE from " + dataController.name)
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self.labelFrame,
                                          textvariable=self.constraintSelectionText,
                                          justify=Tk.CENTER)
        self.resiListVarDisplayed = Tk.StringVar()
        self.resiScrollListDisplayed = ScrolledList(self.labelFrame,
                                                    listvariable=self.resiListVarDisplayed,
                                                    selectmode=Tk.EXTENDED, width=10)
        self.resiListDisplayedController = resiNumberListController()
        self.resiListVarPartner = Tk.StringVar()
        self.resiScrollListPartner = ScrolledList(self.labelFrame,
                                                  listvariable=self.resiListVarPartner,
                                                  selectmode=Tk.EXTENDED, width=10)
        self.resiListPartnerController = resiNumberListController()
        self.atomListVarDisplayed = Tk.StringVar()
        self.atomScrollListDisplayed = ScrolledList(self.labelFrame,
                                                    listvariable=self.atomListVarDisplayed,
                                                    width=10)
        self.atomListDisplayedController = atomTypeListController()
        self.atomListVarPartner = Tk.StringVar()
        self.atomScrollListPartner = ScrolledList(self.labelFrame,
                                                  listvariable=self.atomListVarPartner,
                                                  width=10)
        self.atomListPartnerController = atomTypeListController()
        self.NOEValues = dict()
        self.NOEValueLabels = dict()
        for valueType in ('constraint', 'min', 'plus', 'actual'):
            self.NOEValues[valueType] = Tk.DoubleVar()
            self.NOEValueLabels[valueType] = ttk.Label(self.labelFrame, textvariable=self.NOEValues[valueType], width=3)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.labelFrame.grid(row=0, column=0)
        self.labelConstraints.grid(row=0, column=0, columnspan=8)
        for index, labelName in enumerate(('1st Residue', '1st Atom', '2nd Residue', '2nd Atom')):
            ttk.Label(self.labelFrame, text=labelName).grid(row=1, column=index * 2, columnspan=2)
        self.resiScrollListDisplayed.grid(row=2, column=0, columnspan=2)
        self.atomScrollListDisplayed.grid(row=2, column=2, columnspan=2)
        self.resiScrollListPartner.grid(row=2, column=4, columnspan=2)
        self.atomScrollListPartner.grid(row=2, column=6, columnspan=2)
        columnPosition = 0
        for key, aLabel in self.NOEValueLabels.iteritems():
            aLabel.grid(row=3, column=columnPosition + 1)
            aLabel.state(['disabled'])
            ttk.Label(self.labelFrame, text=key).grid(row=3, column=columnPosition, sticky=Tk.W)
            columnPosition += 2

        self.resiScrollListDisplayed.bind('<<ListboxSelect>>', self.selectResidueDisplayed)
        self.atomScrollListDisplayed.bind('<<ListboxSelect>>', self.selectAtomDisplayed)
        self.resiScrollListPartner.bind('<<ListboxSelect>>', self.selectResiduePartner)
        self.fillResListDisplayed()
        self.constraintSelectionText.set(str(len(self.NOEDataController)) +
                                         " constraints used, involving " +
                                         str(len([residue for residue in self.NOEDataController.residuesList])) +
                                         " residues")
        self.atomScrollListPartner.bind('<<ListboxSelect>>', self.selectAtomPartner)
        self.resizable(width=False, height=False)

    def fillResListDisplayed(self):
        """
        """

        self.resiScrollListDisplayed.clear()
        self.atomScrollListDisplayed.clear()
        self.resiScrollListPartner.clear()
        self.atomScrollListPartner.clear()
        self.resiListDisplayedController.atomsList = self.NOEDataController.displayedAtoms
        self.resiListVarDisplayed.set(" ".join(self.resiListDisplayedController.resiNumberList))

    def selectResidueDisplayed(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        residue_selection = (w.get(resi_number_index) for resi_number_index in selection)

        self.atomListVarDisplayed.set('')
        self.atomListVarPartner.set('')
        self.resiListVarPartner.set('')

        self.switchLabelsState(['disabled'])

        selectedAtoms = list()
        for residue in residue_selection:
            selectedAtoms.extend(self.resiListDisplayedController.resiNumberList[residue.replace(" ", "\ ")])
        if len(selection) > 0:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListPartnerController.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVarPartner.set(" ".join(self.resiListPartnerController.resiNumberList))

            if len(selection) == 1:
                self.atomListDisplayedController.selectedAtoms = selectedAtoms
                self.atomListVarDisplayed.set(" ".join(self.atomListDisplayedController.atomTypeList))

            zoomSelect = MVI.createSelection(self.NOEDataController.structure, self.resiListPartnerController.atomsList+selectedAtoms)
            MVI.zoom(zoomSelect)

    def selectAtomDisplayed(self, evt):
        """
        """
        self.switchLabelsState(['disabled'])
        w = evt.widget
        selection = w.curselection()
        atomType_selection = (w.get(atom_number_index) for atom_number_index in selection)
        self.resiListVarPartner.set('')
        self.atomListVarPartner.set('')

        selectedAtoms = [self.atomListDisplayedController.atomTypeList[atomType] for atomType in atomType_selection]

        if len(selection) == 1:
            self.NOEDataController.setSelectedAtoms(selectedAtoms[0])
            self.resiListPartnerController.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVarPartner.set(" ".join(self.resiListPartnerController.resiNumberList))
            zoomSelect = MVI.createSelection(self.NOEDataController.structure, self.resiListPartnerController.atomsList+selectedAtoms[0])
            MVI.zoom(zoomSelect)

    def selectResiduePartner(self, evt):
        """
        """
        self.switchLabelsState(['disabled'])
        w = evt.widget
        selection = w.curselection()

        if len(selection) == 1:
            self.atomListVarPartner.set('')

            if len(self.atomScrollListDisplayed.curselection()) == 1:

                partnerResidue_selection = (w.get(resi_number_index) for resi_number_index in selection)

                selectedPartnerAtoms = [self.resiListPartnerController.resiNumberList[residue.replace(" ", "\ ")] for residue in partnerResidue_selection]

                self.atomListPartnerController.selectedAtoms = selectedPartnerAtoms[0]
                self.atomListVarPartner.set(" ".join(self.atomListPartnerController.atomTypeList))
                zoomSelect = MVI.createSelection(self.NOEDataController.structure, self.NOEDataController.selectedAtoms+selectedPartnerAtoms[0])
                MVI.zoom(zoomSelect)

    def selectAtomPartner(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        atomType_selection = (w.get(atom_number_index) for atom_number_index in selection)
        selectedPartnerAtoms = [self.atomListPartnerController.atomTypeList[atomType] for atomType in atomType_selection]

        if len(selection) == 1:
            zoomSelect = MVI.createSelection(self.NOEDataController.structure, selectedPartnerAtoms[0]+self.NOEDataController.selectedAtoms)
            MVI.zoom(zoomSelect)

            constraintValues = self.NOEDataController.constraintValueForAtoms(selectedPartnerAtoms[0]+self.NOEDataController.selectedAtoms)
            if constraintValues:
                for key, value in self.NOEValues.iteritems():
                    value.set(round(float(constraintValues[0][0][key]), 1))
                self.switchLabelsState(['!disabled'])
                style = ttk.Style()
                if constraintValues[0][1] is 'unSatisfied':
                    style.configure("Red.TLabel", foreground="red")
                    self.NOEValueLabels['constraint'].configure(style="Red.TLabel")
                if constraintValues[0][1] is 'Satisfied':
                    style.configure("Green.TLabel", foreground="green")
                    self.NOEValueLabels['constraint'].configure(style="Green.TLabel")

    def switchLabelsState(self, state):
        """
        """
        if 'disabled' in state:
            for value in self.NOEValues.itervalues():
                value.set(0)
        for aLabel in self.NOEValueLabels.itervalues():
            aLabel.state(state)
