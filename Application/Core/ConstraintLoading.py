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

#DistanceConstraints loading functions
from sys import stderr, stdout
import re

from .Constraints.NOE import NOE
from ConstraintManager import ConstraintSetManager


class ConstraintLoader(object):
    """Classes used to lad constraints from
    files and returns a constraintSetManager filled
    with constraints
    """
    def __init__(self, fileName, managerName, constraintDefinition):
        self.fileName = fileName
        self.managerName = managerName
        self.constraintDefinition = constraintDefinition
        self.inFileTab = []

        #Useful RegEx definitions
        self.ParReg = re.compile('[()]')  # used in cns constraints loading. Suppression of ()
        self.SParReg = re.compile("\(.*\)")  #used in cns constraint loading.
        self.RegResi = re.compile("RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#]*")  #match CNS Residue definition
        self.SharpReg = re.compile('[#]')  # used in cns constraints loading. Replace # by *
        self.AtTypeReg = re.compile('[CHON][A-Z]*')

    def loadConstraintsFromFile(self):
        self.loadFile()
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
            stderr.write("incorrect or unsupported constraint type.\n")
        self.inFileTab = []

        return aManager

    def loadFile(self):
        fin = open(self.fileName, 'r')
        for txt in fin:
            txt = txt.lstrip()
            if txt.find('!') < 0:
                self.inFileTab.append(txt.upper().rstrip())
            else:
                stderr.write(txt + " skipped. Commented out.\n")
        fin.close()

    def synthesizeCNSFile(self):
        self.validCNSConstraints = []
        for line in self.inFileTab:
            if line.find("ASSI") > -1:
                line = line.replace("GN", "")
                self.validCNSConstraints.append(line.replace("ASSI", ""))
            elif self.RegResi.search(line) != None:
                self.validCNSConstraints[-1] = self.validCNSConstraints[-1] + line

    def CNSConstraintLoading(self, aManager):
        """
        Return a ConstraintSetManager loaded with cns/xplor constraints
        """
        constraint_number = 1

        for aConstLine in self.validCNSConstraints:  #itemizing constraints
            #avoid empty lines
            if re.search('\d', aConstLine):
                parsingResult = self.parseCNSConstraint(aConstLine)
                if len(parsingResult) == 3:  #2 residues + distances (matches also H-Bonds)
                    aConstraint = NOE()
                else:
                    #No other constraint type supported ... for now !
                    break
                aConstraint.id["number"] = constraint_number
                aConstraint.definition = aConstLine
                aConstraint.addAtomGroups(parsingResult)
                aConstraint.setConstraintValues(parsingResult[-1][0], parsingResult[-1][1], parsingResult[-1][2])  #Values always at the end of the array

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
        for aConstLine in self.inFileTab:
            if len(aConstLine) > 1:
                if aConstLine.find('#') == 0:
                    stderr.write(aConstLine + " skipped. Commented out.\n")
                else:
                    cons_tab = aConstLine.split()
                    aConstraint = NOE()
                    try:  #For errors not filtered previously
                        parsed = [
                            {'resid': int(cons_tab[0]),
                             'name': self.AtTypeReg.match(
                                self.convertTypeDyana(cons_tab[2])).group()},
                            {'resid': int(cons_tab[3]),
                             'name': self.AtTypeReg.match(
                                self.convertTypeDyana(cons_tab[5])).group()}
                            ]
                        aConstraint.addAtomGroups(parsed)
                        aConstraint.setConstraintValues(str(1.8 +
                                                            (float(cons_tab[6])
                                                             -1.8)/2),
                                                        '1.8', cons_tab[6])
                        aManager.addConstraint(aConstraint)
                        counter = counter + 1
                    except:
                        stderr.write("Unknown error while loading constraint "
                                     +":\n"+ aConstLine + "\n")
            else:
                stderr.write("Empty line, skipping.\n")

        stdout.write(str(len(aManager)) + " constraints loaded.\n")

    def parseCNSConstraint(self, aCNSConstraint):
        """Split CNS/XPLOR type constraint into an array, contening the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        """
        residuesList = self.RegResi.findall(aCNSConstraint, re.IGNORECASE)
        constraintValuesList = self.SParReg.sub("", aCNSConstraint).split()
        constraintParsingResult = []
        for aResidue in residuesList:
            residueParsingResult = {}
            for aDefinition in self.SharpReg.sub('*', aResidue).split("AND"):
                definitionArray = aDefinition.split()
                residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()
            constraintParsingResult.append(residueParsingResult)
        numericValues = []
        for aValue in constraintValuesList:
            numericValues.append(float(aValue))
        constraintParsingResult.append(numericValues)
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
