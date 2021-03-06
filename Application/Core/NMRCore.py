
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
from os import path
from sys import stderr
import urllib2
import shutil
import gzip
import tempfile
from collections import MutableMapping

# Custom Classes
from Application.Core.ConstraintLoading import loadConstraintsFromFile
from Application.Core.Filtering import NOEFilter
from Application.Core.ConstraintsDrawing import ConstraintDrawer
from Application.Core.MolecularViewerInterfaces import MolecularViewerInterface as MVI
import Application.Core.errors as errors


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
        try:
            return self.ManagersList[key]
        except ValueError:
            raise ValueError("No constraintManager named " + str(key) + "\n")
            
    def __setitem__(self, key, item):
        self.ManagersList[key] = item

    def __delitem__(self, key):
        try:
            del self.ManagersList[key]
        except ValueError:
            raise ValueError("No constraintManager named " + str(key) + "\n")

    def __iter__(self):
        return self.ManagersList.__iter__()

    def __len__(self):
        return len(self.ManagersList)

    def LoadConstraints(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = path.basename(filename)
        self[managerName] = loadConstraintsFromFile(filename, managerName)

    def showSticks(self, managerName, structure, colors, radius,
                   UnSatisfactionMarker, SatisfactionMarker):
        """Display distance constraints as sticks between groups of atoms.
        """
        self.drawer.UnSatisfactionMarker, self.drawer.SatisfactionMarker = UnSatisfactionMarker, SatisfactionMarker
        self.showConstraints(managerName, structure, colors=colors, radius=radius, displayFunction=self.drawer.drC)

    def showNOEDensity(self, managerName, structure, gradient):
        """Display number of constraints per residue as a simulated density
        which is then paint on the model according to a color gradient
        """
        self.showConstraints(managerName, structure, gradient=gradient, displayFunction=self.drawer.paD)

    def showConstraints(self, managerName, structure, displayFunction=None, colors=None,
                        radius=None, gradient=None):
        """Seeks for constraints that fit criteria and call the appropriate display function.
        """
        with errors.errorLog():
            self[managerName].setPDB(structure)
            try:
                if self[managerName].associateToPDB():
                    selectedConstraints = (aConstraint for aConstraint in self[managerName] if self.constraintFilter(aConstraint))
                    if colors:
                        selectedAtoms = displayFunction(selectedConstraints,
                                                        radius, colors)
                    if gradient:
                        selectedAtoms = displayFunction(selectedConstraints,
                                                        self[managerName].structure,
                                                        gradient)
                    if selectedAtoms:
                        MVI.zoom(self[managerName].structure, selectedAtoms)
                else:
                    errors.add_error_message("No structure selected.")
            except ValueError:
                errors.add_error_message("No constraints to draw ! You might want to load a few of them first ...")

    def commandsInterpretation(self, managerName, residuesList, dist_range, violationState,
                               violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if not residuesList:
            residuesList = set(str(aResidueNumber) for aResidueNumber in self[managerName].residuesList)
        self.constraintFilter = NOEFilter(residuesList, dist_range, violationState,
                                          violCutoff, method, rangeCutOff)

    def cleanScreen(self):
        """Remove all sticks
        """
        for aConstraint in self.drawer.displayedConstraintsSticks:
            MVI.delete(self.drawer.IDConstraint(aConstraint))
        del self.drawer.displayedConstraintsSticks[:]

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
        tempDownloadDir = tempfile.mkdtemp()
        localPDBFilePath = path.join(tempDownloadDir, PDBConstraintsFileName)
        localZippedFilePath = path.join(tempDownloadDir, zippedFileName)
        try:
            restraintFileRequest = urllib2.urlopen(urllib2.Request(url+zippedFileName))
            localFile = open(localZippedFilePath, 'wb')
            shutil.copyfileobj(restraintFileRequest, localFile)
            localFile.close()
            restraintFileRequest.close()
            with gzip.open(localZippedFilePath, 'rb') as zippedFile:
                decodedFile = zippedFile.read()
                with open(localPDBFilePath, 'w') as restraintFile:
                    restraintFile.write(decodedFile)
            self.LoadConstraints(localPDBFilePath)
        except IOError:
            stderr.write("Error while downloading or opening " +
                             pdbCode + " NMR Restraints file from PDB website.\n")
        finally:
            shutil.rmtree(tempDownloadDir)

    def getModelsNames(self, satisfactionMarker="", unSatisfactionMarker=""):
        return MVI.getModelsNames(satisfactionMarker, unSatisfactionMarker)
