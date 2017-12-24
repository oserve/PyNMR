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
from Application.DataControllers import atomTypeListController, resiNumberListController
from Application.Core.MolecularViewerInterfaces import MolecularViewerInterface as MVI


class NOEViewController(object):
    """
    """
    def __init__(self, dataController, NOEView, NOETableView):
        self.NOEDataController = dataController
        self.listsControllers = (resiNumberListController(), atomTypeListController(), resiNumberListController(), atomTypeListController())
        self.NOETableView = NOETableView
        self.NOEView = NOEView

    def on_before_widgetCreation(self, *args, **kwargs):
        """
        """
        for atom in self.NOEDataController.displayedAtoms:
            self.listsControllers[0].addAtom(atom)

    def on_after_widgetCreation(self, *args, **kwargs):
        """
        """
        self.NOEView.setTitle(len(self.NOEDataController), len([residue for residue in self.NOEDataController.residuesList]))

    def on_after_changeSelection(self, *args, **kwargs):
        """
        """
        if self.NOETableView.selectedList == 0:
            self.selectResidueDisplayed()
        if self.NOETableView.selectedList == 1:
            self.selectAtomDisplayed()
        if self.NOETableView.selectedList == 2:
            self.selectResiduePartner()
        if self.NOETableView.selectedList == 3:
            self.selectAtomPartner()

    def selectResidueDisplayed(self):
        """
        """
        self.NOEView.setLabelsState(['disabled'])
        for index_controller in xrange(1, len(self.listsControllers)):
            self.listsControllers[index_controller].clear()

        if self.NOETableView.selectedRows[0]:
            selectedAtoms = list()
            for resi_number_index in self.NOETableView.selectedRows[0]:
                selectedAtoms.extend(self.listsControllers[0].values()[resi_number_index])
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            for atom in self.NOEDataController.partnerAtoms:
                self.listsControllers[2].addAtom(atom)

            if len(self.NOETableView.selectedRows[0]) == 1:
                for atom in selectedAtoms:
                    self.listsControllers[1].addAtom(atom)

            MVI.zoom(self.NOEDataController.structure, self.NOEDataController.partnerAtoms+selectedAtoms)

    def selectAtomDisplayed(self):
        """
        """
        self.NOEView.setLabelsState(['disabled'])
        for index_controller in xrange(2, len(self.listsControllers)):
            self.listsControllers[index_controller].clear()

        if len(self.NOETableView.selectedRows[1]) == 1:
            selectedAtoms = [self.listsControllers[1].values()[atomNumber] for atomNumber in self.NOETableView.selectedRows[1]]
            self.NOEDataController.setSelectedAtoms(selectedAtoms[0])
            for atom in self.NOEDataController.partnerAtoms:
                self.listsControllers[2].addAtom(atom)
            MVI.zoom(self.NOEDataController.structure, self.NOEDataController.partnerAtoms+selectedAtoms[0])

    def selectResiduePartner(self):
        """
        """
        selection = self.NOETableView.selectedRows[2]

        if len(selection) == 1:
            if len(self.NOETableView.selectedRows[1]) == 1:
                selectedPartnerAtoms = self.listsControllers[2].values()[selection[0]]
                self.listsControllers[3].addAtom(selectedPartnerAtoms[0])
                MVI.zoom(self.NOEDataController.structure, self.NOEDataController.selectedAtoms+selectedPartnerAtoms)

    def selectAtomPartner(self):
        """
        """
        selection = self.NOETableView.selectedRows[3]
        partnerAtoms = self.listsControllers[3].values()

        if len(selection) == 1:
            MVI.zoom(self.NOEDataController.structure, partnerAtoms[0]+self.NOEDataController.selectedAtoms)

            constraintValues = self.NOEDataController.constraintValueForAtoms(partnerAtoms[0]+self.NOEDataController.selectedAtoms)
            if constraintValues:
                self.NOEView.setLabelsState(['!disabled'])
                self.NOEView.setLabelValues(*constraintValues[0])

    def valuesForColumn(self, index):
        """
        """
        return self.listsControllers[index]
    