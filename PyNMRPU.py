import pickle
from sys import stderr, stdout
import re
from math import sqrt
from os.path import basename
import urllib2
import shutil
import gzip
import os
import sys
import tempfile
import Tkinter as Tk
import ttk
import tkSimpleDialog
import tkFileDialog
import tkColorChooser
# from os import getcwd, chdir
from os.path import exists


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI", configFileName=""):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.StandardPrefDefaults = {
            "radius": 0.03, "cutOff": 0.3,
            "colors": {
                'Satisfied': [1, 1, 1, 1, 1, 1],
                'tooFar': [1, 0, 0, 1, 0, 0],
                'tooClose': [0, 0, 1, 0, 0, 1]
                },
            'gradient': "blue_white_red", "method": "sum6",
            'UnSatisfactionMarker': "_US_", 'SatisfactionMarker': '_S_',
            'rangeCutOff': 5,
            'urlPDB': "ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/"}
        self.gradientColorList = [
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
        if configFileName == "pymolNMR.cfg":
            configFile = open(configFileName, 'r')
            self.defaults = pickle.load(configFile)
            configFile.close()
            self.configFileName = configFileName
        else:
            self.defaults = self.StandardPrefDefaults
            self.configFileName = "pymolNMR.cfg"
        if app == "NoGUI":
            print "Starting PyNMR CLI ..."
        else:
            print "Starting PyNMR GUI ..."
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
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection['values'] = self.gradientColorList
        self.NMRInterface.preferencesPanel.densityPanel.gradient.set(self.defaults["gradient"])
        self.NMRInterface.preferencesPanel.sticksPanel.colors = self.defaults["colors"]
        self.NMRInterface.preferencesPanel.sticksPanel.UnSatisfactionMarker.set(self.defaults["UnSatisfactionMarker"])
        self.NMRInterface.preferencesPanel.sticksPanel.SatisfactionMarker.set(self.defaults["SatisfactionMarker"])
        self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
        self.NMRInterface.mainPanel.constraintPanel.violationsFrame.cutOff.set(self.defaults["cutOff"])
        self.NMRInterface.preferencesPanel.selectedMethod.set(self.defaults["method"])
        self.NMRInterface.preferencesPanel.rangeCutOff.set(self.defaults["rangeCutOff"])
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.comboPDB.values = self.getModelsNames()
        self.NMRInterface.preferencesPanel.configFileName = self.configFileName
        self.NMRInterface.preferencesPanel.url.set(self.defaults["urlPDB"])
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self
        self.NMRInterface.preferencesPanel.mainApp = self

    def getModelsNames(self):
        """
        """
        results = []
        objectsLists = get_names()
        for name in objectsLists:
            if name.find(self.defaults["UnSatisfactionMarker"]) >=0 or name.find(self.defaults["SatisfactionMarker"]) >= 0:
                pass
            else:
                results.append(name)
        return results


def IDConstraint(aConstraint, UnSatisfactionMarker, SatisfactionMarker):
    """Returns name of constraints :
    Name_(constraint number)_(structureName)_(violation_state)
    """
    if aConstraint.satisfaction != '':
        if aConstraint.satisfaction == 'unSatisfied':
            return aConstraint.id['name'] + str(aConstraint.id['number']) + UnSatisfactionMarker + aConstraint.structureName
        else:
            return aConstraint.id['name'] + str(aConstraint.id['number']) + SatisfactionMarker + aConstraint.structureName
    else:
        stderr.write("Can not give ID : Violation state not defined for constraint : " + aConstraint.structureName + "_" + aConstraint.id['name'] + str(aConstraint.id['number']) + "\n" + aConstraint.printCons() + "\n")



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
        self.inFileTab = []

        # Useful RegEx definitions
        self.ParReg = re.compile('[()]')  # used in cns constraints loading. Suppression of ()
        self.SParReg = re.compile(r"\(.*\)")  # used in cns constraint loading.
        self.RegResi = re.compile(r"RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#]*")  # match CNS Residue definition
        self.SharpReg = re.compile('[#]')  # used in cns constraints loading. Replace # by *
        self.AtTypeReg = re.compile('[CHON][A-Z]*')
        self.XEASYReg = re.compile(r'\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\w+\s+\d+')

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
        typeDefinition = ""
        fin = open(self.fileName, 'r')
        for txt in fin:
            self.fileText = self.fileText + txt
            txt = txt.lstrip()
            if txt.find('!') < 0:
                self.inFileTab.append(txt.upper().rstrip())
                if typeDefinition == "":
                    if txt.upper().find("ASSI") > -1:
                        typeDefinition = 'CNS'
                    elif self.XEASYReg.search(txt):
                        typeDefinition = 'CYANA'
            else:
                stderr.write(txt + " skipped. Commented out.\n")
        fin.close()
        return typeDefinition

    def synthesizeCNSFile(self):
        """
        """
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
        aManager.format = "CNS"
        for aConstLine in self.validCNSConstraints:  # itemizing constraints
            # avoid empty lines
            if re.search(r'\d', aConstLine):
                parsingResult = self.parseCNSConstraint(aConstLine)
                if parsingResult is not None:
                    if len(parsingResult) == 3:  # 2 residues + distances (matches also H-Bonds)
                        aConstraint = NOE()
                    else:
                        # No other constraint type supported ... for now !
                        break
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
                             'name': self.AtTypeReg.match(
                                self.convertTypeDyana(cons_tab[2])).group()},
                            {'resid': int(cons_tab[3]),
                             'name': self.AtTypeReg.match(
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
                        stderr.write("Unknown error while loading constraint "
                                     + ":\n" + aConstLine + "\n")
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
        except:
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


class ConstraintSetManager(object):
    """Class to manage a set of constraints
    """
    def __init__(self, managerName):
        self.constraints = []
        self.residuesList = []
        self.structure = ''
        self.name = managerName
        self.format = ""
        self.fileText = ""

    def __str__(self):
        return self.name + " contains " + str(len(self.constraints)) + " constraints.\n"

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    # Constraints management methods

    def setPDB(self, structure):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.structure = structure
        if len(self.constraints):
            for constraint in self.constraints:
                constraint.structureName = self.structure

    def associateToPDB(self):
        """Invokes associatePDBAtoms function on all constraints
        """
        result = 0
        if self.structure != '':
            if len(self.constraints):
                for constraint in self.constraints:
                    constraint.associatePDBAtoms(self.structure)
                    result = 1
        return result

    def removeAllConstraints(self):
        """Empties an array of constraints
        """
        while len(self.constraints) > 0:
            for constraint in self.constraints:
                self.constraints.remove(constraint)

    def addConstraint(self, aConstraint):
        """Add a constraint to the constraint list of the manager and
        update the list of residues
        """
        self.constraints.append(aConstraint)
        aConstraint.setName(self.name)
        for resiNumber in aConstraint.getResisNumber():
            if resiNumber not in self.residuesList:
                self.residuesList.append(resiNumber)

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) <= len(self.constraints):
            del self.constraints[int(aConstraintNumber)]

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
        involvedResidueslist = []
        numberOfDrawnConstraints = 0
        for aConstraint in selectedConstraints:
            if not aConstraint.resis[0]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[0]['number'])
            if not aConstraint.resis[1]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[1]['number'])
            if aConstraint.satisfaction == 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction == 'Satisfied':
                color = colors['Satisfied']
            drawConstraint(aConstraint.points, color, radius,
                           IDConstraint(aConstraint, self.UnSatisfactionMarker,
                                        self.SatisfactionMarker))
            numberOfDrawnConstraints = numberOfDrawnConstraints + 1
        return {'Residueslist': involvedResidueslist,
                'DrawnConstraints': numberOfDrawnConstraints}

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
        """
        constraintList = {}
        constraintsUsed = 0
        for aConstraint in selectedConstraints:
            if not aConstraint.resis[0]['number'] in constraintList.keys():
                constraintList[aConstraint.resis[0]['number']] = 10
            else:
                constraintList[aConstraint.resis[0]['number']] = constraintList[aConstraint.resis[0]['number']] + 10
            if not aConstraint.resis[1]['number'] in constraintList.keys():
                constraintList[aConstraint.resis[1]['number']] = 10
            else:
                constraintList[aConstraint.resis[1]['number']] = constraintList[aConstraint.resis[1]['number']] + 10
            constraintsUsed = constraintsUsed + 1
        return constraintList

    def paD(self, selectedConstraints, structure, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        zeroBFactors(structure)
        if len(densityList) > 0:
            for residu in densityList.keys():
                setBfactor(structure + " & i. " + residu, densityList[residu])
        paintDensity(color_gradient, structure)
        return densityList


class ConstraintFilter(object):
    """

    """

    def __init__(self, structure, residuesList, dist_range, violationState,
                 violCutoff, method, RangeCutOff):
        """Defines parameters for filtering the constraints
        """
        self.parameters = {}
        self.parameters['residuesList'] = residuesList
        self.parameters['range'] = dist_range
        self.parameters['violationState'] = violationState
        self.parameters['cutOff'] = violCutoff
        self.parameters['structure'] = structure
        self.parameters['method'] = method
        self.parameters['rangeCutOff'] = RangeCutOff

    def filter(self, aConstraint):
        """Filter the constraints to be drawn (there should be a better
        way to implement it)
        """
        if aConstraint.getRange(self.parameters['rangeCutOff']) in self.parameters['range']:
            inList = 0
            for aNumber in aConstraint.getResisNumber():
                if aNumber in self.parameters['residuesList']:
                    inList = 1
                    break
            if inList:
                aConstraint.structureName = self.parameters['structure']
                if aConstraint.isValid():
                    if aConstraint.setDistance(self.parameters['method']):
                        aConstraint.setViolationState(self.parameters['cutOff'])
                        if aConstraint.isSatifsied() in self.parameters['violationState']:
                            return 1
                        else:
                            return 0
                    else:
                        stderr.write("Distance issue with constraint :\n"
                                     + aConstraint.definition + "\n")
                        return 0
                else:
                    stderr.write("Selection issue with constraint :\n"
                                 + aConstraint.definition + "\n")
                    return 0
            else:
                return 0
        else:
            return 0

    def filterConstraints(self, constraintList):
        """
        """
        selectedConstraint = []
        for aConstraint in constraintList:
            if self.filter(aConstraint):
                selectedConstraint.append(aConstraint)
        return selectedConstraint

def centerOfMass(selection):
    """ Author: Andreas Henschel 2006
    assumes equal weights
    """
    model = get_model(selection)
    if len(model.atom) > 0:
        x, y, z = 0, 0, 0
        for AtomA in model.atom:
            x += AtomA.coord[0]
            y += AtomA.coord[1]
            z += AtomA.coord[2]
        return (x/len(model.atom), y/len(model.atom), z/len(model.atom))
    else:
        stderr.write("selection is empty :"+ str(selection)+"\n")
        return 0, 0, 0

def calcDistance(selection_init, selection_final, method):
    """
    Choose which method to calculate distances
    """
    if method == 'ave6':
        return averageDistance_6(selection_init, selection_final)
    elif method == 'sum6':
        return sumDistance_6(selection_init, selection_final)
    else:
        stderr.write("This method of calculation is not defined : "
                     + str(method) + "\n")

def averageDistance_6(selection_init, selection_final):
    """
    Calculate distance according to :
    ((sum of all distances^-6)/number of distances)^-1/6
    """
    model_init = get_model(selection_init)
    model_final = get_model(selection_final)
    if len(model_init.atom) > 0 and len(model_final.atom) > 0:
        distance_list = []
        for AtomA in model_init.atom:
            for AtomB in model_final.atom:
                distance_list.append(sqrt(pow((AtomA.coord[0] - AtomB.coord[0]), 2)
                                          + pow((AtomA.coord[1] - AtomB.coord[1]), 2)
                                          + pow((AtomA.coord[2] - AtomB.coord[2]), 2))
                                    )
        sum6 = 0
        for distance in distance_list:
            try:
                sum6 = sum6 + pow(distance, -6)
            except:
                stderr.write("Problem with selection : "+ selection_init + " " +
                             selection_final + "\n" + "distance is : "
                             + str(distance)+" A")
        return pow(sum6/len(distance_list), -1./6)
    else:
        stderr.write("selection is empty : " + selection_init + " "
                     + selection_final + "\n")
        return 0.0

def sumDistance_6(selection_init, selection_final):
    """
    Calculate distance according to : (sum of all distances^-6)^-1/6
    """
    model_init = get_model(selection_init)
    model_final = get_model(selection_final)

    if len(model_init.atom) > 0 and len(model_final.atom) > 0:
        distance_list = []
        for AtomA in model_init.atom:
            for AtomB in model_final.atom:
                distance_list.append(sqrt(pow((AtomA.coord[0] - AtomB.coord[0]), 2)
                                          +pow((AtomA.coord[1] - AtomB.coord[1]), 2)
                                          +pow((AtomA.coord[2] - AtomB.coord[2]), 2))
                                    )
        sum6 = 0
        for distance in distance_list:
            try:
                sum6 = sum6 + pow(distance, -6)
            except:
                stderr.write("Problem with selection : "+ selection_init + " "
                             + selection_final + "\n" + "distance is : "
                             + str(distance) + " A")
        result = pow(sum6, -1./6)
        return result

    else:
        stderr.write("selection is empty : " + selection_init + " "
                     + selection_final + "\n")
        return 0.0

try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def select(selectionName, selection):
        if selectionName == "":
            return PymolCmd.select(selection)
        else:
            return PymolCmd.select(selectionName, selection)

    def get_model(model):
        return PymolCmd.get_model(model)

    def alterBFactors(structure,bFactor):
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

    def createSelection(Items):
        selection = ""
        if len(Items) > 2:
            selection = Items.pop(0) + " &"
            for residue in Items:
                selection = selection + " resi " + residue + " +"
        return selection.rstrip("+")

    def get_names():
        return PymolCmd.get_names()

except ImportError:
    def select(selectionName, selection):
        return []

    def get_model(model):
        return []

    def alterBFactors(structure,bFactor):
        pass

    def spectrum(color_gradient, structure):
        pass

    def drawConstraint(points, color, aRadius, ID):
        pass

    def zoom(selection):
        pass

    def delete(selectionName):
        pass

    def createSelection(Items):
        if len(Items) > 2:
            selection = Items.pop(0) + " &"
            for residue in Items:
                selection = selection + " resi " + residue + " +"
        return selection.rstrip("+")

    def get_names():
        return []

def zeroBFactors(structure):
    alterBFactors(structure, 0)

def setBfactor(selection, bFactor):
    alterBFactors(selection, bFactor)

def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)

"""load CNS or DYANA distances constraints files
into molecular viewer, display them on the molecule
and show unSatisfied constraints according to a cutOff
with different color (White for not unSatisfied, blue for
lower limit violation, red for upper limit violation for NOEs)
"""



class NMRCore(object):
    """Low Level Interface Class
    for loading and displaying constraints
    """
    def __init__(self):
        self.ManagersList = {}
        self.filter = ""
        self.displayedConstraints = []

    def loadNOE(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = basename(filename)
        loader = ConstraintLoader(filename, managerName)
        self.ManagersList[managerName] = loader.loadConstraintsFromFile()

    def showSticks(self, managerName, structure, colors, radius, UnSatisfactionMarker, SatisfactionMarker):
        """
        """
        self.ManagersList[managerName].setPDB(structure)
        drawer = ConstraintDrawer(UnSatisfactionMarker, SatisfactionMarker)
        selectedConstraints = []
        if len(self.ManagersList[managerName]):
            if self.ManagersList[managerName].associateToPDB():
                filteredConstraints = self.filter.filterConstraints(
                    self.ManagersList[managerName].constraints)
                selectedConstraints = []
                for constraint in filteredConstraints:
                    if constraint not in self.displayedConstraints:
                        selectedConstraints.append(constraint)
                self.displayedConstraints = self.displayedConstraints + selectedConstraints
                results = drawer.drC(selectedConstraints, radius, colors)
                numberOfConstraints = results['DrawnConstraints']
                selection = createSelection([self.ManagersList[managerName].structure] + results['Residueslist'])
                select('involRes', selection)
                zoom(selection)

        else:
            stderr.write("No constraints to draw ! You might want to load a few of them first ...\n")
        return {"numberOfConstraints": numberOfConstraints,
                "numberOfResidues": len(results['Residueslist'])}

    def showNOEDensity(self, managerName, structure, gradient):
        """Seeks for constraints that fit criteria, increases a counter for
        each residue which has a matching constraint. That simulates a density
        which is then paint on the model according to a color gradient
        """
        self.ManagersList[managerName].setPDB(structure)
        theFilter = self.filter
        drawer = ConstraintDrawer()
        if len(self.ManagersList[managerName]):
            if self.ManagersList[managerName].associateToPDB():
                selectedConstraints = theFilter.filterConstraints(
                    self.ManagersList[managerName].constraints)
                self.displayedConstraints = self.displayedConstraints + selectedConstraints
                densityList = drawer.paD(selectedConstraints,
                                         self.ManagersList[managerName].structure,
                                         gradient)
                zoomSelection = self.ManagersList[managerName].structure + " &"
                if len(densityList):
                    zoomSelection = createSelection([self.ManagersList[managerName].structure] + densityList.keys())
                zoom(zoomSelection)
                select('involRes', zoomSelection)
        return {"numberOfConstraints": len(selectedConstraints),
                "numberOfResidues": len(densityList)}

    def commandsInterpretation(self, structure, managerName, residuesList, dist_range,
                               violationState, violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if residuesList == 'all':
            resList = self.ManagersList[managerName].residuesList
        else:
            resList = []
            for resi_range in residuesList.split("+"):
                aRange = resi_range.split("-")
                if len(aRange) == 2:
                    for residueNumber in range(int(aRange[0]), int(aRange[1]) + 1):
                        resList = resList + [str(residueNumber)]
                elif len(aRange) == 1:
                    resList = resList + [str(aRange[0])]
                else:
                    stderr.write("Residues set definition error : " +
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
        self.filter = ConstraintFilter(structure, resList, dist_range,
                                       violationState, violCutoff,
                                       method, rangeCutOff)

    def cleanScreen(self, managerName):
        """
        """
        self.displayedConstraints = []
        delete(managerName + "*")

    def saveConstraintsFile(self, aManagerName, fileName):
        """
        """
        fout = open(fileName, 'w')
        fout.write(self.ManagersList[aManagerName].fileText)
        fout.close()

    def downloadFromPDB(self, pdbCode, url):
        """
        """
        fileName = pdbCode.lower()+".mr"
        zippedFileName = fileName+".gz"
        try:
            workdir = os.getcwd()
            tempDownloadDir = tempfile.mkdtemp()
            os.chdir(tempDownloadDir)
            restraintFileRequest = urllib2.urlopen(urllib2.Request(url+zippedFileName))
            with open(zippedFileName, 'wb') as f:
                shutil.copyfileobj(restraintFileRequest, f)
            restraintFileRequest.close()
            zippedFile = gzip.open(zippedFileName, 'rb')
            decodedFile = zippedFile.read()
            restraintFile = open(fileName, 'w')
            restraintFile.write(decodedFile)
            zippedFile.close()
            os.remove(zippedFileName)
            restraintFile.close()
            self.loadNOE(fileName)
            os.remove(fileName)
            os.chdir(workdir)
            os.removedirs(tempDownloadDir)
        except:
            sys.stderr.write("Can not download " +
                             pdbCode + " NMR Restraints file from PDB.\n")

lastDigit = re.compile(r'\d(\b|\Z)')  # look for last digit of atom type (used in AtomSet)


class AtomSet(object):
    """Base Class contains residu number
        and the atom type of the atom
    """

    def __init__(self, structureName, resi_number, resi_type):
        """Initialisation sets the residu number
            and the atom type
        """
        self.structure = structureName
        self.number = resi_number
        self.atType = resi_type

    def __str__(self):
        return self.getID()

    def __eq__(self, otherAtomSet):
        return isinstance(otherAtomSet, self.__class__) and (self.__dict__ == otherAtomSet.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def getID(self):
        """return ID of the atom for selection
            by Pymol functions. Form : structure & i. Number & n. atomType
            should be more independent from pymol, maybe should not be here at all ...
        """
        selection = self.structure + " & i. " + str(self.number) + " & n. " + str(self.atType)
        if not select("", selection):  # often due to different format (e.g. : HB2 -> 2HB)
            if self.atType == 'HN':
                self.atType = 'H'
            elif self.atType == 'H':
                self.atType = 'HN'
            elif lastDigit.search(self.atType):
                digit = lastDigit.search(self.atType).group()[0]
                self.atType = digit + lastDigit.sub('', self.atType)  # put final digit at the beginning
            self.atType = '*' + self.atType
            selection = self.structure + " & i. " + str(self.number) + " & n. " + str(self.atType)
            if not select("", selection):
                selection = "noID"
        return selection


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



class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        """
        """
        super(NOE, self).__init__()
        self.points = {}
        self.numberOfAtomsSets = 2
        self.type = "NOE"

    def setViolationState(self, cutOff):
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

    def getRange(self, RangeCutOff):
        """Return the range name, according to the usual NMR specification
        range depends on the number of residus between the atomsets
        """
        if not int(self.resis[0]['number']) - int(self.resis[1]['number']):
            return 'intra'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) == 1:
            return 'sequential'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) > 1 and abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) <= RangeCutOff:
            return 'medium'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) > RangeCutOff:
            return 'long'
        else:
            stderr.write('How come ?\n')

    def setDistance(self, method):
        """Set actual distance of the constraint in the current structure file
        """
        self.points[0] = centerOfMass(self.atoms[0].getID())
        self.points[1] = centerOfMass(self.atoms[1].getID())
        self.constraintValues['actual'] = calcDistance(self.atoms[0].getID(), self.atoms[1].getID(), method)
        if self.constraintValues['actual'] <= 0:
            return 0
        else:
            return 1

    def getResisNumber(self):
        """Utility method
        """
        return [self.resis[0]['number'], self.resis[1]['number']]


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
        self.aboutFrame.grid(row=0, column=0)
        ttk.Label(self.aboutFrame, justify=Tk.CENTER, text=u"This Pymol plugin has been written \nbecause I " +
                  "thought it would be useful to check \nmy NOEs during my postdocship. I hope it'll" +
                  " \nhelp you as well. Feel free to send \nany comments to : github.com/oserve/PyNMR\n" +
                  "This plugin is free and may be copied as \nlong as you respect the copyright.").grid(row=0, column=0)
        self.helpFrame = ttk.LabelFrame(self, text=u'Help')
        self.helpFrame.grid(row=1, column=0)
        ttk.Label(self.helpFrame, text=u'Some useful hints').grid(row=0, column=0)



class ConstraintSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text=u"Constraints Selection")
        self.consRangeFrame = RangeSelectionPanel(self)
        self.violationsFrame = ViolationSelectionPanel(self)
        self.structureManagement = StructureSelectionPanel(self)
        self.panelsList = [self.consRangeFrame, self.violationsFrame, self.structureManagement]
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
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        rowPosition = 0
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            self.RangesVars[consRange] = Tk.IntVar(self)
            self.RangesCB[consRange] = ttk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
            rowPosition = rowPosition + 1
        self.RangesVars["all"] = Tk.IntVar(self)
        self.RangesCB["all"] = ttk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        """
        """
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            self.RangesVars[consRange].set(self.RangesVars["all"].get())

    def tick(self):
        """
        """
        self.RangesVars["all"].set(1)
        for aRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[aRange].get() == 0:
                self.RangesVars["all"].set(0)
                break

    def getInfo(self):
        """
        """
        ranges = []
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[consRange].get() == 1:
                ranges.append(consRange)
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
        rowPosition = 0
        for violationType in ['unSatisfied', 'Satisfied']:
            self.ViolationsVars[violationType] = Tk.IntVar(self)
            self.UnSatisfiedCB[violationType] = ttk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatisfiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W, columnspan=2)
            self.ViolationsVars[violationType].set(1)
            rowPosition = rowPosition + 1

        ttk.Label(self, text=u'Distance CutOff :').grid(row=rowPosition + 1,
                                                        column=0, columnspan=2)

        self.spinBox_cutOff = Tk.Spinbox(self, textvariable=self.cutOff,
                                         from_=0.0, to=10.0, increment=0.1,
                                         format='%2.1f', width=6)
        self.spinBox_cutOff.grid(row=rowPosition + 2, column=0)
        ttk.Label(self, text=u'\u212b').grid(row=rowPosition + 2, column=1)

    def getInfo(self):
        """
        """
        violationState = []
        for violationType in ['unSatisfied', 'Satisfied']:
            if self.ViolationsVars[violationType].get() == 1:
                violationState.append(violationType)
        return {"cutOff": self.cutOff.get(), "violationState": violationState}


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
        self.comboPDB['values'] = self.mainApp.getModelsNames()



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
        self.saveButton = ttk.Button(self, text=u'Save File', command=self.saveFile)
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
        self.constraintsList.listbox.bind('<<ListboxSelect>>', self.onStructureSelect)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint file")
        if filename is not None:
            self.NMRCommands.loadNOE(filename)
            self.updateFilelist()

    def updateFilelist(self):
        """
        """
        managerList = ""
        for item in self.NMRCommands.ManagersList.keys():
            managerList = managerList + " " + item
        self.constraintsFileList.set(managerList)

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
            waitWindow = ttk.Progressbar(self, mode='indeterminate')
            waitWindow.start()
            self.NMRCommands.downloadFromPDB(pdbCode, infos["urlPDB"])
            waitWindow.stop()
            self.updateFilelist()

    def onStructureSelect(self, evt):
        """
        """
        # Note here that Tkinter passes an event object
        w = evt.widget
        index = int(w.curselection()[0])
        self.selectedFile = w.get(index)
        self.infoLabelString.set("Contains " +
                                 str(len(self.NMRCommands.ManagersList[self.selectedFile])) +
                                 " Constraints (" + self.NMRCommands.ManagersList[self.selectedFile].format + ")")

    def getInfo(self):
        """
        """
        if len(self.selectedFile):
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
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self, textvariable=self.constraintSelectionText)
        self.mainGUI = ""  # Must be set at run time
        self.NMRCommands = ""  # Must be set by application at run time
        self.widgetCreation()


    def widgetCreation(self):
        """
        """
        self.sticksButton.grid(row=0, column=0)
        self.densityButton.grid(row=0, column=1)
        self.cleanButton.grid(row=0, column=2)
        self.labelConstraints.grid(row=1, column=0, columnspan=3)
        self.constraintSelectionText.set('')

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
            results = self.NMRCommands.showSticks(
                                        infos["constraintFile"],
                                        infos["structure"], infos["colors"],
                                        infos["radius"],
                                        infos["UnSatisfactionMarker"],
                                        infos["SatisfactionMarker"])

            self.constraintSelectionText.set(str(results['numberOfConstraints']) +
                                             " constraints used, involving " +
                                             str(results["numberOfResidues"]) +
                                             " residues")

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
            results = self.NMRCommands.showNOEDensity(
                                            infos["constraintFile"],
                                            infos["structure"],
                                            infos["gradient"])

            self.constraintSelectionText.set(str(results['numberOfConstraints']) +
                                             " constraints used, involving " +
                                             str(results["numberOfResidues"]) +
                                             " residues")

    def cleanAll(self):
        """Remove all displayed sticks
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen(infos["constraintFile"])
        self.constraintSelectionText.set("0 constraints used.")

    def infoCheck(self, infos):
        """
        """
        check = 1
        for item in infos:
            if infos[item] == "":
                check = 0
                break
        return check



class SticksPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius,
                                         from_=0.00, to=0.5, increment=0.01,
                                         format='%1.2f', width=4)
        self.satisfiedColorButton = ttk.Button(self, text=u"Choose color",
                                               command=self.setSatisfiedColor)
        self.tooFarButton = ttk.Button(self, text=u"Choose color",
                                       command=self.setTooFarColor)
        self.tooCloseButton = ttk.Button(self, text=u"Choose color",
                                         command=self.setTooCloseColor)
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
        self.satisfiedColorButton.grid(row=1, column=1)
        ttk.Label(self, text=u"Atoms too far").grid(row=2, column=0)
        self.tooFarButton.grid(row=2, column=1)
        ttk.Label(self, text=u"Atoms too close").grid(row=3, column=0)
        self.tooCloseButton.grid(row=3, column=1)
        ttk.Label(self, text=u'Unsatisfied Marker :').grid(row=4, column=0)
        self.UnSatisfactionMarkerEntry.grid(row=4, column=1)
        ttk.Label(self, text=u'Satisfied Marker :').grid(row=5, column=0)
        self.SatisfactionMarkerEntry.grid(row=5, column=1)

    def getInfo(self):
        """
        """
        return {"radius": self.radius.get(),
                "colors": self.colors,
                "UnSatisfactionMarker": self.UnSatisfactionMarker.get(),
                "SatisfactionMarker": self.SatisfactionMarker.get()}

    def setSatisfiedColor(self):
        """
        """
        currentColor = float2intColor(self.colors["Satisfied"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["Satisfied"] = int2floatColor(result[0])

    def setTooFarColor(self):
        """
        """
        currentColor = float2intColor(self.colors["tooFar"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooFar"] = int2floatColor(result[0])

    def setTooCloseColor(self):
        """
        """
        currentColor = float2intColor(self.colors["tooClose"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooClose"] = int2floatColor(result[0])


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
        self.configFileName = ""
        self.rangeCutOff = Tk.IntVar(self)
        self.rangeCutOffEntry = ttk.Entry(self, textvariable=self.rangeCutOff, width=2)
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
            position = position + 1

        ttk.Label(self, text=u'Residue range cut-off :').grid(row=position, column=0)

        self.rangeCutOffEntry.grid(row=position, column=1)
        position = position + 1
        self.sticksPanel.grid(row=position, column=0, columnspan=2)
        position = position + 1
        self.densityPanel.grid(row=position, column=0, columnspan=2)
        position = position + 1
        ttk.Label(self, text=u'PDB.org URL for download').grid(row=position, column=0, columnspan=2)
        position = position + 1
        self.urlTextField.grid(row=position, column=0, columnspan=2)
        position = position + 1
        self.savePrefButton.grid(row=position, column=0)
        self.resetButton.grid(row=position, column=1)

    def savePrefs(self):
        configFile = open(self.configFileName, 'w')
        pickle.dump(self.mainGUI.getInfo(), configFile)
        configFile.close()

    def resetPrefs(self):
        defaults = self.mainApp.StandardPrefDefaults
        self.densityPanel.gradient.set(defaults["gradient"])
        self.sticksPanel.colors = defaults["colors"]
        self.sticksPanel.UnSatisfactionMarker.set(defaults["UnSatisfactionMarker"])
        self.sticksPanel.SatisfactionMarker.set(defaults["SatisfactionMarker"])
        self.sticksPanel.radius.set(defaults["radius"])
        self.selectedMethod.set(defaults["method"])
        self.url.set(defaults["urlPDB"])

    def getInfo(self):
        """
        """
        infos = {"method": self.selectedMethod.get(),
                 "rangeCutOff": self.rangeCutOff.get(),
                 "urlPDB": self.url.get()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


def float2intColor(color):
    """
    """
    return (int(color[0]*255), int(color[1]*255), int(color[2]*255))


def int2floatColor(color):
    """
    """
    return [color[0]/255.0, color[1]/255.0, color[2]/255.0,
            color[0]/255.0, color[1]/255.0, color[2]/255.0]
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
        height=DEFAULT_HEIGHT, vscroll=1, hscroll=0, callback=None, listvariable=None):
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
        self.__createWidgets(listvariable)

    def __createWidgets(self, alistvariable):
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
            borderwidth=2, listvariable=alistvariable)
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
"""Main module declaring the module for pymol
contains interface for command line functions
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



configFileName = "pymolNMR.cfg"

if not exists(configFileName):
    configFileName = ""

Core = NMRCore()

pyNMR = NMRApplication(Core, app="NoGUI", configFileName=configFileName)


def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=lambda s=self: NMRApplication(Core, app="GUI", configFileName=configFileName))


def showNOE(structure='', managerName="", residuesList='all', dist_range='all',
            violationState='all', violCutoff=pyNMR.defaults["cutOff"],
            method="sum6", radius=pyNMR.defaults["radius"],
            colors=pyNMR.defaults["colors"], rangeCutOff=pyNMR.defaults["rangeCutOff"],
            UnSatisfactionMarker=pyNMR.defaults["UnSatisfactionMarker"],
            SatisfactionMarker=pyNMR.defaults["SatisfactionMarker"]):
    """Command to display NMR restraints as sticks on protein structure with
    different parameters : filtering according to distance, restraints display
    options
    """
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(structure, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method, rangeCutOff)
            results = Core.showSticks(managerName, structure, colors, radius,
                            UnSatisfactionMarker, SatisfactionMarker)
            stdout.write(str(results['numberOfConstraints']) +
                             " constraints drawn on a total of " +
                             str(len(Core.ManagersList[managerName])) + "\n")

        else:
            stderr.write("Please check constraints filename.\n")


def loadNOE(filename=""):
    """load NMR distance constraints, call for the correct file format
    (CNS/CYANA),
    """
    if exists(filename):
        Core.loadNOE(filename)
    else:
        stderr.write("File : " + filename + " has not been found.\n")


def showNOEDensity(structure='', managerName="", residuesList='all', dist_range='all',
                   violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                   rangeCutOff=pyNMR.defaults["rangeCutOff"],
                   method='sum6', colors=pyNMR.defaults["gradient"]):
    """Command to display NMR restraints as color map on protein structure with
    different parameters : filtering according to distance, restraints display
    options
    """
    if managerName == '' and len(Core.ManagersList) == 0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName == '':
            managerName = Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(structure, managerName, residuesList,
                                        dist_range, violationState, violCutoff,
                                        method, rangeCutOff)
            results = Core.showNOEDensity(managerName, structure, colors)
            stdout.write(str(results["numberOfConstraints"]) +
                         " constraints used.\n")
            stdout.write(str(results["numberOfResidues"]) +
                         " residues involved.\n")
        else:
            stderr.write("Please check constraints filename.\n")


def loadAndShow(filename, consDef, structure='', residuesList='all', dist_range='all',
                violationState='all', violCutoff=pyNMR.defaults["cutOff"],
                method="sum6", rangeCutOff=pyNMR.defaults["rangeCutOff"],
                radius=pyNMR.defaults["radius"],
                colors=pyNMR.defaults["colors"]):
    """Combine two previous defined functions : load and display"""
    loadNOE(filename)
    showNOE(structure, filename, residuesList, dist_range, violationState,
            violCutoff, method, radius, colors, rangeCutOff)


def downloadNMR(pdbCode, url=pyNMR.defaults["urlPDB"]):
    """
    """
    Core.downloadFromPDB(pdbCode, url)


def cleanScreen(filename):
    """Call the command to clear the screen from all NMR
    restraints
    """
    if filename in Core.ManagersList:
        Core.cleanScreen(filename)

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

except ImportError:
    stderr.write("Demo mode.\n")
