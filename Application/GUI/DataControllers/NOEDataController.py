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

class NOEDataController(object):
    """
    """

    def __init__(self, dataSource, aManagerName):
        """
        """
        self.dataSource = dataSource
        self.name = aManagerName
        self.manager = dataSource.ManagersList.get(aManagerName, "").intersection(dataSource.displayedConstraints)

    def __len__(self):
        """
        """
        return len(self.manager)

    def getDisplayedResiduesList(self):
        """
        """
        return (str(residue) for residue in sorted(int(number) for number in self.manager.residuesList))

    def getSecondResiduesList(self, aResidueSelection):
        """
        """
        residuesList = self.manager.constraintsManagerForResidues(aResidueSelection).partnerResidueListForResidues(aResidueSelection)
        return sorted(int(number) for number in residuesList)

    def getAtomsForResidue(self, aResidueNumber):
        """
        """
        atomsList = self.manager.atomsListForResidue(aResidueNumber)
        return sorted(atomsList)

    def getSecondResiduesForAtoms(self, atomsSelection):
        """
        """
        residuesList = set()
        if atomsSelection:
            residueNumbers = [anAtom['resi_number'] for anAtom in atomsSelection]
            residuesList = self.manager.constraintsManagerForAtoms(atomsSelection).partnerResidueListForResidues(residueNumbers)
        return sorted(int(number) for number in residuesList)

    def getSecondAtomsinResidueForAtom(self, aResidueNumber, anAtomDefinition):
        """
        """
        atomsList = set(self.manager.partnerAtomsInResidueForAtoms(aResidueNumber, anAtomDefinition))
        return sorted(atomsList)
