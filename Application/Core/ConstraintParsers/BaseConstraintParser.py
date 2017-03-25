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
from sys import stderr
import re
from collections import Iterator
from ..Constraints.NOE import NOE


class BaseConstraintParser(Iterator):
    """
    """

    XEASYReg = re.compile(r'\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\w+\s+\d+')
    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self, text):
        """
        """
        self.text = (aLine.strip() for aLine in text.split('\n'))
        self.inFileTab = list()
        self.segments = list()
        self.prepareFile()

    def __iter__(self):
        return self

    def next(self):
        """
        """

        for parsingResult in self.parseConstraints():
            if parsingResult is not None:
                if len(parsingResult["residues"]) == 2:  # 2 residues (matches also H-Bonds)
                    for residue in parsingResult["residues"]: # filters H-Bonds
                        if residue['name'] == "O":
                            break
                    else:
                        aConstraint = NOE()
                        # No other constraint type supported ... for now !
                        aConstraint.definition = parsingResult["definition"]
                        aConstraint.atoms = NOE.addAtoms(BaseConstraintParser.parseAtoms(parsingResult["residues"]))
                        aConstraint.setConstraintValues(parsingResult["values"][0],
                                                        parsingResult["values"][1],
                                                        parsingResult["values"][2])
                        return aConstraint
            else:
                stderr.write("Error while loading : " + parsingResult["definition"])
                continue
        raise StopIteration

    def prepareFile(self):
        """
        """
        raise NotImplementedError

    def parseConstraints(self):
        """
        """
        raise NotImplementedError

    @staticmethod
    def findConstraintType(fileText):
        """
        """
        if "ASSI" in fileText:
            typeDefinition = 'CNS'
        elif BaseConstraintParser.XEASYReg.search(fileText):
            typeDefinition = 'CYANA'
        else:
            typeDefinition = None
        return typeDefinition

    @staticmethod
    def parseAtoms(parsingResult):
        """
        """
        for aResult in parsingResult:
            currentResidue = dict()
            if "resid" in aResult:
                currentResidue["resi_number"] = int(aResult["resid"])
            else:
                currentResidue["resi_number"] = int(aResult["resi"])
            currentResidue["atoms"] = aResult["name"]
            currentResidue["segid"] = aResult.get("segid", 'A')
            yield currentResidue
