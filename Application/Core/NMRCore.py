"""load CNS or DYANA distances constraints files
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

# Required modules
from os.path import basename
from sys import stderr, stdout
# Custom Classes
from ConstraintLoading import ConstraintLoader
from Filtering import ConstraintFilter
from ConstraintsDrawing import ConstraintDrawer
import MolecularViewerInterface as MVI
import urllib2
import shutil
import gzip
import os
import sys
import tempfile


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
                stdout.write(str(results['DrawnConstraints']) +
                             " constraints drawn on a total of " +
                             str(len(self.ManagersList[managerName])) + "\n")
                selection = MVI.createSelection([self.ManagersList[managerName].structure] + results['Residueslist'])
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
                    stdout.write(str(len(selectedConstraints)) + " constraints used.\n")
                    stdout.write(str(len(densityList)) + " residues involved.\n")
                    zoomSelection = MVI.createSelection([self.ManagersList[managerName].structure] + densityList.keys())
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
        MVI.delete(managerName + "*")

    def saveConstraintsFile(self, aManagerName, fileName):
        """
        """
        fout = open(fileName, 'w')
        fout.write(self.ManagersList[aManagerName].fileText)
        fout.close()

    def downloadFromPDB(self, pdbCode):
        """
        """
        url = "ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/"
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
