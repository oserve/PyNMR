
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
        self.drawer = ConstraintDrawer()

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

    def get(self, key, default=None):
        """
        """
        try:
            return self.ManagersList[key]
        except ValueError:
            return default

    def keys(self):
        """
        """
        return self.ManagersList.keys()

    def LoadConstraints(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = path.basename(filename)
        self[managerName] = loadConstraintsFromFile(filename, managerName)

    def showSticks(self, managerName, structure, colors, radius,
                   UnSatisfactionMarker, SatisfactionMarker):
        """Seeks for constraints that fit some criteria.
        """
        with errors.errorLog():
            self[managerName].setPDB(structure)
            self.drawer.UnSatisfactionMarker, self.drawer.SatisfactionMarker = UnSatisfactionMarker, SatisfactionMarker
            try:
                if self[managerName].associateToPDB():
                    self.constraintFilter.constraints = self[managerName]
                    selectedAtoms = self.drawer.drC(self.constraintFilter, radius, colors)
                    if len(selectedAtoms) > 0:
                        selection = MVI.createSelection(self[managerName].structure, selectedAtoms)
                        MVI.select('involvedRes', selection)
                        MVI.zoom(selection)
                else:
                    errors.add_error_message("No structure selected.")
            except ValueError:
                errors.add_error_message("No constraints to draw ! You might want to load a few of them first ...")

    def showNOEDensity(self, managerName, structure, gradient):
        """Seeks for constraints that fit criteria, increases a counter for
        each residue which has a matching constraint. That simulates a density
        which is then paint on the model according to a color gradient
        """
        with errors.errorLog():
            self[managerName].setPDB(structure)
            try:
                if self[managerName].associateToPDB():
                    self.constraintFilter.constraints = self[managerName]
                    densityList = self.drawer.paD(self.constraintFilter,
                                                  self[managerName].structure,
                                                  gradient)
                    if len(densityList) > 0:
                        zoomSelection = MVI.createSelection(self[managerName].structure, densityList)
                        MVI.zoom(zoomSelection)
                        MVI.select('involvedRes', zoomSelection)
                else:
                    errors.add_error_message("No structure selected.")
            except ValueError:
                errors.add_error_message("No constraints to draw ! You might want to load a few of them first ...")

    def commandsInterpretation(self, structure, managerName, residuesList, dist_range,
                                violationState, violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if len(residuesList) == 0:
            residuesList = set(str(aResidueNumber) for aResidueNumber in self[managerName].residuesList)

        self.constraintFilter = ConstraintFilter(structure, residuesList, dist_range, violationState,
                                                 violCutoff, method, rangeCutOff)

    def cleanScreen(self, managerName):
        """Remove all sticks
        """
        self.drawer.displayedConstraintsSticks.removeAllConstraints()
        MVI.delete(managerName + "*")

    def saveConstraintsFile(self, aManagerName, fileName):
        """Save the selected constraint file under the format
        it has been loaded.
        """
        with open(fileName, 'w') as fout:
            fout.write(self[aManagerName].fileText)

    def downloadFromPDB(self, pdbCode, url):
        """Download constraint file from wwwPDB
        if available.
        """
        PDBConstraintsFileName = pdbCode.lower() + ".mr"
        zippedFileName = PDBConstraintsFileName + ".gz"
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
                with open(PDBConstraintsFileName, 'w') as restraintFile:
                    restraintFile.write(decodedFile)
            if path.exists(zippedFileName):
                os.remove(zippedFileName)
                self.LoadConstraints(PDBConstraintsFileName)
                os.remove(PDBConstraintsFileName)
                os.chdir(workdir)
                os.removedirs(tempDownloadDir)
        except IOError:
            sys.stderr.write("Error while downloading or opening " +
                             pdbCode + " NMR Restraints file from PDB.\n")
