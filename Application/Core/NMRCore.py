
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
from os.path import basename, exists
import sys
from sys import stderr
import urllib2
import shutil
import gzip
import tempfile

# Custom Classes
from ConstraintLoading import ConstraintLoader
from Filtering import ConstraintFilter
from ConstraintsDrawing import ConstraintDrawer
import MolecularViewerInterface as MVI
from ConstraintManager import ConstraintSetManager


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
        managerName = basename(filename)
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
                self.displayedConstraints.constraints.extend(selectedConstraints)
                if len(selectedConstraints) > 0:
                    selection = MVI.createSelection(self.ManagersList[managerName].structure, self.displayedConstraints.residuesList)
                    MVI.select('involRes', selection)
                    MVI.zoom(selection)
        else:
            stderr.write("No constraints to draw ! You might want to load a few of them first ...\n")

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
                self.displayedConstraints.constraints.extend(selectedConstraints)
                densityList = drawer.paD(selectedConstraints,
                                         self.ManagersList[managerName].structure,
                                         gradient)
                if densityList:
                    zoomSelection = MVI.createSelection(self.ManagersList[managerName].structure, densityList.keys())
                    MVI.zoom(zoomSelection)
                    MVI.select('involRes', zoomSelection)

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
                    resList += [str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[1]) + 1)]
                elif len(aRange) == 1:
                    resList += [str(aRange[0])]
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
        self.constraintFilter = ConstraintFilter(structure, resList, dist_range,
                                                 violationState, violCutoff,
                                                 method, rangeCutOff)

    def cleanScreen(self, managerName):
        """Remove all sticks from pymol
        """
        self.displayedConstraints.removeAllConstraints()
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
            if exists(zippedFileName):
                os.remove(zippedFileName)
                self.loadNOE(PDBfileName)
                os.remove(PDBfileName)
                os.chdir(workdir)
                os.removedirs(tempDownloadDir)
        except IOError:
            sys.stderr.write("Error while downloading or opening " +
                             pdbCode + " NMR Restraints file from PDB.\n")
