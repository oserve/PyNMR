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
from itertools import izip

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

    AtTypeReg = re.compile(r'[CHON][A-Z]*')
    atoms = dict()

    def __init__(self):
        """
        """
        self.id = dict()
        self.cutOff = 0
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
        return isinstance(anotherConstraint, self.__class__) and all(AAtom == SAtom for AAtom, SAtom in izip(anotherConstraint.atoms, self.atoms)) # assume sorted

    @staticmethod
    def addAtoms(parsingResult):
        """
        """
        return sorted([Constraint.addAtom(aResult) for aResult in parsingResult])

    @staticmethod
    def addAtom(aParsingResult):
        """Checks that atoms are not loaded several times
        should limits future memory issues
        """
        residueKey = ''.join(str(value) for value in aParsingResult.values())
        return Constraint.atoms.setdefault(residueKey, Atoms(**aParsingResult))

    @property
    def name(self):
        """Utility method to set constraint name
        """
        return self.id.get('name', "")

    @name.setter
    def name(self, aName):
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

    def setValueFromStructure(self):
        """
        """
        raise NotImplementedError

    @property
    def ResiNumbers(self):
        """Utility method
        """
        return (atom.resi_number for atom in self.atoms)

    def satisfaction(self, cutOff=-1):
        """Set violation state, with optional additional cutoff
        """
        if cutOff >= 0:
            self.cutOff = cutOff
        if self.constraintValues['actual'] <= (self.constraintValues['constraint'] - self.constraintValues['min'] - self.cutOff):
            self.constraintValues['closeness'] = 'tooClose'
            return 'unSatisfied'
        elif self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + self.cutOff):
            self.constraintValues['closeness'] = 'tooFar'
            return 'unSatisfied'
        else:
            return 'Satisfied'
