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
from sys import stderr, stdout
from math import sqrt, pow
from os.path import basename, exists
from os import getcwd, chdir, path
import Tkinter as Tk
import Pmw
import tkFileDialog
import tkColorChooser
from pymol import cmd
from pymol.cmd import get_names, get_model, zoom, spectrum, extend, delete, load_cgo, alter
from pymol.cgo import CYLINDER

def drawConstraint(points, color, aRadius, ID):
    cons =[CYLINDER]+list(points[0])+list(points[1])+[aRadius]+color
    load_cgo(cons, ID)

def alterBFactors(pdb, bFactor):
    alter(pdb,"b="+ str(bFactor))

def select(selectionName, selection):
    if selectionName == "":
        return cmd.select(selection)
    else:
        return cmd.select(selectionName, selection)

def zeroBFactors(pdb):
    alterBFactors(pdb, 0)

def setBfactor(selection, bFactor):
    alterBFactors(selection, bFactor)

def paintDensity(color_gradient, pdb):
    spectrum("b", color_gradient, pdb )

lastDigit=re.compile('\d(\b|\Z)')#look for last digit of atom type (used in MyAtom)

class AtomSet(object):
    """Base Class contains residu number
        and the atom type of the atom
    """
    
    def __init__(self, pdbName,resi_number, resi_type):
        """Initialisation sets the residu number
            and the atom type
        """
        self.pdb=pdbName
        self.number=resi_number
        self.atType=resi_type
    
    def getID(self):
        """return ID of the atom for selection
            by Pymol functions. Form : pdb & i. Number & n. atomType
            should be more independent from pymol, maybe should not be here at all ...
        """            
        selection=self.pdb+" & i. "+str(self.number)+" & n. "+str(self.atType)
        if not select("",selection):# often due to different format (e.g. : HB2 -> 2HB)
            if self.atType=='HN':
                self.atType='H'
            elif self.atType=='H':
                self.atType='HN'
            elif lastDigit.search(self.atType):
                digit=lastDigit.search(self.atType).group()[0]
                self.atType=digit+lastDigit.sub('',self.atType)# put final digit at the beginning)
            self.atType='*'+self.atType
            selection=self.pdb+" & i. "+str(self.number)+" & n. "+str(self.atType)
            if not select("",selection):
                selection="noID"
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
        self.id = {}
        self.resis = []
        self.satisfaction = ''
        self.definition = ''
        self.atoms = []
        self.constraintValues = {}
        self.numberOfAtomsSets = 0

    def setName(self,aName):
        self.id['name'] = aName

    def setConstraintValues(self, constraintValue, Vmin, Vplus):
        """
        Set constraints values for violations
            determination
        """
        self.constraintValues['constraint'] = float(constraintValue)
        self.constraintValues['min'] = float(Vmin)
        self.constraintValues['plus'] = float(Vplus)

    def isUnSatifsied(self):
        """returns yes or no according to the violation state
        """
        return self.satisfaction

    def associatePDBAtoms(self):
        """
        Sets atoms sets, checks for inconsistency with pdb file
        """
        for atomsSetNumber in range(self.numberOfAtomsSets):
            self.atoms.append( AtomSet(self.pdbName, self.resis[atomsSetNumber]['number'], self.resis[atomsSetNumber]['atoms'] + self.resis[atomsSetNumber]['atoms_number']))

        return self.isValid()
    
    def isValid(self):
        """
        """
        validity=1
        for atomsSetNumber in range(self.numberOfAtomsSets):
            if "noID" in self.atoms[atomsSetNumber].getID():
                validity=0
                break
        return validity

class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        super(NOE, self).__init__()
        self.points = {}
        self.numberOfAtomsSets = 2        

    def setViolationState(self, cutOff):
        """Set violation state, with optional additional cutoff
        """
        if (self.constraintValues['actual'] <= (self.constraintValues['constraint']-self.constraintValues['min']-cutOff)):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooClose'
        elif (self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + cutOff)):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooFar'
        else:
            self.satisfaction = 'not unSatisfied'

    def getRange(self):
        if not (int(self.resis[0]['number'])-int(self.resis[1]['number'])):
            return 'intra'
        elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) == 1:
            return 'sequential'
        elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) > 1 and abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) <= 5:
            return 'medium'
        elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) > 5:
            return 'long'
        else:
            stderr.write('How come ?\n')

    def getID(self):
        """Returns name of constraints : Name_(constraint number)_(pdbName)_(violation_state)
        """
        if self.satisfaction != '':
            if self.satisfaction == 'unSatisfied':
                return self.id['name'] + str(self.id['number']) + "_V" + "_" + self.pdbName
            else:
                return self.id['name'] + str(self.id['number']) + "_NV" + "_" + self.pdbName
        else:
            stderr.write("Can not give ID : Violation state not defined for constraint : " + self.pdbName + "_" + self.id['name'] + str(self.id['number']) + "\n" + self.printCons() + "\n")

    def setDistance(self, method):
        """Set actual distance of the constraint in the current pdb file
        """
        self.points[0] = centerOfMass(self.atoms[0].getID())
        self.points[1] = centerOfMass(self.atoms[1].getID())
        self.constraintValues['actual'] = calcDistance(self.atoms[0].getID(), self.atoms[1].getID(), method)
        if self.constraintValues['actual'] <= 0:
            return 0
        else:
            return 1

    def getResisNumber(self):
        """
        """
        return [self.resis[0]['number'],self.resis[1]['number']]


class ConstraintSetManager(object):
    """Class to manage a set of constraints
    """
    def __init__(self, managerName):
        self.constraints = []
        self.residuesList = []
        self.pdb = ''
        self.name=managerName

    #Constraints management methods

    def setPDB(self, pdb):
        """Sets the name of the structure (usually a PDB File) on which the distance should be calculated
        """
        self.pdb = pdb
        if len(self.constraints):
            for constraint in self.constraints:
                constraint.pdbName = self.pdb

    def associateToPDB(self):
        """Invokes associatePDBAtoms function on all constraints
        """
        result=0
        if self.pdb != '':
            if len(self.constraints):
                for constraint in self.constraints:
                    constraint.associatePDBAtoms()
                    result=1
        return result

    def removeAllConstraints(self):
        """Empties an array of constraints
        """
        while len(self.constraints) > 0:
            for constraint in self.constraints:
                constraintsSet.remove(constraint)

    def addConstraint(self, aConstraint):
        """Add a constraint to the constraint list of the manager and update the list of residues
        """
        self.constraints.append(aConstraint)
        aConstraint.setName(self.name)
        for resiNumber in aConstraint.getResisNumber():
            if resiNumber not in self.residuesList:
                self.residuesList.append(resiNumber)

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) in self.constraints.keys():
            del self.constraints[int(aConstraintNumber)]#

#Useful RegEx definitions
Par=re.compile('[()]')# used in cns constraints loading. Suppression of ()
SPar=re.compile("\(.*\)")#used in cns constraint loading.
RegResi=re.compile("RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#]*")#match CNS Residue definition
Sharp=re.compile('[#]')# used in cns constraints loading. Replace # by *
AtType=re.compile('[CHON][A-Z]*')

def cns(cnsFile, managerName):
    """
    Return a ConstraintSetManager loaded with cns/xplor constraints
    """
    fin=open(cnsFile,'r')
    #Avoid formatting issues
    inFileTab=[]
    for txt in fin:
        txt=txt.lstrip()
        if txt.find('!')<0:
            inFileTab.append(txt.upper().rstrip())
        else:
            stderr.write(txt+" skipped. Commented out.\n")
    fin.close()
    validCNSConstraints=[]
    for line in inFileTab:
        if line.find("ASSI")>-1:
            line=line.replace("GN", "")
            validCNSConstraints.append(line.replace("ASSI",""))
        elif RegResi.search(line)!=None:
            validCNSConstraints[-1]=validCNSConstraints[-1]+line

    constraint_number=1
    aManager=ConstraintSetManager(managerName)
    for aConstLine in validCNSConstraints:#itemizing constraints
        #avoid empty lines
        if re.search('\d', aConstLine):
            parsingResult = parseCNSConstraint(aConstLine)
            if len(parsingResult)==3:#2 residues + distances (matches also H-Bonds)
                aConstraint=NOE()
            else:
                #No other constraint type supported ... for now !
                break
            aConstraint.id["number"]=constraint_number
            aConstraint.definition=aConstLine
            for position in range(aConstraint.numberOfAtomsSets):
                currentResidue={}
                if  "resid" in parsingResult[position].keys():
                    currentResidue["number"]=parsingResult[position]["resid"]
                else:
                    currentResidue["number"]=parsingResult[position]["resi"]                        
                currentResidue["atoms"]=AtType.match(parsingResult[position]["name"]).group()
                currentResidue["atoms_number"]=AtType.sub('', parsingResult[position]["name"])
                currentResidue["ambiguity"]=AtType.sub('', parsingResult[position]["name"]).find('*')
                if "segid" in parsingResult[position].keys():
                    currentResidue["segid"]=parsingResult[position]["segid"]
                aConstraint.resis.append(currentResidue)
            aConstraint.setConstraintValues(parsingResult[-1][0],parsingResult[-1][1],parsingResult[-1][2])#Values always at the end of the array
            
            aManager.addConstraint(aConstraint)
            constraint_number=constraint_number+1
        else:
            stderr.write("This line : "+aConstLine+" is not a valid constraint.\n")
            continue
    stdout.write(str(len(aManager.constraints))+" constraints loaded.\n")
    return aManager

def convertTypeDyana(atType):
    """
    Adapt xeasy nomenclature Q to pymol *
    """
    if atType.count('Q'):
        newType=atType.replace('Q','H',1)
        newType=newType+('*') # Q is replaced by H and a star at the end of the atom type
        newType=newType.replace('Q','')# avoid QQ (QQD-> HD*)
        return newType
    else:
        return atType

def dyana(dyanaFile, managerName):
    """"
    Return a ConstraintSetManager loaded with CYANA/DYANA constraints
    """
    fin=open(dyanaFile,'r')
    i=1
    aManager=ConstraintSetManager(managerName)
    for aConstLine in fin:
        if len(aConstLine)>1:
            if aConstLine.lstrip().find('#')==0:
                stderr.write(aConstLine+" skipped. Commented out.\n")
            else:
                cons_tab=aConstLine.split()
                try: #For errors not filtered previously
                    aConstraint=NOE.initWith(i, cons_tab[0], AtType.match(convertTypeDyana(cons_tab[2])).group(),AtType.sub('',convertTypeDyana(cons_tab[2])) ,cons_tab[3], AtType.match(convertTypeDyana(cons_tab[5])).group(), AtType.sub('',convertTypeDyana(cons_tab[5])), aConstLine)
                    aConstraint.setConstraintValues(str(1.8+(float(cons_tab[6])-1.8)/2),'1.8',cons_tab[6])
                    aManager.addConstraint(aConstraint)
                    i=i+1
                except:
                    stderr.write("Unknown error while loading constraint :\n"+aConstLine+"\n")
        else:
            stderr.write("Empty line, skipping.\n")

    fin.close()
    stdout.write(str(len(aManager.constraints))+" constraints loaded.\n")
    return aManager

def parseCNSConstraint(aCNSConstraint):
    """Split CNS/XPLOR type constraint into an array, contening the name of the residues (as arrays),
    and the values of the parameter associated to the constraint. It should be independant
    from the type of constraint (dihedral, distance, ...)
    """
    residuesList=RegResi.findall(aCNSConstraint, re.IGNORECASE)
    constraintValuesList=SPar.sub("", aCNSConstraint).split()
    constraintParsingResult=[]
    for aResidue in residuesList:
        residueParsingResult={}
        for aDefinition in Sharp.sub('*', aResidue).split("AND"):
            definitionArray=aDefinition.split()
            residueParsingResult[definitionArray[0].strip().lower()]=definitionArray[1].strip()
        constraintParsingResult.append(residueParsingResult)
    numericValues=[]
    for aValue in constraintValuesList:
        numericValues.append(float(aValue))
    constraintParsingResult.append(numericValues)
    return constraintParsingResult

class ConstraintDrawer(object):
    """

    """
    def drC(self, selectedConstraint, radius, colors):
        """
        Draw an array of constraints according to the filter defined by user, using the drawConstraint function
        """    
        involvedResidueslist = []
        numberOfDrawnConstraints = 0
        for aConstraint in selectedConstraint:
            if not aConstraint.resis[0]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[0]['number'])
            if not aConstraint.resis[1]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[1]['number'])
            if aConstraint.satisfaction == 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction == 'Satisfied':
                color = colors['Satisfied']
            drawConstraint(aConstraint.points, color, radius, aConstraint.getID())
            numberOfDrawnConstraints = numberOfDrawnConstraints + 1
        return {'Residueslist':involvedResidueslist, 'DrawnConstraints':numberOfDrawnConstraints}

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints by the filter
        """
        list = {}
        constraintsUsed = 0
        for aConstraint in selectedConstraints:
            if not aConstraint.resis[0]['number'] in list.keys():
                list[aConstraint.resis[0]['number']] = 10
            else:
                list[aConstraint.resis[0]['number']] = list[aConstraint.resis[0]['number']] + 10
            if not aConstraint.resis[1]['number'] in list.keys():
                list[aConstraint.resis[1]['number']] = 10
            else:
                list[aConstraint.resis[1]['number']] = list[aConstraint.resis[1]['number']] + 10
            constraintsUsed = constraintsUsed + 1
        return list

    def paD(self, selectedConstraints, pdb, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        zeroBFactors(pdb)
        if len(densityList) > 0:
            for residu in densityList.keys():
                setBfactor(pdb + " & i. " + residu, densityList[residu])
        paintDensity(color_gradient, pdb)
        return densityList

class ConstraintFilter(object):
    """

    """

    def __init__(self, pdb, residuesList, dist_range, violationState, violCutoff, method):
        """Defines parameters for filtering the constraints
        """
        self.parameters = {}
        self.parameters['residuesList'] = residuesList
        self.parameters['range'] = dist_range
        self.parameters['violationState'] = violationState
        self.parameters['cutOff'] = violCutoff
        self.parameters['pdb'] = pdb
        self.parameters['method'] = method

    def filter(self, aConstraint):
        """Filter the constraints to be drawn (there should be a better way to implement it)
        """
        if aConstraint.getRange() in self.parameters['range']:
            inList=0
            for aNumber in aConstraint.getResisNumber():
                if aNumber in self.parameters['residuesList']:
                    inList=1
                    break
            if inList:
                aConstraint.pdbName = self.parameters['pdb']
                if aConstraint.isValid():
                    if aConstraint.setDistance(self.parameters['method']):
                        aConstraint.setViolationState(self.parameters['cutOff'])
                        if aConstraint.isSatifsied() in self.parameters['violationState']:
                            return 1
                        else:
                            return 0
                    else:
                        stderr.write("Distance issue with constraint :\n" + aConstraint.definition+"\n")
                        return 0
                else:
                    stderr.write("Selection issue with constraint :\n" + aConstraint.definition+"\n")
                    return 0    
            else:
                return 0
        else:
            return 0
    
    def filterConstraints(self, constraintList):
        selectedConstraint=[]
        for aConstraint in constraintList:
            if self.filter(aConstraint):
                selectedConstraint.append(aConstraint)
        return selectedConstraint

def centerOfMass(selection):
    ## Author: Andreas Henschel 2006
    ## assumes equal weights
    model = get_model(selection)
    if len(model.atom)>0:
        x,y,z=0,0,0
        for a in model.atom:
            x+= a.coord[0]
            y+= a.coord[1]
            z+= a.coord[2]
        return (x/len(model.atom), y/len(model.atom), z/len(model.atom))
    else:
        stderr.write("selection is empty :"+ str(selection)+"\n")
        return 0,0,0            

#Methods for distance constraints
def calcDistance(selection_init,selection_final,method):
    """
    Choose which method to calculate distances
    """
    if method=='ave6':
        return(averageDistance_6(selection_init,selection_final))
    elif method=='sum6':
        return(sumDistance_6(selection_init,selection_final))
    else:
        stderr.write("This method of calculation is not defined : "+str(method)+"\n")

def averageDistance_6(selection_init,selection_final):
    """
    Calculate distance according to : ((sum of all distances^6)/number of distances)^6
    """
    model_init = get_model(selection_init)
    model_final= get_model(selection_final)
    if len(model_init.atom)>0 and len(model_final.atom)>0:
            distance_list=[]
            for a in model_init.atom:
                for b in model_final.atom:
                    distance_list.append(sqrt(pow((a.coord[0]-b.coord[0]),2)+pow((a.coord[1]-b.coord[1]),2)+pow((a.coord[2]-b.coord[2]),2)))
            sum6=0
            for distance in distance_list:
                try:
                    sum6=sum6+pow(distance,-6)
                except:
                    stderr.write("Problem with selection : "+selection_init+" "+selection_final + "\n" + "distance is : "+str(distance)+" A")
            return pow(sum6/len(distance_list),-1./6)
    else:
        stderr.write("selection is empty : "+selection_init+" "+selection_final+"\n")
        return 0.0

def sumDistance_6(selection_init,selection_final):
    """
    Calculate distance according to : (sum of all distances^6)^-1/6
    """
    model_init = get_model(selection_init)
    model_final= get_model(selection_final)

    if len(model_init.atom)>0 and len(model_final.atom)>0:
            distance_list=[]
            for a in model_init.atom:
                for b in model_final.atom:
                    distance_list.append(sqrt(pow((a.coord[0]-b.coord[0]),2)+pow((a.coord[1]-b.coord[1]),2)+pow((a.coord[2]-b.coord[2]),2)))
            sum6=0
            for distance in distance_list:
                try:
                    sum6=sum6+pow(distance,-6)
                except:
                    stderr.write("Problem with selection : "+selection_init+" "+selection_final + "\n" + "distance is : "+str(distance)+" A")
            result=pow(sum6,-1./6)
            return result

    else:
        stderr.write("selection is empty : "+selection_init+" "+selection_final+"\n")
        return 0.0

class NMRCore(object):
    
    def __init__(self):
        self.ManagersList={}
        self.filter=""
        self.displayedConstraints=[]

    def loadNOE(self, filename, consDef):
        """load NMR distance constraints, call for the correct file format (CNS/CYANA),
        """
        managerName=basename(filename)
        if consDef in ['XPLOR', 'CNS']:
            self.ManagersList[managerName]=cns(filename, managerName)
        elif consDef in ['DYANA', 'CYANA']:
            self.ManagersList[managerName]=dyana(filename,managerName)
        else:
            stderr.write("incorrect or unsupported constraint type.\n")
    
    def showSticks(self, managerName, pdb, colors, radius):
        self.ManagersList[managerName].setPDB(pdb)
        theFilter=self.filter
        drawer=ConstraintDrawer()
        selectedConstraints=[]
        if len(self.ManagersList[managerName].constraints):
            if self.ManagersList[managerName].associateToPDB():
                filteredConstraints=self.filter.filterConstraints(self.ManagersList[managerName].constraints)
                selectedConstraints=[]
                for constraint in filteredConstraints:
                    if constraint not in self.displayedConstraints:
                        selectedConstraints.append(constraint)
                self.displayedConstraints=self.displayedConstraints+selectedConstraints
                results=drawer.drC(selectedConstraints, radius, colors)
                stdout.write(str(results['DrawnConstraints'])+" constraints drawn on a total of "+str(len(self.ManagersList[managerName].constraints))+"\n")            
                zoomSelection=self.ManagersList[managerName].pdb+" &"
                if len(results['Residueslist']):
                    for residue in results['Residueslist']:
                        zoomSelection=zoomSelection+" resi "+residue+" +"
                    zoom(zoomSelection.rstrip(' +'))
                    select('involRes',zoomSelection.rstrip(' +'))
        else:
            stderr.write( "No constraints to draw ! You might want to load a few of them first ...\n")

    def showNOEDensity(self, managerName, pdb, gradient):
        """Seeks for constraints that fit criteria, increases a counter for each residue which has a
         matching constraint. That simulates a density which is then paint on the model according to a color gradient
        """
        self.ManagersList[managerName].setPDB(pdb)
        theFilter=self.filter
        drawer=ConstraintDrawer()
        if len(self.ManagersList[managerName].constraints):
            if self.ManagersList[managerName].associateToPDB():
                selectedConstraints=theFilter.filterConstraints(self.ManagersList[managerName].constraints)
                self.displayedConstraints=self.displayedConstraints+selectedConstraints
                densityList=drawer.paD(selectedConstraints, self.ManagersList[managerName].pdb, gradient)
                zoomSelection=self.ManagersList[managerName].pdb+" &"
                if len(densityList):
                    stdout.write(str(len(selectedConstraints)) + " constraints used.\n")
                    stdout.write(str(len(densityList))+" residues involved.\n")
                    for residue in densityList.keys():
                        zoomSelection=zoomSelection+" resi "+residue+" +"
                    zoom(zoomSelection.rstrip(' +'))
                    select('involRes', zoomSelection.rstrip(' +'))
    
    def commandsInterpretation(self, pdb, managerName, residuesList, dist_range, violationState, violCutoff, method):
        """Setup Filter for constraints
        """
        if residuesList=='all':
            resList=self.ManagersList[managerName].residuesList
        else:
            resList=[]
            for resi_range in residuesList.split("+"):
                aRange=resi_range.split("-")
                if len(aRange)==2:
                    for i in range(int(aRange[0]),int(aRange[1])+1):
                        resList=resList+[str(i)]
                elif len(aRange)==1:
                    resList=resList+[str(aRange)]
                else:
                    stderr.write("Residues set definition error : "+residuesList+"\n")
        if type(dist_range)!=type([]):
            if dist_range=='all':
                dist_range=['intra', 'sequential', 'medium', 'long']
            else:
                dist_range=[dist_range]

        if type(violationState)!=type([]):
            if violationState=='all':
                violationState=['unSatisfied', 'Satisfied']
            else:
                violationState=[violationState]
        self.filter=ConstraintFilter(pdb, resList, dist_range, violationState, violCutoff, method)
    
    def cleanScreen(self, managerName):
        self.displayedConstraints=[]
        delete(managerName+"*")

class Panel(Tk.LabelFrame):
    def __init__(self, master, frameText = ""):
        """Abstract Class
        """
        Tk.LabelFrame.__init__(self, master, text=frameText)

    def getInfo(self):
        return {}

class FileSelectionPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Constraints Files")
        self.widgetCreation()
        self.NMRCommands=""#Must be set by application at run time

    def widgetCreation(self):
        self.constraintFilesButtonBox = Pmw.ButtonBox(self, labelpos = 'nw', orient='vertical')
        self.constraintFilesButtonBox.add("Load Constraints", command=self.loadFile)
        self.constraintFilesButtonBox.add("Remove Constraints", command=self.removeFile)
        self.constraintFilesButtonBox.grid(row=0, column=0)
        self.constraintsList=Pmw.ScrolledListBox(self)
        self.constraintsList.component("listbox").exportselection=0
        self.constraintsList.grid(row=0, column=1)
        self.constraintDefinitions = Pmw.RadioSelect(self, label_text="Select constraints definition type :",labelpos = 'nw', buttontype='radiobutton')
        self.constraintDefinitions.add("CNS/XPLOR")
        self.constraintDefinitions.add("CYANA/DYANA")
        self.constraintDefinitions.setvalue("CNS/XPLOR")
        self.constraintDefinitions.grid(row=1, column=0, columnspan=2)

    def loadFile(self):
        filename=tkFileDialog.askopenfilename(title="Open a constraint " + self.constraintDefinitions.getvalue() + " file ")
        constraintType=""
        if self.constraintDefinitions.getvalue()=="CNS/XPLOR":
            constraintDefinition="CNS"
        else:
            constraintDefinition="CYANA"
        if filename:
            self.NMRCommands.loadNOE(filename, constraintDefinition)
            self.updateFilelist()
            self.constraintsList.setvalue(path.basename(filename))

    def updateFilelist(self):
        self.constraintsList.setlist(self.NMRCommands.ManagersList.keys())

    def removeFile(self):
        toRemove=self.constraintsList.getvalue()
        if toRemove:
            for manager in toRemove:
                del self.NMRCommands.ManagersList[manager]
        self.constraintsList.setlist(self.NMRCommands.ManagersList.keys())

    def getInfo(self):
        if len(self.constraintsList.getvalue()):
            return {"constraintFile":self.constraintsList.getvalue()[0]}
        else:
            return {"constraintFile":""}

class ConstraintSelectionPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Constraints Selection")
        self.panelsList=[]
        self.widgetCreation()

    def widgetCreation(self):
        #Creation of range input
        self.consRangeFrame=RangeSelectionPanel(self)
        self.consRangeFrame.grid(row=0, column=0)
        self.panelsList.append(self.consRangeFrame)

        #Creation of Violations inputs
        self.violationsFrame=ViolationSelectionPanel(self)
        self.violationsFrame.grid(row=0, column=1)
        self.panelsList.append(self.violationsFrame)

        #Creation of structure inputs
        self.structureManagement = StructureSelectionPanel(self)
        self.structureManagement.grid(row=1, column=0, columnspan=2)
        self.panelsList.append(self.structureManagement)

    def getInfo(self):
        infos={}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos

class StructureSelectionPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Structure")
        self.residueRanges=Tk.StringVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text="Structure :").grid(row=0, column=0)
        x=Pmw.EntryField()#Do not remove this line if combobox is the first Pmw combobox, Pmw bug
        self.comboPDB=Pmw.ComboBox(self)
        self.comboPDB.grid(row=0, column=1)
        self.comboPDB.bind('<Enter>', self.updatePdbList)

        Tk.Label(self, text='Residues ranges :').grid(row=2, column=0, sticky=Tk.W)
        self.entry_res=Tk.Entry(self, textvariable=self.residueRanges)
        self.entry_res.grid(row=2, column=1)
        self.residueRanges.set('all')

    def getInfo(self):
        return {"pdb":self.comboPDB.component("entryfield").getvalue(), "ranges":self.residueRanges.get()}
    
    def updatePdbList(self, event):
        self.comboPDB.setlist(self.mainGUI.getModelsNames())

class NOEDrawingPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE Representation")
        self.widgetCreation()
        self.mainGUI=""#Must be set at run time
        self.NMRCommands=""#Must be set by application at run time

    def widgetCreation(self):
        self.drawingNOEButtonBox = Pmw.ButtonBox(self, orient='horizontal')
        self.drawingNOEButtonBox.add('Sticks', command = self.showSticks)
        self.drawingNOEButtonBox.add('Density', command = self.showDensity)
        self.drawingNOEButtonBox.add('Clean NOEs', command = self.cleanAll)
        self.drawingNOEButtonBox.grid(row=0, column=0)
        self.drawingNOEButtonBox.setdefault('Sticks')

    def showSticks(self):
        infos= self.mainGUI.getInfo()
        infoCheck=1

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["pdb"], infos["constraintFile"], infos["ranges"], infos["residuesRange"], infos["violationState"], infos["cutOff"], infos["method"])
            self.NMRCommands.showSticks(infos["constraintFile"], infos["pdb"], infos["colors"], infos["radius"])

    def showDensity(self):
        infos= self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["pdb"], infos["constraintFile"], infos["ranges"], infos["residuesRange"], infos["violationState"], infos["cutOff"], infos["method"])
            self.NMRCommands.showNOEDensity(infos["constraintFile"], infos["pdb"], infos["gradient"])

    def cleanAll(self):
        infos= self.mainGUI.getInfo()
        
        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen(infos["constraintFile"])

    def infoCheck(self, infos):
        check=1
        for item in infos:
            if infos[item]=="":
                check=0
                break
        return check

class RangeSelectionPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Range Selection")

        self.RangesVars={}
        self.RangesCB={}
        self.RangesFunctions={}
        self.widgetCreation()

    def widgetCreation(self):
        rowPosition=0
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            self.RangesVars[consRange]=Tk.IntVar(self)
            self.RangesCB[consRange]=Tk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
            rowPosition=rowPosition+1
        self.RangesVars["all"]=Tk.IntVar(self)
        self.RangesCB["all"]=Tk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        if self.RangesVars["all"].get()==1:
            for consRange in ['intra', 'sequential', 'medium', 'long']:
                self.RangesCB[consRange].select()
        if self.RangesVars["all"].get()==0:
            for consRange in ['intra', 'sequential', 'medium', 'long']:
                self.RangesCB[consRange].deselect()
    def tick(self):
        self.RangesCB["all"].select()
        for aRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[aRange].get()==0:
                self.RangesCB["all"].deselect()
                break
    def getInfo(self):
        ranges=[]
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[consRange].get()==1:
                ranges.append(consRange)
        return {"residuesRange":ranges}

class ViolationSelectionPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="Violation state Selection")

        self.ViolationsVars={}
        self.UnSatifsiedCB={}
        self.cutOff=Tk.DoubleVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        rowPosition=0
        for violationType in ['unSatisfied', 'Satisfied']:
            self.ViolationsVars[violationType]=Tk.IntVar(self)
            self.UnSatifsiedCB[violationType]=Tk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatifsiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W)
            self.UnSatifsiedCB[violationType].select()
            rowPosition=rowPosition+1

        Tk.Label(self, text='Distance CutOff (A)').grid(row=rowPosition+1, column=0)

        self.spinBox_cutOff=Tk.Spinbox(self, textvariable=self.cutOff, from_=0.0, to=10.0, increment=0.1)
        self.spinBox_cutOff.grid(row=rowPosition+2, column=0)

    def getInfo(self):
        violationState=[]
        for violationType in ['unSatisfied','Satisfied']:
            if self.ViolationsVars[violationType].get()==1:
                violationState.append(violationType)
        return {"cutOff":self.cutOff.get(), "violationState":violationState}

class SticksPreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE Sticks Preferences")
        self.radius=Tk.DoubleVar(self)
        self.colors={}
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='Stick radius (A):').grid(row=0, column=0)
        self.spinBox_Radius=Tk.Spinbox(self, textvariable=self.radius, from_=0.00, to=0.5, increment=0.01)
        self.spinBox_Radius.grid(row=0, column=1)
        Tk.Label(self, text='Satisfied constraint').grid(row=1, column=0)
        self.satisfiedColorButton=Tk.Button(self, text="Choose color", command=self.setSatisfiedColor)
        self.satisfiedColorButton.grid(row=1, column=1)
        Tk.Label(self, text="Atoms too far").grid(row=2, column=0)
        self.tooFarButton=Tk.Button(self, text="Choose color", command=self.setTooFarColor)
        self.tooFarButton.grid(row=2, column=1)
        Tk.Label(self, text="Atoms too close").grid(row=3, column=0)
        self.tooCloseButton=Tk.Button(self, text="Choose color", command=self.setTooCloseColor)
        self.tooCloseButton.grid(row=3, column=1)

    def getInfo(self):
        return {"radius":self.radius.get(), "colors":self.colors}

    def setSatisfiedColor(self):
        currentColor = self.float2intColor(self.colors["satisfied"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["satisfied"]=self.int2floatColor(result[0])

    def setTooFarColor(self):
        currentColor = self.float2intColor(self.colors["tooFar"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooFar"]=self.int2floatColor(result[0])

    def setTooCloseColor(self):
        currentColor = self.float2intColor(self.colors["tooClose"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooClose"]=self.int2floatColor(result[0])

    #This should be in an different file probably
    def float2intColor(self, color):
        return (int(color[0]*255), int(color[1]*255), int(color[2]*255))

    def int2floatColor(self, color):
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0, color[0]/255.0, color[1]/255.0, color[2]/255.0]
    
class DensityPreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE density Preferences")
        self.gradient=Tk.StringVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='Gradient :').grid(row=0, column=0)
        x=Pmw.EntryField()#Do not remove this line if combobox is the first Pmw combobox, Pmw bug
        self.gradientSelection = Pmw.ComboBox(self)
        self.gradientSelection.grid(row=0, column=1)
    
    def getInfo(self):
        return {"gradient":self.gradientSelection.component("entryfield").getvalue()}

class PreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE Preferences")
        self.panelsList=[]
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='NOE Distance calculation :\n(> 2 atoms)').grid(row=0, column=0)

        self.methodSelection = Pmw.RadioSelect(self, buttontype='radiobutton', orient='vertical')
        self.methodSelection.add("sum6", text="Sum of r^6")
        self.methodSelection.add("average6", text="Average of r^6")
        self.methodSelection.grid(row=0, column=1)
        self.methodSelection.setvalue("sum6")

        self.sticksPanel = SticksPreferencesPanel(self)
        self.sticksPanel.grid(row=1, column=0, columnspan=2)
        self.panelsList.append(self.sticksPanel)

        self.densityPanel = DensityPreferencesPanel(self)
        self.densityPanel.grid(row=2, column=0, columnspan=2)
        self.panelsList.append(self.densityPanel)

    def getInfo(self):
        infos={"method":self.methodSelection.getvalue()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos

class NMRGUI(Tk.Tk):
    def __init__ (self):
        Tk.Tk.__init__(self)
        self.title('PymolNMR')
        self.panelsList=[]
        
    def createPanels(self):
        #Main Frames (not IBM)
        
        self.noteBook = Pmw.NoteBook(self)
        self.mainPage = self.noteBook.add("Main")
        
        self.constraintSelectionManagement = ConstraintSelectionPanel(self.mainPage)
        self.panelsList.append(self.constraintSelectionManagement)

        self.constraintFilesManagement = FileSelectionPanel(self.mainPage)
        self.panelsList.append(self.constraintFilesManagement)

        self.NOEDrawingManagement = NOEDrawingPanel(self.mainPage)
        self.panelsList.append(self.NOEDrawingManagement)

        self.preferencesPage = self.noteBook.add("Preferences")

        self.preferencesPanel= PreferencesPanel(self.preferencesPage)
        self.panelsList.append(self.preferencesPanel)
    
        self.constraintFilesManagement.grid(row=0, column=0)
        self.constraintSelectionManagement.grid(row=1, column=0)
        self.NOEDrawingManagement.grid(row=2, column=0)
        self.preferencesPanel.grid(row=0, column=0)        
        self.noteBook.setnaturalsize()

    def startGUI(self):
        self.createPanels()
        self.noteBook.grid(row=0, column=0)
        self.setDelegation()

    def setDelegation(self):
        self.NOEDrawingManagement.mainGUI=self
        
    def getInfo(self):
        infos={}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos#Needed to upload custom modules

Core=NMRCore()
    
class NMRApplication(object):
    def __init__(self, Core):
        self.NMRCommands = Core        
        self.log=""
        self.defaults={"radius":0.03, "cutOff":0.3, "colors":{'satisfied':[1,1,1,1,1,1],'tooFar':[1,0,0,1,0,0],'tooClose':[0,0,1,0,0,1]}, 'gradient':"blue_white_red"}

    def startGUI(self):
        self.NMRInterface = NMRGUI()
        self.NMRInterface.startGUI()
        self.GUIBindings()        
        self.setDefaults()
    
    def setDefaults(self):
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection.setlist( ["blue_green","blue_magenta","blue_red","blue_white_green","blue_white_magenta","blue_white_red","blue_white_yellow","blue_yellow","cbmr","cyan_magenta","cyan_red","cyan_white_magenta","cyan_white_red","cyan_white_yellow","cyan_yellow","gcbmry","green_blue","green_magenta","green_red","green_white_blue","green_white_magenta","green_white_red","green_white_yellow","green_yellow","green_yellow_red","magenta_blue","magenta_cyan","magenta_green","magenta_white_blue","magenta_white_cyan","magenta_white_green","magenta_white_yellow","magenta_yellow","rainbow","rainbow2","rainbow2_rev","rainbow_cycle","rainbow_cycle_rev","rainbow_rev red_blue","red_cyan red_green","red_white_blue","red_white_cyan","red_white_green","red_white_yellow","red_yellow","red_yellow_green","rmbc","yellow_blue","yellow_cyan","yellow_cyan_white","yellow_green","yellow_magenta","yellow_red","yellow_white_blue","yellow_white_green","yellow_white_magenta","yellow_white_red","yrmbcg"])
        self.NMRInterface.preferencesPanel.densityPanel.gradientSelection.component("entryfield").setvalue(self.defaults["gradient"])
        self.NMRInterface.preferencesPanel.sticksPanel.colors=self.defaults["colors"]
        self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
        self.NMRInterface.constraintSelectionManagement.violationsFrame.cutOff.set(self.defaults["cutOff"])
        self.NMRInterface.constraintSelectionManagement.structureManagement.comboPDB.setlist(self.getModelsNames())
        self.NMRInterface.constraintFilesManagement.updateFilelist()

    def GUIBindings(self):
        self.NMRInterface.constraintFilesManagement.NMRCommands=self.NMRCommands
        self.NMRInterface.NOEDrawingManagement.NMRCommands=self.NMRCommands
        self.NMRInterface.constraintSelectionManagement.structureManagement.mainGUI=self
    
    def getModelsNames(self):
        results=[]
        objectsLists=get_names()
        for name in objectsLists:
            if len(self.NMRCommands.ManagersList):
                for managerName in self.NMRCommands.ManagersList.keys():
                    if name.find(managerName)<0:
                        if name not in results:
                            results.append(name)
            else:
                if name not in results:
                    results.append(name)
        return results

pyNMR=NMRApplication(Core)

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
    if managerName=='' and len(Core.ManagersList)==0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName=='':
            managerName=Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
            Core.showSticks(managerName, pdb, colors, radius)
        else:
            stderr.write("Please check constraints filename.\n")

def loadNOE(filename="", consDef=""):
    """load NMR distance constraints, call for the correct file format (CNS/CYANA),
    """
    if exists(filename):
        Core.loadNOE(filename, consDef.upper())
    else:
        stderr.write("File : "+ filename +" has not been found.\n")

def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method='sum6', colors=pyNMR.defaults["gradient"]):
    if managerName=='' and len(Core.ManagersList)==0:
        stderr.write("No constraints loaded.\n")
    else:
        if managerName=='':
            managerName=Core.ManagersList.keys()[0]
        if managerName in Core.ManagersList:
            Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
            Core.showNOEDensity(managerName, pdb, colors)
        else:
            stderr.write("Please check constraints filename.\n")

def loadAndShow(filename, consDef, pdb='', residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
    """
    """
    loadNOE(filename, consDef)
    showNOE(pdb,filename, residuesList, dist_range, violationState, violCutoff, method, radius, colors)

def cleanScreen(filename):
    if filename in Core.ManagersList:
        Core.cleanScreen(filename)

extend("loadNOE", loadNOE)
extend("showNOE", showNOE)
extend("showNOEDensity", showNOEDensity)
extend("loadAndShow", loadAndShow)

def __init__(self):
    self.menuBar.addmenuitem('Plugin', 'command', 'PyNMR', label = 'PyNMR', command = lambda s=self : pyNMR.startGUI())
