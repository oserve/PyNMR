import gzip
import os
import os.path as path
import pickle
import re
import shutil
import sys
import tempfile
import tkColorChooser
import tkFileDialog
import Tkinter as Tk
import tkSimpleDialog
import ttk
import urllib2
from collections import OrderedDict, namedtuple
from math import sqrt
from sys import stderr, stdout


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI"):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.NMRCLI = NMRCLI(Core)
        if app == "NoGUI":
            stdout.write("Starting PyNMR CLI ...\n")
        else:
            stdout.write("Starting PyNMR GUI ...\n")
            self.startGUI()

    def startGUI(self):
        """
        """
        self.NMRInterface = NMRGUI()
        self.NMRInterface.startGUI()
        self.GUIBindings()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection['values'] = defaultForParameter('gradientColorList')
        self.NMRInterface.preferencesPanel.setDefaults()
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(defaultForParameter("cutOff"))
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = getModelsNames(defaultForParameter('SatisfactionMarker'), defaultForParameter('UnSatisfactionMarker'))
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self
        self.NMRInterface.preferencesPanel.mainApp = self


class NMRCLI(object):
    """
    """

    def __init__(self, Core):
        """
        """
        self.Core = Core
        self.dataControllers = dict()

    def showNOE(self, structure, managerName, residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker):
        """Command to display NMR restraints as sticks on protein structure with
        different parameters : filtering according to distance, restraints display
        options
        """
        if structure != '':
            if managerName == '' and len(self.Core.ManagersList) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.ManagersList.keys()[0]
                if managerName in self.Core.ManagersList:
                    self.Core.commandsInterpretation(structure, managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showSticks(managerName, structure, colors, radius,
                                         UnSatisfactionMarker, SatisfactionMarker)

                    self.dataControllers[managerName] = NOEDataController(self.Core, managerName)
                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].getResiduesList()])) +
                                 " residues involved.\n")

                else:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def loadNOE(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        if path.exists(filename):
            self.Core.loadNOE(filename)
            stdout.write(str(len(self.Core.ManagersList[path.basename(filename)])) + " constraints loaded.\n")

        else:
            stderr.write("File : " + filename + " has not been found.\n")

    def showNOEDensity(self, structure, managerName, residuesList, dist_range,
                       violationState, violCutoff, rangeCutOff, method, colors):
        """Command to display NMR restraints as color map on protein structure with
        different parameters : filtering according to distance, restraints display
        options
        """
        if structure != '':
            if managerName == '' and len(self.Core.ManagersList) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.ManagersList.keys()[0]
                if managerName in self.Core.ManagersList:
                    self.Core.commandsInterpretation(structure, managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showNOEDensity(managerName, structure, colors)
                    self.dataControllers[managerName] = NOEDataController(self.Core, managerName)

                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].getResiduesList()])) +
                                 " residues involved.\n")
                else:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def loadAndShow(self, filename, structure, residuesList, dist_range,
                    violationState, violCutoff, method, rangeCutOff,
                    radius, colors, UnSatisfactionMarker, SatisfactionMarker):
        """Combine two previous defined functions : load and display"""
        self.loadNOE(filename)
        self.showNOE(structure, path.basename(filename), residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker)


    def downloadNMR(self, pdbCode, url):
        """
        """
        self.Core.downloadFromPDB(pdbCode, url)

    def cleanScreen(self, filename):
        """Call the command to clear the screen from all NMR
        restraints
        """
        if filename in self.Core.ManagersList:
            self.Core.cleanScreen(filename)
            del self.dataControllers[filename]


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
            aManager.format = "CNS"
            parser = CNSParser(self.fileText)
        elif self.constraintDefinition in ['DYANA', 'CYANA']:
            aManager.format = "XEASY"
            parser = CYANAParser(self.fileText)
        else:
            stderr.write("Incorrect or unsupported constraint type.\n")
        if parser is not None:
            aManager.fileText = self.fileText
            parser.parseConstraints(aManager)

        return aManager

    def loadFile(self):
        """
        """

        with open(self.fileName, 'r') as file_in:
            self.fileText = file_in.read().upper()

        return constraintParser.findConstraintType(self.fileText)


class imConstraintSetManager(object):
    """Class to manage an immutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, managerName):
        self.constraints = ()
        self.name = managerName
        self.index = -1

    def __str__(self):
        return self.name + " contains " + str(len(self.constraints)) + " constraints.\n"

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    def __iter__(self):
        return self

    def next(self):
        """
        """
        if self.index == len(self.constraints) - 1:
            self.index = -1
            raise StopIteration
        self.index += 1
        return self.constraints[self.index]

    # Constraints management methods

    def setPDB(self, structure):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.structure = structure
        for constraint in self.constraints:
            constraint.structureName = self.structure

    def associateToPDB(self):
        """read strutural data
        """
        if self.structure != '':
            setPDB(self.structure)
            if self.constraints:
                return 1
        return 0

    def constraintsManagerForDataType(self, dataType):
        """
        """
        newManager = imConstraintSetManager(self.name + str(dataType))
        newManager.constraints = tuple(constraint for constraint in self.constraints if constraint.type == dataType)
        return newManager

    def constraintsManagerForAtoms(self, atomDefinitions):
        """
        """
        newManager = imConstraintSetManager(self.name + " for atoms " + str(atomDefinitions))
        newConstraints = set()
        for constraint in self.constraints:
            for atom in constraint.atoms:
                if atom in atomDefinitions:
                    newConstraints.add(constraint)
        newManager.constraints = tuple(newConstraints)
        return newManager

    @property
    def residuesList(self):
        """
        """
        resis = set()
        for constraint in self.constraints:
            resis.update(number for number in constraint.getResisNumber())
        return resis

    def intersection(self, anotherManager):
        """
        """
        newManager = imConstraintSetManager("")
        if isinstance(anotherManager, imConstraintSetManager):
            newManager.constraints = tuple(constraint for constraint in self.constraints if constraint in anotherManager)
            newManager.name = self.name + anotherManager.name
        return newManager

    @property
    def atomsList(self):
        """
        """
        atomList = set()
        for constraint in self.constraints:
            atomList.update(constraint.atoms)
        return atomList

    def setPartnerAtoms(self, AtomSelection):
        """
        """
        self.partnerManager = self.constraintsManagerForAtoms(AtomSelection)

    def areAtomsPartner(self, anAtom):
        """
        """
        if anAtom in self.partnerManager.atomsList:
            return True
        else:
            return False


class ConstraintSetManager(imConstraintSetManager):
    """Class to manage a mutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, managerName):
        super(ConstraintSetManager, self).__init__(managerName)
        self.constraints = []
        self.structure = ''
        self.format = ""
        self.fileText = ""

    # Constraints management methods

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

    def addConstraints(self, constraints):
        """
        """
        for constraint in constraints:
            self.addConstraint(constraint)

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) <= len(self.constraints):
            del self.constraints[int(aConstraintNumber)]


alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class constraintParser(object):
    """
    """

    XEASYReg = re.compile(r'\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\w+\s+\d+')
    AtTypeReg = re.compile('[CHON][A-Z]*')

    def __init__(self, text):
        """
        """
        self.text = (aLine.strip() for aLine in text.split('\n'))
        self.inFileTab = list()
        self.segments = list()

    def parseConstraints(self, aManager):
        """
        """
        self.prepareFile()
        constraint_number = 0
        for parsingResult in self.parseAConstraint():
            if parsingResult is not None:
                if len(parsingResult["residues"]) == 2:  # 2 residues (matches also H-Bonds)
                    for residue in parsingResult["residues"]: # filters H-Bonds
                        if residue['name'] == "O":
                            break
                    else:
                        aConstraint = NOE()
                        # No other constraint type supported ... for now !
                        aConstraint.id["number"] = constraint_number
                        aConstraint.definition = parsingResult["definition"]
                        aConstraint.atoms = NOE.addAtoms(constraintParser.parseAtoms(parsingResult["residues"]))
                        aConstraint.setConstraintValues(parsingResult["values"][0],
                                                        parsingResult["values"][1],
                                                        parsingResult["values"][2])

                        aManager.addConstraint(aConstraint)
                        constraint_number += 1

            else:
                stderr.write("Error while loading : " + parsingResult["definition"])

    def prepareFile(self):
        """
        """
        raise NotImplementedError

    def parseAConstraint(self):
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
        residues = list()
        for aResult in parsingResult:
            currentResidue = dict()
            if "resid" in aResult:
                currentResidue["resi_number"] = int(aResult["resid"])
            else:
                currentResidue["resi_number"] = int(aResult["resi"])
            currentResidue["atoms"] = aResult["name"]
            currentResidue["segid"] = aResult.get("segid", 'A')

            residues.append(currentResidue)
        return residues


class CNSParser(constraintParser):
    """
    """
    ParReg = re.compile('[()]')  # used in cns constraints loading. Suppression of ()
    SParReg = re.compile(r"\(.*\)")  # used in cns constraint loading.
    RegResi = re.compile(r"RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#]*")  # match CNS Residue definition
    SharpReg = re.compile('[#]')  # used in cns constraints loading. Replace # by *
    RegSeg = re.compile(r'SEGI\w*\s+[\w\d]*')  # match CNS segid definition
    RegFloat = re.compile(r'\s+[-+]?[0-9]*\.?[0-9]+'*3)

    def __init__(self, text):
        """
        """
        constraintParser.__init__(self, text)
        self.validConstraints = list()

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
        self.validConstraints = [constraint for constraint in self.validConstraints if re.search(r'\d', constraint)]

    def parseAConstraint(self):
        """Split CNS/XPLOR type constraint into an array, contening the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        """
        for aCNSConstraint in self.validConstraints:
            try:
                residuesList = CNSParser.RegResi.findall(aCNSConstraint, re.IGNORECASE)
                segments = CNSParser.RegSeg.findall(aCNSConstraint, re.IGNORECASE)
                for segment in segments:
                    if segment not in self.segments:
                        self.segments.append(segment)
                numberOfSegments = len(segments)

                constraintParsingResult = dict()
                residues = list()
                for (indice, aResidue) in enumerate(residuesList):
                    residueParsingResult = dict()
                    for aDefinition in CNSParser.SharpReg.sub('*', aResidue).split("AND "):
                        definitionArray = aDefinition.split()
                        residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()
                    if numberOfSegments > 0:
                        residueParsingResult["segid"] = alphabet[self.segments.index(segments[indice])]
                    else:
                        residueParsingResult["segid"] = "A"
                    residues.append(residueParsingResult)
                constraintParsingResult["residues"] = residues

                if 'OR ' in aCNSConstraint:
                    self.constraintAmbiguity(constraintParsingResult["residues"])

                constraintParsingResult["values"] = self.constraintValues(aCNSConstraint)
                constraintParsingResult["definition"] = aCNSConstraint

            except:
                stderr.write('Can not parse : ' + aCNSConstraint + '\n')
                constraintParsingResult = None
            yield constraintParsingResult

    @staticmethod
    def constraintAmbiguity(constraintParsingResult):
        """
        """
        if constraintParsingResult[0] == constraintParsingResult[2] or constraintParsingResult[0] == constraintParsingResult[3]:
            indiceAmbiguous = 1
        else:
            indiceAmbiguous = 0
        constraintParsingResult[indiceAmbiguous]['name'] = constraintParsingResult[indiceAmbiguous]['name'][0:-1] + "*"
        constraintParsingResult = [constraintParsingResult[0], constraintParsingResult[1]]

    @staticmethod
    def constraintValues(aCNSConstraint):
        """
        """
        constraintValues = CNSParser.RegFloat.findall(aCNSConstraint)
        if constraintValues:
            constraintValuesList = constraintValues[0].split()
        else:
            constraintValuesList = tuple()
        return [float(aValue) for aValue in constraintValuesList]


class CYANAParser(constraintParser):
    """
    """
    AtTypeReg = re.compile('[CHON][A-Z]*')

    def prepareFile(self):
        """
        """
        self.inFileTab = self.text

    def parseAConstraint(self):
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
        if atType.count('Q'):
            newType = atType.replace('Q', 'H', 1)
            newType = newType + ('*')  # Q is replaced by H and a star at the end of the atom type
            newType = newType.replace('Q', '')  # avoid QQ (QQD-> HD*)
            return newType
        else:
            return atType

"""Module for drawing constraints
"""


class ConstraintDrawer(object):
    """

    """
    def __init__(self, UnSatisfactionMarker="", SatisfactionMarker=""):
        """
        """
        self.UnSatisfactionMarker = UnSatisfactionMarker
        self.SatisfactionMarker = SatisfactionMarker

    def drC(self, selectedConstraints, radius, colors):
        """
        Draw an array of constraints according to the filter defined by user,
        using the drawConstraint function
        """
        for aConstraint in selectedConstraints:
            if aConstraint.satisfaction == 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction == 'Satisfied':
                color = colors['Satisfied']
            drawConstraint(aConstraint.points, color, radius,
                               self.IDConstraint(aConstraint,
                                                 self.UnSatisfactionMarker,
                                                 self.SatisfactionMarker))

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
        """
        densityStep = 10
        constraintList = dict()
        for aConstraint in selectedConstraints:
            for resi in aConstraint.resis:
                constraintList[resi['number']] = constraintList.get(resi['number'], 0) + densityStep

        return constraintList

    def paD(self, selectedConstraints, structure, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        zeroBFactors(structure)
        for residu, density in densityList.iteritems():
            setBfactor(structure, residu, density)
        paintDensity(color_gradient, structure)
        return densityList

    @staticmethod
    def IDConstraint(aConstraint, UnSatisfactionMarker, SatisfactionMarker):
        """Returns name of constraints :
        Name_(constraint number)_(structureName)_(violation_state)
        """
        if aConstraint.satisfaction != '':
            if aConstraint.satisfaction == 'unSatisfied':
                marker = UnSatisfactionMarker
            else:
                marker = SatisfactionMarker
            return aConstraint.id['name'] + str(aConstraint.id['number']) + marker + aConstraint.structureName
        else:
            stderr.write("Can not give ID : Violation state not defined for constraint : " +
                         aConstraint.structureName + "_" +
                         aConstraint.id['name'] +
                         str(aConstraint.id['number']) + "\n" +
                         str(aConstraint) +
                         "\n")

"""Module for error logging
"""

error_messages = []


def add_error_message(message):
    """
    """
    error_messages.append(str(message))


def get_error_messages():
    """
    """
    for message in error_messages:
        yield message

def erase_all_error_messages():
    """
    """
    del error_messages[:]


class ConstraintFilter(object):
    """

    """

    def __init__(self, structure, residuesList, dist_range, violationState,
                 violCutoff, method, RangeCutOff):
        """Defines parameters for filtering the constraints
        """
        self.residuesList = residuesList
        self.range = dist_range
        self.violationState = violationState
        self.cutOff = violCutoff
        self.structure = structure
        self.method = method
        self.rangeCutOff = RangeCutOff

    def filterAConstraint(self, aConstraint):
        """Filter the constraints to be drawn.
        """
        if aConstraint.getRange(self.rangeCutOff) in self.range:
            if [aResiNumber for aResiNumber in aConstraint.getResisNumber() if aResiNumber in self.residuesList]:
                if aConstraint.isValid():
                    if aConstraint.setValueFromStructure():
                        aConstraint.setViolationState(self.cutOff)
                        if aConstraint.isSatisfied() in self.violationState:
                            return True
                    else:
                        add_error_message("Distance issue with constraint :\n" + aConstraint.definition)
                else:
                    add_error_message("Selection issue with constraint :\n" + aConstraint.definition)
        return False

    def filterConstraints(self, constraintList):
        """
        """
        setPDB(self.structure)
        set_method(self.method)
        selectedConstraints = [constraint for constraint in constraintList if self.filterAConstraint(constraint)]
        stderr.write("\n".join(get_error_messages()) + '\n')
        erase_all_error_messages()
        return selectedConstraints

distance_method = ""


def set_method(newMethod):
    """
    """
    global distance_method
    distance_method = newMethod


def centerOfMass(coords):
    """ Adapted from : Andreas Henschel 2006
    assumes equal weights for atoms (usually protons)
    """

    if coords:
        sumCoords = (sum(coord) for coord in zip(*coords))
        numCoords = len(coords)
        return [coord/numCoords for coord in sumCoords]
    else:
        return [0, 0, 0]


def calcDistance(coord_init, coord_final):
    """    Calculate distance according to :
    ((sum of all distances^-6)/number of distances)^-1/6
    or (sum of all distances^-6)^-1/6
    """
    result = 0.0

    if coord_init and coord_final:
        distance_list = [sqrt(sum((coord[0] - coord[1]) ** 2 for coord in zip(AtomA, AtomB))) for AtomA in coord_init for AtomB in coord_final]
        if len(distance_list) > 1:
            try:
                sum6 = sum(pow(distance, -6) for distance in distance_list)
                if distance_method == 'ave6':
                    result = pow(sum6/len(distance_list), -1./6)
                elif distance_method == 'sum6':
                    result = pow(sum6, -1./6)
            except ValueError:
                add_error_message("Problem using coordinates : " +
                                         str(coord_init) + " " +
                                         str(coord_final) + "\n" +
                                         " and distances list" +
                                         str(distance_list) + "\n")
        else:
            result = distance_list[0]
    return result

lastDigit = re.compile(r'\d(\b|\Z)')  # look for last digit of atom type (used in AtomSet)

pdb = {}

try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def setPDB(structure):
        """
        """
        list_atoms = PymolCmd.get_model(str(structure))
        pdb.clear()
        pdb['name'] = str(structure)

        for atom in list_atoms.atom:
            signature = atom.get_signature().split(":")
            pdb.setdefault(signature[3], []).append({'name': signature[5],
                                                     'coord': atom.coord,
                                                     'segi': atom.chain})

        #with open(structure+".pyn", 'w') as fout:
        #    pickle.dump(pdb, fout)

    def select(selectionName, selection):
        if selectionName == "":
            return PymolCmd.select(selection)
        else:
            return PymolCmd.select(selectionName, selection)

    def get_model(model):
        return PymolCmd.get_model(model)

    def alterBFactors(structure, bFactor):
        PymolCmd.alter(structure, "b=" + str(bFactor))

    def spectrum(color_gradient, structure):
        PymolCmd.spectrum("b", color_gradient, structure)

    def zoom(selection):
        PymolCmd.zoom(selection)

    def drawConstraint(points, color, aRadius, ID):
        """used to draw a NOE constraint between two sets of atoms
                using cgo from Pymol
        """
        cons = [CYLINDER] + list(points[0]) + list(points[1]) + [aRadius] + color
        PymolCmd.load_cgo(cons, ID)

    def delete(selectionName):
        PymolCmd.delete(selectionName)

    def get_names():
        return PymolCmd.get_names()


except ImportError:
    def select(selectionName, selection):
        return []

    def get_model(model):
        return []

    def alterBFactors(structure, bFactor):
        pass

    def spectrum(color_gradient, structure):
        pass

    def drawConstraint(points, color, aRadius, ID):
        stdout.write("Drawn " + ID + " between points " + str(points) + " with " + str(color) + " color and radius " + str(aRadius) +"\n")

    def zoom(selection):
        pass

    def delete(selectionName):
        pass

    def get_names():
        return [fileName.split(".")[0] for fileName in os.listdir(os.getcwd()) if '.pyn' in fileName]

    def getID(atomSet):
        return ""

    def setPDB(structure):
        """
        """
        with open(structure + ".pyn", 'r') as fin:
            pdb.update(pickle.load(fin))


def zeroBFactors(structure):
    alterBFactors(structure, 0)


def setBfactor(structure, residu, bFactor):
    alterBFactors(structure + " & i. " + residu, bFactor)


def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)


def checkID(atomSet):
    """
    """
    check = False
    newName = ""
    error_message = ""
    if str(atomSet.resi_number) in pdb:
        if atomSet.segid in (atom['segi'] for atom in pdb[str(atomSet.resi_number)]):
            if atomSet.atoms in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                check = True
            else:
                if '*' not in atomSet.atoms:
                    if atomSet.atoms == 'HN':
                        newName = 'H'
                    elif atomSet.atoms == 'H':
                        newName = 'HN'
                    elif lastDigit.search(atomSet.atoms):
                        digit = lastDigit.search(atomSet.atoms).group()[0]
                        newName = digit + lastDigit.sub('', atomSet.atoms)  # put final digit at the beginning
                    if newName in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                        check = True
                    else:
                        error_message = "Atom name not found"
                else:
                    nameRoot = atomSet.atoms.replace('*', '')
                    for aName in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                        if nameRoot in aName:
                            check = True
                            break
                    if check is False:
                        error_message = "Atom name not found"
        else:
            error_message = "Wrong segment / chain"
    else:
        error_message = "Residue number not found"
    if check is False:
        add_error_message("Can't find " + str(atomSet.atoms) + " in structure " + pdb['name'] + " because : " + error_message)
    if newName:
        return {'valid': check, 'NewData': {'atoms': newName}}
    else:
        return {'valid': check, 'NewData': ''}


def get_coordinates(atomSet):
    """
    """
    coordinates = list()
    if '*' in atomSet.atoms:
        nameRoot = atomSet.atoms.replace('*', '')
        for atom in pdb[str(atomSet.resi_number)]:
            if atomSet.segid == atom['segi']:
                if nameRoot in atom['name']:
                    coordinates.append(atom['coord'])
    else:
        for atom in pdb[str(atomSet.resi_number)]:
            if atomSet.segid == atom['segi']:
                if atomSet.atoms == atom['name']:
                    coordinates = [atom['coord']]
                    break
    return coordinates

def createSelection(structure, Atoms):
    """
    """
    selection = structure + " and ("
    selection += " ".join("chain {} and resi {} and name {} +".format(atom.segid, atom.resi_number, atom.atoms) for atom in sorted(Atoms))
    return selection.rstrip("+") + ")"

def getModelsNames(satisfactionMarker="", unSatisfactionMarker=""):
    """
    """
    objectsLists = get_names()
    return [name for name in objectsLists if not (name.find(unSatisfactionMarker) >= 0 or name.find(satisfactionMarker) >= 0)]


class NMRCore(object):
    """Low Level Interface Class
    for loading and displaying constraints
    """
    def __init__(self):
        self.ManagersList = {}
        self.constraintFilter = ""
        self.displayedConstraints = ConstraintSetManager('displayed')

    def loadNOE(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = path.basename(filename)
        loader = ConstraintLoader(filename, managerName)
        self.ManagersList[managerName] = loader.loadConstraintsFromFile()

    def showSticks(self, managerName, structure, colors, radius,
                   UnSatisfactionMarker, SatisfactionMarker):
        """Seeks for constraints that fit criteria, increases a counter for
        each residue which has a matching constraint.
        """
        self.ManagersList[managerName].setPDB(structure)
        drawer = ConstraintDrawer(UnSatisfactionMarker, SatisfactionMarker)
        if self.ManagersList[managerName]:
            if self.ManagersList[managerName].associateToPDB():
                filteredConstraints = self.constraintFilter.filterConstraints(
                    self.ManagersList[managerName])
                selectedConstraints = [constraint for constraint in filteredConstraints if constraint not in self.displayedConstraints]
                drawer.drC(selectedConstraints, radius, colors)
                self.displayedConstraints.addConstraints(selectedConstraints)
                if len(selectedConstraints) > 0:
                    selection = createSelection(self.ManagersList[managerName].structure, self.displayedConstraints.atomsList)
                    select('NOE', selection)
                    zoom(selection)
        else:
            sys.stderr.write("No constraints to draw ! You might want to load a few of them first ...\n")

    def showNOEDensity(self, managerName, structure, gradient):
        """Seeks for constraints that fit criteria, increases a counter for
        each residue which has a matching constraint. That simulates a density
        which is then paint on the model according to a color gradient
        """
        self.ManagersList[managerName].setPDB(structure)
        drawer = ConstraintDrawer()
        if self.ManagersList[managerName]:
            if self.ManagersList[managerName].associateToPDB():
                selectedConstraints = self.constraintFilter.filterConstraints(
                    self.ManagersList[managerName])
                self.displayedConstraints.addConstraints(selectedConstraints)
                densityList = drawer.paD(selectedConstraints,
                                         self.ManagersList[managerName].structure,
                                         gradient)
                if densityList:
                    zoomSelection = createSelection(self.ManagersList[managerName].structure, densityList.keys())
                    zoom(zoomSelection)
                    select('involRes', zoomSelection)

    def commandsInterpretation(self, structure, managerName, residuesList, dist_range,
                               violationState, violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if residuesList == 'all':
            resList = self.ManagersList[managerName].residuesList
        else:
            resList = set()
            for resi_range in residuesList.split("+"):
                aRange = resi_range.split("-")
                if 1 <= len(aRange) <= 2:
                    resList.update([str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[-1]) + 1)])
                else:
                    sys.stderr.write("Residues set definition error : " +
                                     residuesList + "\n")

        if not isinstance(dist_range, list):
            if dist_range == 'all':
                dist_range = ['intra', 'sequential', 'medium', 'long']
            else:
                dist_range = [dist_range]

        if not isinstance(violationState, list):
            if violationState == 'all':
                violationState = ['unSatisfied', 'Satisfied']
            else:
                violationState = [violationState]
        self.constraintFilter = ConstraintFilter(structure, resList, dist_range,
                                                 violationState, violCutoff,
                                                 method, rangeCutOff)

    def cleanScreen(self, managerName):
        """Remove all sticks from pymol
        """
        self.displayedConstraints.removeAllConstraints()
        delete(managerName + "*")

    def saveConstraintsFile(self, aManagerName, fileName):
        """Save the selected constraint file under the format
        it has been loaded.
        """
        with open(fileName, 'w') as fout:
            fout.write(self.ManagersList[aManagerName].fileText)

    def downloadFromPDB(self, pdbCode, url):
        """Download constraint file from wwwPDB
        if available.
        """
        PDBfileName = pdbCode.lower() + ".mr"
        zippedFileName = PDBfileName + ".gz"
        workdir = os.getcwd()
        tempDownloadDir = tempfile.mkdtemp()
        os.chdir(tempDownloadDir)
        try:
            restraintFileRequest = urllib2.urlopen(urllib2.Request(url+zippedFileName))
            localFile = open(zippedFileName, 'wb')
            shutil.copyfileobj(restraintFileRequest, localFile)
            localFile.close()
            restraintFileRequest.close()
            with gzip.open(zippedFileName, 'rb') as zippedFile:
                decodedFile = zippedFile.read()
                with open(PDBfileName, 'w') as restraintFile:
                    restraintFile.write(decodedFile)
            if path.exists(zippedFileName):
                os.remove(zippedFileName)
                self.loadNOE(PDBfileName)
                os.remove(PDBfileName)
                os.chdir(workdir)
                os.removedirs(tempDownloadDir)
        except IOError:
            sys.stderr.write("Error while downloading or opening " +
                             pdbCode + " NMR Restraints file from PDB.\n")


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
            check = checkID(atomSet)
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
        return [atom.resi_number for atom in self.atoms]

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



class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        """
        """
        super(NOE, self).__init__()
        self.points = tuple()
        self.numberOfAtomsSets = 2
        self.type = "NOE"

    def getRange(self, RangeCutOff):
        """Return the range name,
        range depends on the number of residus between the atomsets
        """
        if self.atoms[0].segid == self.atoms[1].segid:
            resi_diff = abs(int(self.atoms[0].resi_number) - int(self.atoms[1].resi_number))
            if resi_diff == 0:
                return 'intra'
            elif resi_diff == 1:
                return 'sequential'
            elif resi_diff > 1 and resi_diff <= RangeCutOff:
                return 'medium'
            else:
                return 'long'
        else:
            return 'long'

    def setValueFromStructure(self):
        """
        """
        return self.setDistance()

    def setDistance(self):
        """Set actual distance of the constraint in the current structure file
        """
        self.points = tuple(centerOfMass(get_coordinates(atom)) for atom in self.atoms)

        self.constraintValues['actual'] = calcDistance(get_coordinates(self.atoms[0]),
                                                       get_coordinates(self.atoms[1]))
        if self.constraintValues['actual'] <= 0.0:
            return False
        else:
            return True




class NOEDataViewer(Tk.Toplevel):
    """
    """
    def __init__(self, dataController):
        """
        """
        Tk.Toplevel.__init__(self, class_='NOEDataViewer')
        self.labelFrame = ttk.LabelFrame(self, text='Select NOE residue and / or atom to see their counterparts :')
        self.NOEDataController = dataController
        self.title("NOE from " + dataController.name)
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self.labelFrame,
                                          textvariable=self.constraintSelectionText,
                                          justify=Tk.CENTER)
        self.resiListVarDisplayed = Tk.StringVar()
        self.resiScrollListDisplayed = ScrolledList(self.labelFrame,
                                                                 listvariable=self.resiListVarDisplayed,
                                                                 selectmode=Tk.EXTENDED,
                                                                 width=10)
        self.resiListDisplayedController = resiNumberListController()
        self.resiListVarPartner = Tk.StringVar()
        self.resiScrollListPartner = ScrolledList(self.labelFrame,
                                                               listvariable=self.resiListVarPartner,
                                                               selectmode=Tk.EXTENDED,
                                                               width=10)
        self.resiListPartnerController = resiNumberListController()
        self.atomListVarDisplayed = Tk.StringVar()
        self.atomScrollListDisplayed = ScrolledList(self.labelFrame,
                                                                 listvariable=self.atomListVarDisplayed,
                                                                 width=10)
        self.atomListDisplayedController = atomTypeListController()
        self.atomListVarPartner = Tk.StringVar()
        self.atomScrollListPartner = ScrolledList(self.labelFrame,
                                                               listvariable=self.atomListVarPartner,
                                                               width=10)
        self.atomListPartnerController = atomTypeListController()
        self.NOEValues = dict()
        self.NOEValueLabels = dict()
        for valueType in ('constraint', 'min', 'plus', 'actual'):
            self.NOEValues[valueType] = Tk.DoubleVar()
            self.NOEValueLabels[valueType] = ttk.Label(self.labelFrame, textvariable=self.NOEValues[valueType], width=3)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.labelFrame.grid(row=0, column=0)
        self.labelConstraints.grid(row=0, column=0, columnspan=8)
        for index, labelName in enumerate(['1st Residue', '1st Atom', '2nd Residue', '2nd Atom']):
            ttk.Label(self.labelFrame, text=labelName).grid(row=1, column=index * 2, columnspan=2)
        self.resiScrollListDisplayed.grid(row=2, column=0, columnspan=2)
        self.atomScrollListDisplayed.grid(row=2, column=2, columnspan=2)
        self.resiScrollListPartner.grid(row=2, column=4, columnspan=2)
        self.atomScrollListPartner.grid(row=2, column=6, columnspan=2)
        columnPosition = 0
        for key, aLabel in self.NOEValueLabels.iteritems():
            aLabel.grid(row=3, column=columnPosition + 1)
            aLabel.state(['disabled'])
            ttk.Label(self.labelFrame, text=key).grid(row=3, column=columnPosition, sticky=Tk.W)
            columnPosition += 2

        self.resiScrollListDisplayed.bind('<<ListboxSelect>>', self.selectResidueDisplayed)
        self.atomScrollListDisplayed.bind('<<ListboxSelect>>', self.selectAtomDisplayed)
        self.resiScrollListPartner.bind('<<ListboxSelect>>', self.selectResiduePartner)
        self.fillResListDisplayed()
        self.constraintSelectionText.set(str(len(self.NOEDataController)) +
                                         " constraints used, involving " +
                                         str(len([residue for residue in self.NOEDataController.getResiduesList()])) +
                                         " residues")
        self.atomScrollListPartner.bind('<<ListboxSelect>>', self.selectAtomPartner)

    def fillResListDisplayed(self):
        """
        """

        self.resiScrollListDisplayed.clear()
        self.atomScrollListDisplayed.clear()
        self.resiScrollListPartner.clear()
        self.atomScrollListPartner.clear()
        self.resiListDisplayedController.atomsList = self.NOEDataController.displayedAtoms
        self.resiListVarDisplayed.set(" ".join(self.resiListDisplayedController.resiNumberList))

    def selectResidueDisplayed(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        residue_selection = [w.get(resi_number_index) for resi_number_index in selection]

        self.atomListVarDisplayed.set('')
        self.atomListVarPartner.set('')
        self.resiListVarPartner.set('')

        self.switchLabelsState(['disabled'])

        selectedAtoms = list()
        for residue in residue_selection:
            selectedAtoms.extend(self.resiListDisplayedController.resiNumberList[residue.replace(" ", "\ ")])
        if len(selection) > 0:
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            self.resiListPartnerController.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVarPartner.set(" ".join(self.resiListPartnerController.resiNumberList))

            if len(selection) == 1:
                self.atomListDisplayedController.selectedAtoms = selectedAtoms
                self.atomListVarDisplayed.set(" ".join(self.atomListDisplayedController.atomTypeList))

            zoomSelect = createSelection(self.NOEDataController.structure, self.resiListPartnerController.atomsList+selectedAtoms)
            zoom(zoomSelect)
            delete('involRes')
            select('involRes', zoomSelect)

    def selectAtomDisplayed(self, evt):
        """
        """
        self.switchLabelsState(['disabled'])
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        self.resiListVarPartner.set('')
        self.atomListVarPartner.set('')

        selectedAtoms = [self.atomListDisplayedController.atomTypeList[atomType] for atomType in atomType_selection]

        if len(selection) == 1:
            self.NOEDataController.setSelectedAtoms(selectedAtoms[0])
            self.resiListPartnerController.atomsList = self.NOEDataController.partnerAtoms
            self.resiListVarPartner.set(" ".join(self.resiListPartnerController.resiNumberList))
            zoomSelect = createSelection(self.NOEDataController.structure, self.resiListPartnerController.atomsList+selectedAtoms[0])
            zoom(zoomSelect)
            delete('involRes')
            select('involRes', zoomSelect)

    def selectResiduePartner(self, evt):
        """
        """
        self.switchLabelsState(['disabled'])
        w = evt.widget
        selection = w.curselection()

        if len(selection) == 1:
            self.atomListVarPartner.set('')

            if len(self.atomScrollListDisplayed.curselection()) == 1:

                partnerResidue_selection = [w.get(resi_number_index) for resi_number_index in selection]

                selectedPartnerAtoms = [self.resiListPartnerController.resiNumberList[residue.replace(" ", "\ ")] for residue in partnerResidue_selection]

                self.atomListPartnerController.selectedAtoms = selectedPartnerAtoms[0]
                self.atomListVarPartner.set(" ".join(self.atomListPartnerController.atomTypeList))
                zoomSelect = createSelection(self.NOEDataController.structure, self.NOEDataController.selectedAtoms+selectedPartnerAtoms[0])
                zoom(zoomSelect)
                delete('involRes')
                select('involRes', zoomSelect)

    def selectAtomPartner(self, evt):
        """
        """
        w = evt.widget
        selection = w.curselection()
        atomType_selection = [w.get(atom_number_index) for atom_number_index in selection]
        selectedPartnerAtoms = [self.atomListPartnerController.atomTypeList[atomType] for atomType in atomType_selection]

        if len(selection) == 1:
            zoomSelect = createSelection(self.NOEDataController.structure, selectedPartnerAtoms[0]+self.NOEDataController.selectedAtoms)
            zoom(zoomSelect)
            delete('involRes')
            select('involRes', zoomSelect)

            constraintValues = self.NOEDataController.constraintValueForAtoms(selectedPartnerAtoms[0]+self.NOEDataController.selectedAtoms)
            if constraintValues:
                for key, value in self.NOEValues.iteritems():
                    value.set(round(float(constraintValues[0][0][key]), 1))
                self.switchLabelsState(['!disabled'])
                style = ttk.Style()
                if constraintValues[0][1] is 'unSatisfied':
                    style.configure("Red.TLabel", foreground="red")
                    self.NOEValueLabels['constraint'].configure(style="Red.TLabel")
                if constraintValues[0][1] is 'Satisfied':
                    style.configure("Green.TLabel", foreground="green")
                    self.NOEValueLabels['constraint'].configure(style="Green.TLabel")

    def switchLabelsState(self, state):
        """
        """
        if 'disabled' in state:
            for value in self.NOEValues.itervalues():
                value.set(0)
        for aLabel in self.NOEValueLabels.itervalues():
            aLabel.state(state)


class NMRGUI(Tk.Toplevel):
    """
    """
    def __init__(self):
        """
        """
        Tk.Toplevel.__init__(self)
        self.title('PymolNMR')
        self.resizable(0, 0)
        self.noteBook = ttk.Notebook(self)
        self.mainPanel = mainPanel(self.noteBook)
        self.preferencesPanel = PreferencesPanel(self.noteBook)
        self.About = About(self.noteBook)
        self.panelsList = []

    def createPanels(self):
        """Main Frames (not IBM ;-)
        """

        self.noteBook.grid(row=0, column=0)

        self.noteBook.add(self.mainPanel, text="Main")
        self.panelsList.append(self.mainPanel)

        self.panelsList.append(self.preferencesPanel)
        self.noteBook.add(self.preferencesPanel, text="Preferences")

        self.noteBook.add(self.About, text="Help")

    def startGUI(self):
        """
        """
        self.createPanels()
        self.setDelegations()

    def setDelegations(self):
        """
        """
        self.mainPanel.NOEDrawing.mainGUI = self
        self.preferencesPanel.mainGUI = self
        self.mainPanel.fileSelection.mainGUI = self

    def getInfo(self):
        """
        """
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos



class About(ttk.Frame):
    """
    """
    def __init__(self, master=None):
        """
        """
        ttk.Frame.__init__(self, master)
        self.aboutFrame = ttk.LabelFrame(self, text=u'About')
        self.aboutFrame.grid(row=1, column=0)
        ttk.Label(self.aboutFrame, justify=Tk.CENTER, text=u"This Pymol plugin" +
                  " has been written \nbecause I thought it would be useful to" +
                  "check \nmy NOEs during my postdocship. I hope it'll" +
                  " \nhelp you as well. Feel free to send \nany comments to " +
                  ": github.com/oserve/PyNMR\nThis plugin is free and may be " +
                  "copied as \nlong as you respect the copyright."
                  ).grid(row=0, column=0)
        self.helpFrame = ttk.LabelFrame(self, text=u'Quick Help')
        self.helpFrame.grid(row=0, column=0)
        ttk.Label(self.helpFrame, text=u'- First open a file or ' +
                  'download one frome the PDB\n  using a structure PDB code\n' +
                  '- Then select which type of constraint you want\n' +
                  '- You can select residue numbers (X+Y+Z)\n  or a range ' +
                  '(X-Z) or both (default is all)\n - After that, select the ' +
                  'structure you want\n to' +
                  ' display the constraints on.\n - Finally, click on the' +
                  ' display you want\n (sticks or colormap)'
                  ).grid(row=0, column=0)

"""
Definitions for application defaults
"""

configFileName = "pymolNMR.cfg"
defaults = {}

standardDefaults = {'radius': 0.03, 'cutOff': 0.3,
					'colors':
						{
							'Satisfied': [1, 1, 1, 1, 1, 1],
							'tooFar': [ 1, 0, 0, 1, 0, 0],
							'tooClose': [ 0, 0, 1, 0, 0, 1]
						},
		'gradient': 'blue_white_red', 'method': 'sum6',
		'UnSatisfactionMarker': '_US_', 'SatisfactionMarker': '_S_',
		'rangeCutOff': 5,
		'urlPDB': 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/',
		'gradientColorList' : [
            "blue_green", "blue_magenta", "blue_red", "blue_white_green",
            "blue_white_magenta", "blue_white_red", "blue_white_yellow",
            "blue_yellow", "cbmr", "cyan_magenta", "cyan_red",
            "cyan_white_magenta", "cyan_white_red", "cyan_white_yellow",
            "cyan_yellow", "gcbmry", "green_blue", "green_magenta",
            "green_red", "green_white_blue", "green_white_magenta",
            "green_white_red", "green_white_yellow", "green_yellow",
            "green_yellow_red", "magenta_blue", "magenta_cyan",
            "magenta_green", "magenta_white_blue", "magenta_white_cyan",
            "magenta_white_green", "magenta_white_yellow", "magenta_yellow",
            "rainbow", "rainbow2", "rainbow2_rev", "rainbow_cycle",
            "rainbow_cycle_rev", "rainbow_rev", "red_blue", "red_cyan",
            "red_green", "red_white_blue", "red_white_cyan", "red_white_green",
            "red_white_yellow", "red_yellow", "red_yellow_green", "rmbc",
            "yellow_blue", "yellow_cyan", "yellow_cyan_white", "yellow_green",
            "yellow_magenta", "yellow_red", "yellow_white_blue",
            "yellow_white_green", "yellow_white_magenta", "yellow_white_red",
            "yrmbcg"
            ]
        }


def registerDefaults(newDefaults):
    """
    """
    defaults.update(newDefaults)


def defaultForParameter(parameter):
    """
    """
    return defaults[parameter]


def setToStandardDefaults():
    """
    """
    defaults.update(standardDefaults)
    if path.exists(configFileName):
        os.remove(configFileName)


def saveDefaults():
    """
    """
    configFile = open(configFileName, 'w')
    pickle.dump(defaults, configFile)
    configFile.close()


def loadDefaults():
    """
    """
    if path.exists(configFileName):
        configFile = open(configFileName, 'r')
        defaults.update(pickle.load(configFile))
        configFile.close()
    else:
        setToStandardDefaults()



class ConstraintSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text=u"Constraints Selection")
        self.consRangeFrame = RangeSelectionPanel(self)
        self.violationsFrame = ViolationSelectionPanel(self)
        self.structureManagement = StructureSelectionPanel(self)
        self.panelsList = (self.consRangeFrame, self.violationsFrame, self.structureManagement)
        self.widgetCreation()

    def widgetCreation(self):
        # Creation of range input
        self.consRangeFrame.grid(row=0, column=0)

        # Creation of Violations inputs
        self.violationsFrame.grid(row=0, column=1)

        # Creation of structure inputs
        self.structureManagement.grid(row=1, column=0, columnspan=2)

    def getInfo(self):
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


class RangeSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Range Selection")

        self.RangesVars = {}
        self.RangesCB = {}
        self.RangesFunctions = {}
        self.ranges = ('intra', 'sequential', 'medium', 'long')
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, consRange in enumerate(self.ranges):
            self.RangesVars[consRange] = Tk.IntVar(self)
            self.RangesCB[consRange] = ttk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesVars["all"] = Tk.IntVar(self)
        self.RangesCB["all"] = ttk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition + 1, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        """
        """
        for consRange in self.ranges:
            self.RangesVars[consRange].set(self.RangesVars["all"].get())

    def tick(self):
        """
        """
        self.RangesVars["all"].set(1)
        for aRange in self.ranges:
            if self.RangesVars[aRange].get() == 0:
                self.RangesVars["all"].set(0)
                break

    def getInfo(self):
        """
        """
        ranges = [aRange for aRange in self.ranges if self.RangesVars[aRange].get() == 1]
        return {"residuesRange": ranges}


class ViolationSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Constraint state :")

        self.ViolationsVars = {}
        self.UnSatisfiedCB = {}
        self.cutOff = Tk.DoubleVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, violationType in enumerate(['unSatisfied', 'Satisfied']):
            self.ViolationsVars[violationType] = Tk.IntVar(self)
            self.UnSatisfiedCB[violationType] = ttk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatisfiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W, columnspan=2)
            self.ViolationsVars[violationType].set(1)

        rowPosition += 1
        ttk.Label(self, text=u'Distance CutOff :').grid(row=rowPosition,
                                                        column=0, columnspan=2)

        rowPosition += 1
        self.spinBox_cutOff = Tk.Spinbox(self, textvariable=self.cutOff,
                                         from_=0.0, to=10.0, increment=0.1,
                                         format='%2.1f', width=6)
        self.spinBox_cutOff.grid(row=rowPosition, column=0)
        ttk.Label(self, text=u'\u212b').grid(row=rowPosition, column=1)

    def getInfo(self):
        """
        """
        violationStates = [violationType for violationType in ['unSatisfied', 'Satisfied'] if self.ViolationsVars[violationType].get() == 1]
        return {"cutOff": self.cutOff.get(), "violationState": violationStates}


class StructureSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Structure")
        self.residueRanges = Tk.StringVar()
        self.structureList = Tk.StringVar()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u"Structure :").grid(row=0, column=0)
        self.comboPDB = ttk.Combobox(self, state='readonly',
                                     textvariable=self.structureList)
        self.comboPDB.grid(row=0, column=1)
        self.comboPDB.bind('<Enter>', self.updatePdbList)

        ttk.Label(self, text=u'Residues ranges :').grid(row=2, column=0, sticky=Tk.W)
        self.entry_res = ttk.Entry(self, textvariable=self.residueRanges)
        self.entry_res.grid(row=2, column=1)
        self.residueRanges.set('all')

    def getInfo(self):
        """
        """
        return {"structure": self.structureList.get(),
                "ranges": self.residueRanges.get()}

    def updatePdbList(self, event):
        """
        """
        infos = self.mainApp.NMRInterface.getInfo()
        self.comboPDB['values'] = getModelsNames(infos['SatisfactionMarker'], infos['UnSatisfactionMarker'])



class FileSelectionPanel(ttk.LabelFrame):
    """This panel allows to import constraint file
    into the Core. Also it allows the selection of the file
    for the following calculations.
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text="Constraints Files")
        self.constraintsFileList = Tk.StringVar()
        self.infoLabelString = Tk.StringVar()
        self.loadFileButton = ttk.Button(self, text=u"Load file",
                                        command=self.loadFile)
        self.removeFileButton = ttk.Button(self, text=u"Remove file",
                                          command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        self.downloadButton = ttk.Button(self, text=u"Download \nfrom PDB",
                                        command=self.downloadRestraintFileWin)
        self.saveButton = ttk.Button(self, text=u'Save File',
                                     command=self.saveFile)
        self.infoLabel = ttk.Label(self, textvariable=self.infoLabelString)
        self.selectedFile = ""
        self.widgetCreation()
        self.NMRCommands = ""  # Must be set by application at run time
        self.mainGUI = ""  # Must be set at run time

    def widgetCreation(self):
        """
        """
        self.constraintsList.listbox.exportselection = 0
        self.constraintsList.grid(row=0, column=1, rowspan=4)
        self.loadFileButton.grid(row=0, column=0)
        self.removeFileButton.grid(row=1, column=0)
        self.downloadButton.grid(row=2, column=0)
        self.saveButton.grid(row=3, column=0)
        self.infoLabel.grid(row=4, column=0, columnspan=2)
        self.constraintsList.bind('<<ListboxSelect>>', self.onStructureSelect)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint file")
        if len(filename):
            self.NMRCommands.loadNOE(filename)
            self.updateFilelist()

    def updateFilelist(self):
        """
        """
        managerList = " ".join(self.NMRCommands.ManagersList.keys()).strip()
        self.constraintsFileList.set(managerList)
        if len(managerList) == 0:
            self.infoLabelString.set('')
        else:
            self.constraintsList.listbox.activate(len(managerList) - 1)

    def removeFile(self):
        """
        """
        toRemove = self.selectedFile
        if toRemove:
            del self.NMRCommands.ManagersList[toRemove]
        self.updateFilelist()

    def saveFile(self):
        """
        """
        toSave = self.selectedFile
        if toSave:
            filename = tkFileDialog.asksaveasfilename(
                title="Save constraint file as", initialfile=toSave)
            if filename is not None:
                self.NMRCommands.saveConstraintsFile(toSave, filename)

    def downloadRestraintFileWin(self):
        """
        """
        pdbCode = tkSimpleDialog.askstring('PDB NMR Restraints',
                                           'Please enter a 4-digit pdb code:',
                                           parent=self)
        if pdbCode:
            infos = self.mainGUI.getInfo()
            self.NMRCommands.downloadFromPDB(pdbCode, infos["urlPDB"])
            self.updateFilelist()

    def onStructureSelect(self, evt):
        """
        """
        # Note here that Tkinter passes an event object
        w = evt.widget
        selection = w.curselection()
        if len(selection) == 1:
            index = int(selection[0])
            self.selectedFile = w.get(index)
            self.infoLabelString.set("Contains " +
                                     str(len(self.NMRCommands.ManagersList[self.selectedFile])) +
                                     " Constraints (" + self.NMRCommands.ManagersList[self.selectedFile].format + ")")

    def getInfo(self):
        """
        """
        if self.selectedFile:
            return {"constraintFile": self.selectedFile}
        else:
            return {"constraintFile": ""}



class mainPanel(ttk.Frame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.Frame.__init__(self, master)
        self.fileSelection = FileSelectionPanel(self)
        self.constraintPanel = ConstraintSelectionPanel(self)
        self.NOEDrawing = NOEDrawingPanel(self)
        self.panelsList = [self.fileSelection, self.constraintPanel]
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.fileSelection.grid(row=0, column=0)
        self.constraintPanel.grid(row=1, column=0)
        self.NOEDrawing.grid(row=2, column=0)

    def getInfo(self):
        """
        """
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


class NOEDrawingPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text="NOE Representation")
        self.sticksButton = ttk.Button(self, text="Sticks",
                                       command=self.showSticks)
        self.densityButton = ttk.Button(self, text="Density",
                                        command=self.showDensity)
        self.cleanButton = ttk.Button(self, text="Clean Sticks",
                                      command=self.cleanAll)
        self.mainGUI = ""  # Must be set at run time
        self.NMRCommands = ""  # Must be set by application at run time
        self.dataControllers = dict()
        self.dataViewers = dict()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.sticksButton.grid(row=0, column=0)
        self.densityButton.grid(row=0, column=1)
        self.cleanButton.grid(row=0, column=2)

    def showSticks(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["structure"],
                                                    infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            self.NMRCommands.showSticks(infos["constraintFile"],
                                        infos["structure"],
                                        infos["colors"],
                                        infos["radius"],
                                        infos["UnSatisfactionMarker"],
                                        infos["SatisfactionMarker"])

            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands,
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]])

    def showDensity(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["structure"],
                                                    infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            self.NMRCommands.showNOEDensity(infos["constraintFile"],
                                            infos["structure"],
                                            infos["gradient"])

            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands,
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]])

    def cleanAll(self):
        """Remove all displayed sticks
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen(infos["constraintFile"])
            self.dataViewers[self.mainGUI.getInfo()["constraintFile"]].destroy()
            del self.dataViewers[self.mainGUI.getInfo()["constraintFile"]]
            del self.dataControllers[self.mainGUI.getInfo()["constraintFile"]]

    def infoCheck(self, infos):
        """
        """
        check = 1
        for item in infos.values():
            if item == "":
                check = 0
                break
        return check



class SticksPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        self.satisfactions = ["Satisfied", "tooFar", "tooClose"]
        self.satisfactionColorButtons = {}
        ttk.LabelFrame.__init__(self, master, text=u"NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius,
                                         from_=0.00, to=0.5, increment=0.01,
                                         format='%1.2f', width=4)
        for satisfaction in self.satisfactions:
            self.satisfactionColorButtons[satisfaction] = ttk.Button(self,
                                                                     text=u"Choose color",
                                                                     command=lambda satisfaction=satisfaction: self.setColor(satisfaction))
        self.UnSatisfactionMarker = Tk.StringVar(self)
        self.SatisfactionMarker = Tk.StringVar(self)
        self.UnSatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.UnSatisfactionMarker, width=6)
        self.SatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.SatisfactionMarker, width=6)
        self.colors = {}
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Stick radius (\u212b):').grid(row=0, column=0)
        self.spinBox_Radius.grid(row=0, column=1)
        ttk.Label(self, text=u'Satisfied constraint').grid(row=1, column=0)
        self.satisfactionColorButtons["Satisfied"].grid(row=1, column=1)
        ttk.Label(self, text=u"Atoms too far").grid(row=2, column=0)
        self.satisfactionColorButtons["tooFar"].grid(row=2, column=1)
        ttk.Label(self, text=u"Atoms too close").grid(row=3, column=0)
        self.satisfactionColorButtons["tooClose"].grid(row=3, column=1)
        ttk.Label(self, text=u'Unsatisfied Marker :').grid(row=4, column=0)
        self.UnSatisfactionMarkerEntry.grid(row=4, column=1)
        ttk.Label(self, text=u'Satisfied Marker :').grid(row=5, column=0)
        self.SatisfactionMarkerEntry.grid(row=5, column=1)

    def setDefaults(self):
        """
        """
        self.colors = defaultForParameter("colors")
        self.UnSatisfactionMarker.set(defaultForParameter("UnSatisfactionMarker"))
        self.SatisfactionMarker.set(defaultForParameter("SatisfactionMarker"))
        self.radius.set(defaultForParameter("radius"))

    def getInfo(self):
        """
        """
        return {"radius": self.radius.get(),
                "colors": self.colors,
                "UnSatisfactionMarker": self.UnSatisfactionMarker.get(),
                "SatisfactionMarker": self.SatisfactionMarker.get()}

    def setColor(self, satisfaction):
        """
        """
        currentColor = self.float2hex(self.colors[satisfaction])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors[satisfaction] = self.int2floatColor(result[0])

    @staticmethod
    def int2floatColor(color):
        """
        """
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0,
                color[0]/255.0, color[1]/255.0, color[2]/255.0]

    @staticmethod
    def float2hex(color):
        """From stackoverflow
        """
        return '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))

class DensityPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE density Preferences")
        self.gradient = Tk.StringVar()
        self.gradientSelection = ttk.Combobox(self, state="readonly",
                                              textvariable=self.gradient)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Gradient :').grid(row=0, column=0)
        self.gradientSelection.grid(row=0, column=1)

    def getInfo(self):
        """
        """
        return {"gradient": self.gradient.get()}


class PreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE Preferences")
        self.panelsList = []
        self.methodsList = [(u"\u03a3 r-6", "sum6"), (u"(\u03a3 r-6)/n", "ave6")]
        self.selectedMethod = Tk.StringVar()
        self.sticksPanel = SticksPreferencesPanel(self)
        self.panelsList.append(self.sticksPanel)
        self.densityPanel = DensityPreferencesPanel(self)
        self.panelsList.append(self.densityPanel)
        self.savePrefButton = ttk.Button(self, text=u"Save preferences",
                                         command=self.savePrefs)
        self.resetButton = ttk.Button(self, text=u"Defaults",
                                      command=self.resetPrefs)
        self.rangeCutOff = Tk.IntVar(self)
        self.rangeCutOffEntry = Tk.Spinbox(self, textvariable=self.rangeCutOff,
                                           from_=1, to=20, increment=1, width=2)
        self.url = Tk.StringVar(self)
        self.urlTextField = ttk.Entry(self, textvariable=self.url)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, justify=Tk.CENTER, text=u'NOE Distance calculation :\n(> 2 atoms)').grid(
            row=0, column=0, rowspan=2)
        position = 0
        for methodName, method in self.methodsList:
            ttk.Radiobutton(self, text=methodName, variable=self.selectedMethod,
                            value=method).grid(row=position, column=1)
            position += 1

        ttk.Label(self, text=u'Residue range cut-off :').grid(row=position, column=0)

        self.rangeCutOffEntry.grid(row=position, column=1)
        position += 1
        self.sticksPanel.grid(row=position, column=0, columnspan=2)
        position += 1
        self.densityPanel.grid(row=position, column=0, columnspan=2)
        position += + 1
        ttk.Label(self, text=u'PDB.org URL for download').grid(row=position, column=0, columnspan=2)
        position += + 1
        self.urlTextField.grid(row=position, column=0, columnspan=2)
        position += 1
        self.savePrefButton.grid(row=position, column=0)
        self.resetButton.grid(row=position, column=1)

    def savePrefs(self):
        """
        """
        registerDefaults(self.mainGUI.getInfo())
        saveDefaults()

    def resetPrefs(self):
        """
        """
        setToStandardDefaults()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.densityPanel.gradient.set(defaultForParameter("gradient"))
        self.selectedMethod.set(defaultForParameter("method"))
        self.url.set(defaultForParameter("urlPDB"))
        self.rangeCutOff.set(defaultForParameter("rangeCutOff"))
        self.sticksPanel.setDefaults()

    def getInfo(self):
        """
        """
        infos = {"method": self.selectedMethod.get(),
                 "rangeCutOff": self.rangeCutOff.get(),
                 "urlPDB": self.url.get()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos

"""scrolledlist.py: A Tkinter widget combining a Listbox with Scrollbar(s).

  For details, see:
    http://www.nmt.edu/tcc/help/lang/python/examples/scrolledlist/
"""




DEFAULT_WIDTH = "20"
DEFAULT_HEIGHT = "10"


class ScrolledList(ttk.Frame):
    """A compound widget containing a listbox and up to two scrollbars.

      State/invariants:
        .listbox:      [ The Listbox widget ]
        .vScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .hScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .callback:     [ as passed to constructor ]
        .vscroll:      [ as passed to constructor ]
        .hscroll:      [ as passed to constructor ]
    """

    def __init__(self, master=None, width=DEFAULT_WIDTH,
                 height=DEFAULT_HEIGHT, vscroll=1, hscroll=0, callback=None,
                 listvariable=None, selectmode=Tk.BROWSE):
        """Constructor for ScrolledList.
        """
        # -- 1 --
        # [ self  :=  a new Frame widget child of master ]
        ttk.Frame.__init__(self, master)
        # -- 2 --
        self.width = width
        self.height = height
        self.vscroll = vscroll
        self.hscroll = hscroll
        self.callback = callback
        # -- 3 --
        # [ self  :=  self with all widgets created and registered ]
        self.__createWidgets(listvariable, selectmode)

    def __createWidgets(self, alistvariable, aselectmode):
        """Lay out internal widgets.
        """
        # -- 1 --
        # [ if self.vscroll ->
        #     self  :=  self with a vertical Scrollbar widget added
        #     self.vScrollbar  :=  that widget ]
        #   else -> I ]
        if self.vscroll:
            self.vScrollbar = ttk.Scrollbar(self, orient=Tk.VERTICAL)
            self.vScrollbar.grid(row=0, column=1, sticky=Tk.N+Tk.S)
        # -- 2 --
        # [ if self.hscroll ->
        #     self  :=  self with a horizontal Scrollbar widget added
        #     self.hScrollbar  :=  that widget
        #   else -> I ]
        if self.hscroll:
            self.hScrollbar = ttk.Scrollbar(self, orient=Tk.HORIZONTAL)
            self.hScrollbar.grid(row=1, column=0, sticky=Tk.E+Tk.W)
        # -- 3 --
        # [ self  :=  self with a Listbox widget added
        #   self.listbox  :=  that widget ]
        self.listbox = Tk.Listbox(self, relief=Tk.SUNKEN,
                                  width=self.width, height=self.height,
                                  borderwidth=2, listvariable=alistvariable,
                                  selectmode=aselectmode)
        self.listbox.grid(row=0, column=0)
        self.listbox.configure(exportselection=False)
        # -- 4 --
        # [ if self.vscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.vScrollbar can reposition it ]
        #     self.vScrollbar  :=  self.vScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.vscroll:
            self.listbox["yscrollcommand"] = self.vScrollbar.set
            self.vScrollbar["command"] = self.listbox.yview

        # -- 5 --
        # [ if self.hscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.hScrollbar can reposition it ]
        #     self.hScrollbar  :=  self.hScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.hscroll:
            self.listbox["xscrollcommand"] = self.hScrollbar.set
            self.hScrollbar["command"] = self.listbox.xview
        # -- 6 --
        # [ self.listbox  :=  self.listbox with an event handler
        #       for button-1 clicks that causes self.callback
        #       to be called if there is one ]
        self.listbox.bind("<Button-1>", self.__clickHandler)

    def __clickHandler(self, event):
        """Called when the user clicks on a line in the listbox.
        """
        # -- 1 --
        if not self.callback:
            return
        # -- 2 --
        # [ call self.callback(c) where c is the line index
        #   corresponding to event.y ]
        lineNo = self.listbox.nearest(event.y)
        self.callback(lineNo)
        # -- 3 --
        self.listbox.focus_set()

    def count(self):
        """Return the number of lines in use in the listbox.
        """
        return self.listbox.size()

    def __getitem__(self, k):
        """Get the (k)th line from the listbox.
        """

        # -- 1 --
        if 0 <= k < self.count():
            return self.listbox.get(k)
        else:
            raise IndexError("ScrolledList[%d] out of range." % k)

    def append(self, text):
        """Append a line to the listbox.
        """
        self.listbox.insert(Tk.END, text)

    def insert(self, linex, text):
        """Insert a line between two existing lines.
        """

        # -- 1 --
        if 0 <= linex < self.count():
            where = linex
        else:
            where = Tk.END

        # -- 2 --
        self.listbox.insert(where, text)

    def delete(self, linex):
        """Delete a line from the listbox.
        """
        if 0 <= linex < self.count():
            self.listbox.delete(linex)

    def clear(self):
        """Remove all lines.
        """
        self.listbox.delete(0, Tk.END)

    def curselection(self):
        """
        """
        return self.listbox.curselection()

    def bind(self, sequence=None, func=None, add=None):
        """
        """
        self.listbox.bind(sequence, func, add)


class atomTypeListController(object):
    """
    """

    def __init__(self):
        """
        """
        self.selectedAtoms = list()

    @property
    def atomTypeList(self):
        """
        """
        atomTypeList = OrderedDict()
        for atomType in sorted(set(atom.atoms for atom in self.selectedAtoms)):
            resi = [atom for atom in self.selectedAtoms if atom.atoms == atomType]
            atomTypeList[atomType] = resi
        return atomTypeList


class resiNumberListController(object):
    """
    """

    def __init__(self):
        """
        """
        self.atomsList = list()

    @property
    def resiNumberList(self):
        """
        """
        resiNumberList = OrderedDict()
        for segid in sorted(set(atom.segid for atom in self.atomsList)):
            for resi_number in sorted(set(atom[1] for atom in self.atomsList)):
                resi = [atom for atom in self.atomsList if atom.resi_number == resi_number and atom.segid == segid]
                resiNumberList["{}\ ({})".format(resi_number, segid)] = resi
        return resiNumberList


class NOEDataController(object):
    """
    """

    def __init__(self, dataSource, aManagerName, structure):
        """
        """
        self.dataSource = dataSource
        self.structure = structure
        self.name = aManagerName
        self.dataType = 'NOE'
        self.selectedAtoms = list()
        self.manager = dataSource.displayedConstraints.intersection(dataSource.ManagersList.get(aManagerName, "").constraintsManagerForDataType(self.dataType))

    def __len__(self):
        """
        """
        return len(self.manager)

    def getResiduesList(self):
        """
        """
        return (str(residue) for residue in sorted(int(number) for number in self.manager.residuesList))

    def setSelectedAtoms(self, aSelection):
        """
        """
        self.selectedAtoms = aSelection
        self.manager.setPartnerAtoms(aSelection)

    @property
    def displayedAtoms(self):
        """
        """
        return sorted(self.manager.atomsList)

    @property
    def partnerAtoms(self):
        """
        """
        if self.selectedAtoms:
            return sorted(set(atom for atom in self.manager.atomsList if self.manager.areAtomsPartner(atom) and atom not in self.selectedAtoms))
        else:
            return set()

    def constraintsForAtoms(self, atomsList):
        """
        """
        if len(atomsList) == 2:
            consManager = self.manager.constraintsManagerForAtoms([atomsList[0]]).intersection(self.manager.constraintsManagerForAtoms([atomsList[1]]))
            return consManager.constraints

    def constraintValueForAtoms(self, atomsList):
        """
        """
        return [(constraint.constraintValues, constraint.isSatisfied()) for constraint in self.constraintsForAtoms(atomsList)]

"""Main module declaring the module for pymol
contains interface for command line functions :
load CNS or DYANA distances constraints files
into molecular viewer, display them on the molecule
and show unSatisfied constraints according to a cutOff
with different color (White for not unSatisfied, blue for
lower limit violation, red for upper limit violation for NOEs)
"""
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



loadDefaults()

Core = NMRCore()

pyNMR = NMRApplication(Core, app="NoGUI")

def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=lambda s=self: NMRApplication(Core, app="GUI"))


PyNMRCLI = pyNMR.NMRCLI

def showNOE(structure='', managerName="", residuesList='all',
            dist_range='all', violationState='all',
            violCutoff=defaultForParameter("cutOff"),
            method=defaultForParameter('method'),
            radius=defaultForParameter("radius"),
            colors=defaultForParameter("colors"),
            rangeCutOff=defaultForParameter("rangeCutOff"),
            UnSatisfactionMarker=defaultForParameter("UnSatisfactionMarker"),
            SatisfactionMarker=defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.showNOE(structure, managerName, residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker)

def loadNOE(filename=""):
    """
    """
    PyNMRCLI.loadNOE(filename)

def showNOEDensity(structure='', managerName="", residuesList='all',
                   dist_range='all', violationState='all',
                   violCutoff=defaultForParameter("cutOff"),
                   rangeCutOff=defaultForParameter("rangeCutOff"),
                   method=defaultForParameter('method'),
                   colors=defaultForParameter("gradient")):
    """
    """
    PyNMRCLI.showNOEDensity(structure, managerName, residuesList,
                            dist_range, violationState, violCutoff, rangeCutOff,
                            method, colors)

def loadAndShow(filename, structure='', residuesList='all', dist_range='all',
                violationState='all',
                violCutoff=defaultForParameter("cutOff"),
                method=defaultForParameter('method'),
                rangeCutOff=defaultForParameter("rangeCutOff"),
                radius=defaultForParameter("radius"),
                colors=defaultForParameter("colors"),
                UnSatisfactionMarker=defaultForParameter("UnSatisfactionMarker"),
                SatisfactionMarker=defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.loadAndShow(filename, structure, residuesList, dist_range,
                         violationState, violCutoff, method, rangeCutOff,
                         radius, colors, UnSatisfactionMarker,
                         SatisfactionMarker)

def downloadNMR(pdbCode, url=defaultForParameter("urlPDB")):
    """
    """
    PyNMRCLI.downloadNMR(pdbCode, url)

def cleanScreen(filename):
    """
    """
    PyNMRCLI.cleanScreen(filename)


if __name__ == "__main__":
    MainWin = Tk.Tk()
    pyNMR.startGUI()
    MainWin.mainloop()

try:
    from pymol.cmd import extend
    extend("loadNOE", loadNOE)
    extend("showNOE", showNOE)
    extend("showNOEDensity", showNOEDensity)
    extend("loadAndShow", loadAndShow)
    extend("downloadNMR", downloadNMR)
    extend("cleanScreen", cleanScreen)

except ImportError:
    stderr.write("Demo mode.\n")
