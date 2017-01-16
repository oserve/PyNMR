
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

# Standard modules
import os
import os.path as path
import sys
import urllib2
import shutil
import gzip
import tempfile
from collections import MutableMapping

# Custom Classes
from ConstraintLoading import loadConstraintsFromFile
from Filtering import ConstraintFilter
from ConstraintsDrawing import ConstraintDrawer
import MolecularViewerInterface as MVI
from ConstraintManager import ConstraintSetManager
import errors


class NMRCore(MutableMapping):
    """Low Level Interface Class
    for loading and displaying constraints
    """
    def __init__(self):
        self.ManagersList = dict()
        self.constraintFilter = None
        self.displayedConstraintsSticks = ConstraintSetManager('Sticks')
        self.displayedConstraintsDensity = ConstraintSetManager('Density')

    def __getitem__(self, key):
        """Return a constraint Manager
        """
        if key in self.ManagersList:
            return self.ManagersList[key]
        else:
            raise ValueError("No constraintManager named " + str(key) + "\n")

    def __setitem__(self, key, item):
        self.ManagersList[key] = item

    def __delitem__(self, key):
        if key in self.ManagersList:
            del self.ManagersList[key]
        else:
            raise ValueError("No constraintManager named " + str(key) + "\n")

    def __iter__(self):
        return self.ManagersList.__iter__()

    def __len__(self):
        return len(self.ManagersList)

    def get(self, key, alternative):
        """
        """
        if key in self.ManagersList:
            return self.ManagersList[key]
        else:
            return alternative

    def keys(self):
        """
        """
        return self.ManagersList.keys()

    def loadNOE(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = path.basename(filename)
        self.ManagersList[managerName] = loadConstraintsFromFile(filename, managerName)

    def showSticks(self, managerName, structure, colors, radius,
                   UnSatisfactionMarker, SatisfactionMarker):
        """Seeks for constraints that fit some criteria.
        """
        with errors.errorLog():
            self.ManagersList[managerName].setPDB(structure)
            drawer = ConstraintDrawer(UnSatisfactionMarker, SatisfactionMarker)
            if self.ManagersList[managerName]:
                if self.ManagersList[managerName].associateToPDB():
                    for aConstraint in self.ManagersList[managerName]:
                        if aConstraint in self.displayedConstraintsSticks:
                            self.displayedConstraintsSticks.removeConstraint(aConstraint)
                            MVI.delete(drawer.IDConstraint(aConstraint))
                    self.constraintFilter.constraints = self.ManagersList[managerName]
                    selectedConstraints = [constraint for constraint in self.constraintFilter]
                    drawer.drC(selectedConstraints, radius, colors)
                    self.displayedConstraintsSticks.extend(selectedConstraints)
                    if len(selectedConstraints) > 0:
                        selection = MVI.createSelection(self.ManagersList[managerName].structure, self.displayedConstraintsSticks.atomsList)
                        MVI.select('involRes', selection)
                        MVI.zoom(selection)
            else:
                errors.add_error_message("No constraints to draw ! You might want to load a few of them first ...\n")

    def showNOEDensity(self, managerName, structure, gradient):
        """Seeks for constraints that fit criteria, increases a counter for
        each residue which has a matching constraint. That simulates a density
        which is then paint on the model according to a color gradient
        """
        with errors.errorLog():
            self.ManagersList[managerName].setPDB(structure)
            drawer = ConstraintDrawer()
            if self.ManagersList[managerName]:
                if self.ManagersList[managerName].associateToPDB():
                    self.displayedConstraintsDensity.removeConstraints(self.ManagersList[managerName])
                    self.constraintFilter.constraints = self.ManagersList[managerName]
                    selectedConstraints = [constraint for constraint in self.constraintFilter]
                    self.displayedConstraintsDensity.extend(selectedConstraints)
                    densityList = drawer.paD(selectedConstraints,
                                            self.ManagersList[managerName].structure,
                                            gradient)
                    if densityList:
                        zoomSelection = MVI.createSelection(self.ManagersList[managerName].structure, densityList)
                        MVI.zoom(zoomSelection)
                        MVI.select('involRes', zoomSelection)

    def commandsInterpretation(self, structure, managerName, residuesList, dist_range,
                                violationState, violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if len(residuesList) == 0:
            residuesList = self.ManagersList[managerName].residuesList

        self.constraintFilter = ConstraintFilter(structure, residuesList, dist_range, violationState,
                                                 violCutoff, method, rangeCutOff)

    def cleanScreen(self, managerName):
        """Remove all sticks
        """
        self.displayedConstraintsSticks.removeAllConstraints()
        MVI.delete(managerName + "*")

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
