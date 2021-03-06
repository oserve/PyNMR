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

    def __init__(self, dataSource, aManagerName, structure):
        """
        """
        self.structure = structure
        self.name = aManagerName
        self.dataType = 'NOE'
        self.selectedAtoms = list()
        self.manager = dataSource.constraintsManagerForDataType(self.dataType)

    def __len__(self):
        """
        """
        return len(self.manager)

    @property
    def residuesList(self):
        """
        """
        return (str(residue) for residue in sorted(self.manager.residuesList, key=int))

    def setSelectedAtoms(self, aSelection):
        """
        """
        self.selectedAtoms = aSelection
        self.manager.setPartnerAtoms(aSelection)

    @property
    def displayedAtoms(self):
        """
        """
        return sorted(self.manager.atomsList)

    @property
    def partnerAtoms(self):
        """
        """
        partners = set()
        if self.selectedAtoms:
            for anAtom in self.selectedAtoms:
                self.manager.setPartnerAtoms([anAtom])
                partners.update(atom for atom in self.manager.atomsList if self.manager.areAtomsPartner(atom) and atom != anAtom)
            return sorted(partners)
        else:
            raise UnboundLocalError("Partner list not registered.\n")

    def constraintsForAtoms(self, atomsList):
        """
        """
        if len(atomsList) == 2:
            consManager = self.manager.constraintsManagerForAtoms([atomsList[0]]).intersection(self.manager.constraintsManagerForAtoms([atomsList[1]]))
            return consManager.constraints
        else:
            raise ValueError("There should be 2 items in the list, " + str(len(atomsList)) + " found.\n")

    def constraintValueForAtoms(self, atomsList):
        """
        """
        return [(constraint.constraintValues, constraint.satisfaction()) for constraint in self.constraintsForAtoms(atomsList)]
