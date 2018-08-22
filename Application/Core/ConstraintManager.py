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
import re
from collections import Sequence, MutableSequence

import Application.Core.MolecularViewerInterfaces.MolecularViewerInterface as MVI


class imConstraintSetManager(Sequence):
    """Class to manage an immutable set of constraints
    """

    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self, managerName):
        self.constraints = tuple()
        self.name = managerName

    def __str__(self):
        return "\n".join(str(constraint) for constraint in self)

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    def __getitem__(self, constraintIndex):
        try:
            self.constraints[constraintIndex].id['number'] = constraintIndex
            return self.constraints[constraintIndex]
        except IndexError:
            raise IndexError("Index error, no constraint at index {}.\n".format(constraintIndex))
            
    # Constraints management methods

    def setPDB(self, structure):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.structure = structure
        for constraint in self.constraints:
            constraint.structureName = self.structure

    def associateToPDB(self):
        """read strutural data
        """
        if self.structure != '':
            MVI.setPDB(self.structure)
            return len(self.constraints) > 0
        return False

    def constraintsManagerForDataType(self, dataType):
        """
        """
        newManager = imConstraintSetManager(self.name + str(dataType))
        newManager.constraints = tuple(constraint for constraint in self.constraints if constraint.type == dataType)
        return newManager

    def constraintsManagerForAtoms(self, atomDefinitions):
        """
        """
        newManager = imConstraintSetManager(self.name + " for atoms " + str(atomDefinitions))
        newConstraints = set()
        for constraint in self.constraints:
            for atom in constraint.atoms:
                if atom in atomDefinitions:
                    newConstraints.add(constraint)
        newManager.constraints = tuple(newConstraints)
        return newManager

    @property
    def residuesList(self):
        """
        """
        resis = set()
        for constraint in self.constraints:
            resis.update(constraint.ResiNumbers)
        return resis

    def intersection(self, anotherManager):
        """
        """
        newManager = imConstraintSetManager("")
        if isinstance(anotherManager, imConstraintSetManager):
            newManager.constraints = tuple(set(self.constraints) & set(anotherManager.constraints))
            newManager.name = self.name + anotherManager.name
        else:
            raise TypeError(str(anotherManager) + " is not a " + str(type(self)) + "\n")
        return newManager

    @property
    def atomsList(self):
        """
        """
        atomList = set()
        for constraint in self.constraints:
            atomList.update(constraint.atoms)
        return atomList

    def setPartnerAtoms(self, AtomSelection):
        """
        """
        self.partnerManager = self.constraintsManagerForAtoms(AtomSelection)

    def areAtomsPartner(self, anAtom):
        """
        """
        return anAtom in self.partnerManager.atomsList


class ConstraintSetManager(imConstraintSetManager, MutableSequence):
    """Class to manage a mutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self, managerName):
        super(ConstraintSetManager, self).__init__(managerName)
        self.constraints = list()
        self.structure = ""
        self.format = ""
        self.fileText = ""

    def __setitem__(self, constraintIndex, constraint):
        try:
            self.constraints[constraintIndex] = constraint
            if constraint.name == "":
                constraint.name = self.name
        except IndexError:
            raise IndexError("Index error, no constraint at index {}.\n".format(constraintIndex))

    def __delitem__(self, constraintIndex):
        try:
            del self.constraints[constraintIndex]
        except IndexError:
            raise IndexError("Index error, no constraint at index {}.\n".format(constraintIndex))

    def insert(self, constraintIndex, constraint):
        self.constraints.insert(constraintIndex, constraint)
