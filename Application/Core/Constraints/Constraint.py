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
from AtomClass import AtomSet
import re


class Constraint(object):
    """
    Abstract Constraint Class
    Contains informations about constraints
    atoms, model value, theoretical value,
    constraint number, constraint name
    and methods that allows to get these informations
    or to determine if the constraints is unSatisfied or not (TODO)
    """

    def __init__(self):
        """
        """
        self.id = {}
        self.resis = []
        self.satisfaction = ''
        self.definition = ''
        self.atoms = []
        self.constraintValues = {}
        self.numberOfAtomsSets = 0
        self.AtTypeReg = re.compile('[CHON][A-Z]*')
        self.structureName = ""

    def __str__(self):
        """
        """
        return self.definition

    __repr__ = __str__

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

    def isSatifsied(self):
        """
        Returns yes or no according to the violation state
        """
        return self.satisfaction

    def associatePDBAtoms(self, structureName):
        """
        Sets atoms sets, checks for inconsistency with structure file
        """
        for atomsSetNumber in range(self.numberOfAtomsSets):
            self.atoms.append(AtomSet(structureName,
                                      self.resis[atomsSetNumber]['number'],
                                      self.resis[atomsSetNumber]['atoms'] +
                                      self.resis[atomsSetNumber]['atoms_number']
                                      )
                              )

        return self.isValid()

    def isValid(self):
        """Return yes or no if one of the atomset is not valid
        """
        validity = 1
        for atomsSetNumber in range(self.numberOfAtomsSets):
            if "noID" in self.atoms[atomsSetNumber].getID():
                validity = 0
                break
        return validity

    def addAtomGroups(self, parsingResult):
        """
        """
        for position in range(self.numberOfAtomsSets):
            currentResidue = {}
            if "resid" in parsingResult[position].keys():
                currentResidue["number"] = parsingResult[position]["resid"]
            else:
                currentResidue["number"] = parsingResult[position]["resi"]
            currentResidue["atoms"] = self.AtTypeReg.match(parsingResult[position]["name"]).group()
            currentResidue["atoms_number"] = self.AtTypeReg.sub('', parsingResult[position]["name"])
            currentResidue["ambiguity"] = self.AtTypeReg.sub('', parsingResult[position]["name"]).find('*')
            if "segid" in parsingResult[position].keys():
                currentResidue["segid"] = parsingResult[position]["segid"]
            self.resis.append(currentResidue)
