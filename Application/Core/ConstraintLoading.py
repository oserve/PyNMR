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

# DistanceConstraints loading functions
from sys import stderr, stdout
import re
from .Constraints.NOE import NOE
from ConstraintManager import ConstraintSetManager

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# Useful RegEx definitions
ParReg = re.compile('[()]')  # used in cns constraints loading. Suppression of ()
SParReg = re.compile(r"\(.*\)")  # used in cns constraint loading.
RegResi = re.compile(r"RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#]*")  # match CNS Residue definition
SharpReg = re.compile('[#]')  # used in cns constraints loading. Replace # by *
AtTypeReg = re.compile('[CHON][A-Z]*')
XEASYReg = re.compile(r'\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\w+\s+\d+')
RegSeg = re.compile(r'SEGI\w*\s+[\w\d]*') # match CNS segid definition
RegFloat = re.compile(r'\s+[-+]?[0-9]*\.?[0-9]+'*3)


class ConstraintLoader(object):
    """Classes used to lad constraints from
    files and returns a constraintSetManager filled
    with constraints
    """
    def __init__(self, fileName, managerName):
        """
        """
        self.fileName = fileName
        self.managerName = managerName
        self.fileText = ""
        self.segments = []
        self.inFileTab = []
        self.validCNSConstraints = []

    def loadConstraintsFromFile(self):
        """
        """
        self.constraintDefinition = self.loadFile()
        return self.loadConstraints()

    def loadConstraints(self):
        """Starts constraints loading, uses appropriate function
        depending on file type
        """
        aManager = ConstraintSetManager(self.managerName)
        if self.constraintDefinition in ['XPLOR', 'CNS']:
            self.synthesizeCNSFile()
            self.CNSConstraintLoading(aManager)
        elif self.constraintDefinition in ['DYANA', 'CYANA']:
            self.CYANAConstraintLoading(aManager)
        else:
            stderr.write("Incorrect or unsupported constraint type.\n")
        self.inFileTab = []
        aManager.fileText = self.fileText

        return aManager

    def loadFile(self):
        """
        """

        with open(self.fileName, 'r') as file_in:
            fin = file_in.read().upper()

        self.fileText = fin

        if "ASSI" in fin:
            typeDefinition = 'CNS'
        elif XEASYReg.search(fin):
            typeDefinition = 'CYANA'
        else:
            typeDefinition = None

        for txt in fin.split('\n'):
            txt = txt.strip()
            if '!' in txt:
                stderr.write('Comment excluded : ' + txt[txt.find('!'):-1] + "\n")
                txt = txt[0:txt.find('!')].replace('!', '')
                if txt == '':
                    continue
            if 'OR ' in txt:
                self.inFileTab[-1] = self.inFileTab[-1] + txt
                continue
            self.inFileTab.append(txt)
        return typeDefinition

    def synthesizeCNSFile(self):
        """
        """
        del self.validCNSConstraints[:]
        for line in [aline.replace('"', ' ') for aline in self.inFileTab]:
            if "ASSI" in line:
                line = line.replace("GN", "")
                self.validCNSConstraints.append(line.replace("ASSI", ""))
            elif RegResi.search(line) != None:
                self.validCNSConstraints[-1] = self.validCNSConstraints[-1] + line

    def CNSConstraintLoading(self, aManager):
        """
        Return a ConstraintSetManager loaded with cns/xplor constraints
        """
        constraint_number = 1
        aManager.format = "CNS"
        del self.segments[:]
        for aConstLine in self.validCNSConstraints:  # itemizing constraints
            # avoid empty lines
            if re.search(r'\d', aConstLine):
                parsingResult = self.parseCNSConstraint(aConstLine)
                if parsingResult is not None:
                    if len(parsingResult) == 3:  # 2 residues + distances (matches also H-Bonds)
                        aConstraint = NOE()
                    else:
                        # No other constraint type supported ... for now !
                        continue
                    aConstraint.id["number"] = constraint_number
                    aConstraint.definition = aConstLine
                    aConstraint.addAtomGroups(parsingResult)
                    aConstraint.setConstraintValues(parsingResult[-1][0],
                                                    parsingResult[-1][1],
                                                    parsingResult[-1][2])  # Values always at the end of the array

                    aManager.addConstraint(aConstraint)
                    constraint_number = constraint_number + 1
            else:
                stderr.write("This line : " + aConstLine + " is not a valid constraint.\n")
                continue
        stdout.write(str(len(aManager)) + " constraints loaded.\n")

    def CYANAConstraintLoading(self, aManager):
        """"
        Return a ConstraintSetManager loaded with CYANA/DYANA constraints
        """
        counter = 1
        aManager.format = "XEASY"
        for aConstLine in self.inFileTab:
            if len(aConstLine) > 1:
                if aConstLine.find('#') == 0:
                    stderr.write(aConstLine + " skipped. Commented out.\n")
                else:
                    cons_tab = aConstLine.split()
                    aConstraint = NOE()
                    try:  # For errors not filtered previously
                        parsed = [
                            {'resid': int(cons_tab[0]),
                             'name': AtTypeReg.match(
                                self.convertTypeDyana(cons_tab[2])).group()},
                            {'resid': int(cons_tab[3]),
                             'name': AtTypeReg.match(
                                self.convertTypeDyana(cons_tab[5])).group()}
                            ]
                        aConstraint.addAtomGroups(parsed)
                        aConstraint.setConstraintValues(str(1.8 +
                                                            (float(cons_tab[6])
                                                             - 1.8)/2),
                                                        '1.8', cons_tab[6])
                        aManager.addConstraint(aConstraint)
                        counter = counter + 1
                    except:
                        stderr.write("Unknown error while loading constraint " +
                                     ":\n" + aConstLine + "\n")
            else:
                stderr.write("Empty line, skipping.\n")

        stdout.write(str(len(aManager)) + " constraints loaded.\n")

    def parseCNSConstraint(self, aCNSConstraint):
        """Split CNS/XPLOR type constraint into an array, contening the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        """
        try:
            residuesList = RegResi.findall(aCNSConstraint, re.IGNORECASE)
            segments = RegSeg.findall(aCNSConstraint, re.IGNORECASE)
            for segment in segments:
                if segment not in self.segments:
                    self.segments.append(segment)
            numberOfSegments = len(segments)

            constraintParsingResult = []
            indice = 0
            for aResidue in residuesList:
                residueParsingResult = {}
                for aDefinition in SharpReg.sub('*', aResidue).split("AND "):
                    definitionArray = aDefinition.split()
                    residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()
                if numberOfSegments > 0:
                    residueParsingResult["segid"] = alphabet[self.segments.index(segments[indice])]
                else:
                    residueParsingResult["segid"] = "A"
                constraintParsingResult.append(residueParsingResult)
                indice += 1

            if 'OR ' in aCNSConstraint:
                if constraintParsingResult[0] == constraintParsingResult[2] or constraintParsingResult[0] == constraintParsingResult[3]:
                    indiceAmbiguous = 1
                else:
                    indiceAmbiguous = 0
                constraintParsingResult[indiceAmbiguous]['name'] = constraintParsingResult[indiceAmbiguous]['name'][0:-1] + "*"
                constraintParsingResult = [constraintParsingResult[0], constraintParsingResult[1]]

            constraintValues = RegFloat.findall(aCNSConstraint)
            if len(constraintValues) > 0:
                constraintValuesList = RegFloat.findall(aCNSConstraint)[0].split()
            else:
                constraintValuesList = []
            numericValues = [float(aValue) for aValue in constraintValuesList]
            constraintParsingResult.append(numericValues)

        except:
            stderr.write('Can not parse : ' + aCNSConstraint + '\n')
            constraintParsingResult = None
        return constraintParsingResult

    def convertTypeDyana(self, atType):
        """
        Adapt xeasy nomenclature Q to pymol *
        """
        if atType.count('Q'):
            newType = atType.replace('Q', 'H', 1)
            newType = newType + ('*')  # Q is replaced by H and a star at the end of the atom type
            newType = newType.replace('Q', '')  # avoid QQ (QQD-> HD*)
            return newType
        else:
            return atType
