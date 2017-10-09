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
from itertools import izip
import re

from Application.Core.ConstraintParsers.BaseConstraintParser import BaseConstraintParser

SegResiReg = re.compile(r"(SEGI\w*\s+[\w\d]+\s+AND\s+)?(RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#\+%]*)")
RegFloat = re.compile(r'\s+[-+]?[0-9]*\.?[0-9]+'*3)


class CNSParser(BaseConstraintParser):
    """
    """
    def __init__(self, text):
        """
        """
        self.validConstraints = list()
        BaseConstraintParser.__init__(self, text)

    def prepareFile(self):
        """
        """
        for txt in self.text:
            if '!' in txt:
                exclamIndex = txt.find('!')
                stderr.write('Comment excluded : ' + txt[exclamIndex:-1] + "\n")
                txt = txt[0:exclamIndex].replace('!', '')
                if txt == '':
                    continue
            if 'OR ' in txt:
                self.inFileTab[-1] = self.inFileTab[-1] + txt
                continue
            self.inFileTab.append(txt)

        del self.validConstraints[:]

        for line in (aline.replace('"', ' ') for aline in self.inFileTab):
            if "ASSI" in line:
                line = line.replace("GN", "")
                self.validConstraints.append(line.replace("ASSI", ""))
            elif SegResiReg.search(line) is not None:
                self.validConstraints[-1] = self.validConstraints[-1] + line
        self.validConstraints = (constraint for constraint in self.validConstraints if re.search(r'\d', constraint))

    def parseConstraints(self):
        """Split CNS/XPLOR type constraint into a dictionnary, containing the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        """
        for aCNSConstraint in self.validConstraints:
            try:
                residuesList = SegResiReg.finditer(aCNSConstraint, re.IGNORECASE)

                constraintParsingResult = dict()
                residues = list()
                for aResidue in residuesList:
                    residueParsingResult = dict()
                    try:
                        segid = aResidue.group(1).split()[1]
                    except AttributeError:
                        segid = ''
                    residueParsingResult["segid"] = segid

                    for aDefinition in aResidue.group(2).split(" AND "):
                        definitionArray = aDefinition.split()
                        residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()

                    residues.append(residueParsingResult)
                constraintParsingResult["residues"] = residues

                if 'OR ' in aCNSConstraint: # only for NOE
                    constraintParsingResult["residues"] = constraintAmbiguity(constraintParsingResult["residues"])

                constraintParsingResult["values"] = constraintValues(aCNSConstraint)
                constraintParsingResult["definition"] = aCNSConstraint

            except ZeroDivisionError:
                stderr.write('Can not parse : ' + aCNSConstraint + '\n')
                constraintParsingResult = None
            yield constraintParsingResult


def constraintAmbiguity(constraintResidues):
    """
    """
    sortedResidues = [[constraintResidues[0]], []]
    for residue in constraintResidues[1:]:
        if residuesLooksLike(constraintResidues[0], residue):
            sortedResidues[0].append(residue)
        else:
            sortedResidues[1].append(residue)

    results = []
    for resiList in sortedResidues:
        names = [residue['name'] for residue in resiList]
        ambiguousResidue = resiList[0]
        if len(set(names)) != 1:
            ambiguousResidue = resiList[0]
            for index, letters in enumerate(izip(*names)):
                if len(set(letters)) != 1:
                    ambiguousResidue['name'] = resiList[0]['name'][:index] + "*"
                    break       
        results.append(ambiguousResidue)
    return results

def constraintValues(aCNSConstraint):
    """
    """
    constraintValues = RegFloat.findall(aCNSConstraint)
    if constraintValues:
        constraintValuesList = constraintValues[0].split()
    else:
        constraintValuesList = tuple()
    return tuple(float(aValue) for aValue in constraintValuesList)

def residuesLooksLike(residueA, residueB):
    if residueA.get("segid", "A") == residueA.get("segid", "A"):
        if residueA["resid"] == residueB["resid"]:
            if len(residueA["name"]) > 1:
                if len(residueA["name"]) == len(residueB["name"]):
                    return residueA["name"][0:-1] == residueB["name"][0:-1]
    return False
