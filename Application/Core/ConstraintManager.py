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
import MolecularViewerInterface as MVI


class imConstraintSetManager(object):
    """Class to manage an immutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, managerName):
        self.constraints = ()
        self.name = managerName
        self.index = -1

    def __str__(self):
        return self.name + " contains " + str(len(self.constraints)) + " constraints.\n"

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    def __iter__(self):
        return self

    def next(self):
        if self.index == len(self.constraints) - 1:
            self.index = -1
            raise StopIteration
        self.index += 1
        return self.constraints[self.index]

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
        result = 0
        if self.structure != '':
            MVI.setPDB(self.structure)
            if self.constraints:
                result = 1
        return result

    def constraintsManagerForDataType(self, dataType):
        """
        """
        newManager = imConstraintSetManager(self.name + str(dataType))
        newConstraintsSet = set(constraint for constraint in self.constraints if constraint.type == dataType)
        newManager.constraints = tuple(newConstraintsSet)
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
            resis.update(number for number in constraint.getResisNumber())
        return resis

    def intersection(self, anotherManager):
        """
        """
        newManager = imConstraintSetManager("")
        if isinstance(anotherManager, self.__class__):
            constraints = set()
            constraints.update(constraint for constraint in self.constraints if constraint in anotherManager)
            newManager.constraints = tuple(constraints)
            newManager.name = self.name + anotherManager.name
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
        if anAtom in self.partnerManager.atomsList:
            return True
        else:
            return False


class ConstraintSetManager(imConstraintSetManager):
    """Class to manage a mutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, managerName):
        super(ConstraintSetManager, self).__init__(managerName)
        self.constraints = []
        self.structure = ''
        self.format = ""
        self.fileText = ""

    # Constraints management methods

    def removeAllConstraints(self):
        """Empties an array of constraints
        """
        del self.constraints[:]

    def addConstraint(self, aConstraint):
        """Add a constraint to the constraint list of the manager and
        update the list of residues
        """
        self.constraints.append(aConstraint)
        aConstraint.setName(self.name)

    def addConstraints(self, constraints):
        """
        """
        for constraint in constraints:
            self.addConstraint(constraint)

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) <= len(self.constraints):
            del self.constraints[int(aConstraintNumber)]
