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
from AtomClass import AtomSet
from .. Core import MolecularViewerInterface as MVI


class Constraint(object):
    """
    Abstract Constraint Class
    Contains informations about constraints
    atoms, model value, theoretical value,
    constraint number, constraint name
    and methods that allows to get these informations
    or to determine if the constraints is unSatisfied or not (TODO)
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self):
        """
        """
        self.id = dict()
        self.resis = list()
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
        return isinstance(anotherConstraint, self.__class__) and (anotherConstraint.__dict__ == self.__dict__)

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

    def associatePDBAtoms(self, structureName):
        """
        Sets atoms sets, checks for inconsistency with structure file
        """
        for atomsSetNumber in xrange(self.numberOfAtomsSets):
            self.atoms.append(AtomSet(self.resis[atomsSetNumber]['number'],
                                      self.resis[atomsSetNumber]['atoms'] +
                                      self.resis[atomsSetNumber]['atoms_number'],
                                      self.resis[atomsSetNumber]['segid']))

    def isValid(self):
        """Return false if one of the atomsets is not valid
        """
        validity = True
        for atomSet in self.atoms:
            if MVI.checkID(atomSet) == False:
                validity = False
                break
        return validity

    def setValueFromStructure(self):
        """
        """
        raise NotImplementedError


    def getResisNumber(self):
        """Utility method
        """
        return [resi['number'] for resi in self.resis]

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
