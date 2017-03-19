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
import string
from Constraints.NOE import NOE


class constraintParser(Iterator):
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
                        aConstraint.atoms = NOE.addAtoms(constraintParser.parseAtoms(parsingResult["residues"]))
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
        elif constraintParser.XEASYReg.search(fileText):
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


class CNSParser(constraintParser):
    """
    """
    ParReg = re.compile(r'[()]')  # used in cns constraints loading. Suppression of ()
    SParReg = re.compile(r"\(.*\)")  # used in cns constraint loading.
    RegResi = re.compile(r"RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#\+%]*")  # match CNS Residue definition
    SharpPlusReg = re.compile(r'[\+#]')  # used in cns constraints loading. Replace # by *
    RegSeg = re.compile(r'SEGI\w*\s+[\w\d]*')  # match CNS segid definition
    RegFloat = re.compile(r'\s+[-+]?[0-9]*\.?[0-9]+'*3)

    def __init__(self, text):
        """
        """
        self.validConstraints = list()
        constraintParser.__init__(self, text)

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
            elif CNSParser.RegResi.search(line) is not None:
                self.validConstraints[-1] = self.validConstraints[-1] + line
        self.validConstraints = (constraint for constraint in self.validConstraints if re.search(r'\d', constraint))

    def parseConstraints(self):
        """Split CNS/XPLOR type constraint into an array, containing the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        It returns a dictionnary
        """
        for aCNSConstraint in self.validConstraints:
            try:
                segments = tuple(segment.group(0).split()[1] for segment in CNSParser.RegSeg.finditer(aCNSConstraint, re.IGNORECASE))
                numberOfSegments = len(segments)
                for segment in segments:
                    if segment not in self.segments:
                        self.segments.append(segment)

                residuesList = CNSParser.RegResi.finditer(aCNSConstraint, re.IGNORECASE)

                constraintParsingResult = dict()
                residues = list()
                for (indice, aResidue) in enumerate(residuesList):
                    residueParsingResult = dict()
                    for aDefinition in CNSParser.SharpPlusReg.sub('*', aResidue.group(0)).split("AND "):
                        definitionArray = aDefinition.split()
                        residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()
                    if numberOfSegments > 0:
                        residueParsingResult["segid"] = string.ascii_uppercase[self.segments.index(segments[indice])]
                    else:
                        residueParsingResult["segid"] = "A"
                    residues.append(residueParsingResult)
                constraintParsingResult["residues"] = residues

                if 'OR ' in aCNSConstraint: # only for NOE
                    self.constraintAmbiguity(constraintParsingResult["residues"])

                constraintParsingResult["values"] = self.constraintValues(aCNSConstraint)
                constraintParsingResult["definition"] = aCNSConstraint

            except ZeroDivisionError:
                stderr.write('Can not parse : ' + aCNSConstraint + '\n')
                constraintParsingResult = None
            yield constraintParsingResult

    @staticmethod
    def constraintAmbiguity(constraintResidues):
        """
        """
        if constraintResidues[0] == constraintResidues[2] or constraintResidues[0] == constraintResidues[3]:
            indiceAmbiguous = 1
        else:
            indiceAmbiguous = 0
        constraintResidues[indiceAmbiguous]['name'] = constraintResidues[indiceAmbiguous]['name'][0:-1] + "*"
        constraintResidues = (constraintResidues[0], constraintResidues[1])

    @staticmethod
    def constraintValues(aCNSConstraint):
        """
        """
        constraintValues = CNSParser.RegFloat.findall(aCNSConstraint)
        if constraintValues:
            constraintValuesList = constraintValues[0].split()
        else:
            constraintValuesList = tuple()
        return tuple(float(aValue) for aValue in constraintValuesList)


class CYANAParser(constraintParser):
    """
    """
    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def prepareFile(self):
        """
        """
        self.inFileTab = self.text

    def parseConstraints(self):
        """
        """
        for aConstraintLine in self.inFileTab:
            if len(aConstraintLine) > 1:
                if aConstraintLine.find('#') == 0:
                    stderr.write(aConstraintLine + " skipped. Commented out.\n")
                    parsed = None
            cons_tab = aConstraintLine.split()
            try:
                parsed = {"residues":
                    [{'resid': int(cons_tab[0]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[2])).group()},
                    {'resid': int(cons_tab[3]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[5])).group()}]}
                parsed["values"] = ([str(1.8 + (float(cons_tab[6]) - 1.8)/2), '1.8', cons_tab[6]])
                parsed["definition"] = aConstraintLine
            except:
                stderr.write("Unknown error while loading constraint " + ":\n" +
                             aConstraintLine + "\n")
                parsed = None
            yield parsed

    @staticmethod
    def convertTypeDyana(atType):
        """
        Adapt xeasy nomenclature Q to pymol *
        """
        if 'Q' in atType:
            newType = atType.replace('Q', 'H', 1) + ('*')
            # Q is replaced by H and a star at the end of the atom type
            # avoid QQ (QQD-> HD*)
            return newType.replace('Q', '')
        else:
            return atType
