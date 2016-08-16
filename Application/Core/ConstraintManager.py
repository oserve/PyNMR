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
import MolecularViewerInterface as MVI
import re


class ConstraintSetManager(object):
    """Class to manage a set of constraints
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, managerName):
        self.constraints = []
        self.residuesList = []
        self.structure = ''
        self.name = managerName
        self.format = ""
        self.fileText = ""
        self.atoms = {}

    def __str__(self):
        return self.name + " contains " + str(len(self.constraints)) + " constraints.\n"

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    # Constraints management methods

    def setPDB(self, structure):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.structure = structure
        for constraint in self.constraints:
            constraint.structureName = self.structure

    def associateToPDB(self):
        """Invokes associatePDBAtoms function on all constraints
        """
        result = 0
        if self.structure != '':
            MVI.setPDB(self.structure)
            if self.constraints:
                for constraint in self.constraints:
                    constraint.associatePDBAtoms(self.structure)
                result = 1
        return result

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

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) <= len(self.constraints):
            del self.constraints[int(aConstraintNumber)]

    def addAtom(self, parsingResult):
        """Checks that atoms are not loaded several times
        should limits future memory issues
        """
        residues = []
        for aResult in parsingResult:
            currentResidue = {}
            if "resid" in aResult:
                currentResidue["number"] = aResult["resid"]
            else:
                currentResidue["number"] = aResult["resi"]
            currentResidue["atoms"] = ConstraintSetManager.AtTypeReg.match(aResult["name"]).group()
            currentResidue["atoms_number"] = ConstraintSetManager.AtTypeReg.sub('', aResult["name"])
            currentResidue["ambiguity"] = ConstraintSetManager.AtTypeReg.sub('', aResult["name"]).find('*')
            if "segid" in aResult:
                currentResidue["segid"] = aResult["segid"]

            residueKey = ''.join(str(value) for value in currentResidue.values())

            if residueKey not in self.atoms:
                self.atoms[residueKey] = currentResidue
                if currentResidue["number"] not in self.residuesList:
                    self.residuesList.append(currentResidue["number"])
                residues.append(currentResidue)
            else:
                residues.append(self.atoms[residueKey])
        return residues
