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
from collections import namedtuple

from .. import MolecularViewerInterface as MVI

Atoms = namedtuple("Atoms", ['segid', 'resi_number', 'atoms'])


class Constraint(object):
    """
    Abstract Constraint Class
    Contains informations about constraints
    atoms, model value, theoretical value,
    constraint number, constraint name
    and methods that allows to get these informations
    or to determine if the constraints is unSatisfied or not
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')
    atoms = dict()

    def __init__(self):
        """
        """
        self.id = dict()
        self.satisfaction = ''
        self.definition = ''
        self.atoms = list()
        self.constraintValues = dict()
        self.numberOfAtomsSets = 0
        self.structureName = ""
        self.type = ""

    def __str__(self):
        """
        """
        return self.definition

    __repr__ = __str__

    def __eq__(self, anotherConstraint):
        """
        """
        if isinstance(anotherConstraint, self.__class__):
            for AAtom, SAtom in zip(sorted(anotherConstraint.atoms), sorted(self.atoms)):
                if not AAtom == SAtom:
                    break
            else:
                return True
        return False

    @classmethod
    def addAtoms(cls, parsingResult):
        """
        """
        residues = list()
        for aResult in parsingResult:
            residues.append(Constraint.addAtom(aResult))
        return residues

    @classmethod
    def addAtom(cls, aParsingResult):
        """Checks that atoms are not loaded several times
        should limits future memory issues
        """
        residueKey = ''.join(str(value) for value in aParsingResult.values())
        if residueKey not in Constraint.atoms:
            Constraint.atoms[residueKey] = Atoms(**aParsingResult)
        return Constraint.atoms[residueKey]

    def setName(self, aName):
        """Utility method to set constraint name
        """
        self.id['name'] = aName

    def setConstraintValues(self, constraintValue, Vmin, Vplus):
        """
        Set constraints values for violations
        determination
        """
        self.constraintValues['constraint'] = float(constraintValue)
        self.constraintValues['min'] = float(Vmin)
        self.constraintValues['plus'] = float(Vplus)

    def isSatisfied(self):
        """
        Returns yes or no according to the violation state
        """
        return self.satisfaction

    def isValid(self):
        """Return false if one of the atomsets is not valid
        calls checkid to check this assertion and modify
        atoms data if it can
        """
        atoms = dict()
        for index, atomSet in enumerate(self.atoms):
            check = MVI.checkID(atomSet)
            if check['valid'] is True:
                if check['NewData']:
                    atom = dict(atomSet._asdict())
                    atom.update(check['NewData'])
                    atoms[index] = Constraint.addAtom(atom)
            else:
                break
        else:
            for index, value in atoms.items():
                self.atoms[index] = value
            return True
        return False

    def setValueFromStructure(self):
        """
        """
        raise NotImplementedError

    def getResisNumber(self):
        """Utility method
        """
        return (atom.resi_number for atom in self.atoms)

    def setViolationState(self, cutOff=0):
        """Set violation state, with optional additional cutoff
        """
        if self.constraintValues['actual'] <= (self.constraintValues['constraint'] - self.constraintValues['min'] - cutOff):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooClose'
        elif self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + cutOff):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooFar'
        else:
            self.satisfaction = 'Satisfied'
