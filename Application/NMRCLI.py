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
from sys import stderr, stdout
from os.path import exists, basename
import re
from DataControllers import NOEDataController

regInput = re.compile(r'[^0-9\+\-\,]')

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
            if managerName == '' and len(self.Core) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.keys()[0]
                if managerName in self.Core:
                    residuesList, dist_range, violationState = interpret(dist_range, violationState, residuesList)
                    self.Core.commandsInterpretation(structure, managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showSticks(managerName, structure, colors, radius,
                                         UnSatisfactionMarker, SatisfactionMarker)

                    self.dataControllers[managerName] = NOEDataController(self.Core, managerName, structure)
                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].residuesList])) +
                                 " residues involved.\n")

                else:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def LoadConstraints(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        if exists(filename):
            self.Core.LoadConstraints(filename)
            stdout.write(str(len(self.Core[basename(filename)])) + " constraints loaded.\n")

        else:
            stderr.write("File : " + filename + " has not been found.\n")

    def showNOEDensity(self, structure, managerName, residuesList, dist_range,
                       violationState, violCutoff, rangeCutOff, method, colors):
        """Command to display NMR restraints as color map on protein structure with
        different parameters : filtering according to distance, restraints display
        options
        """
        if structure != '':
            if managerName == '' and len(self.Core) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.keys()[0]
                if managerName in self.Core:
                    dist_range, violationState, residuesList = interpret(dist_range, violationState, residuesList)

                    self.Core.commandsInterpretation(structure, managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showNOEDensity(managerName, structure, colors)
                    self.dataControllers[managerName] = NOEDataController(self.Core, managerName, structure)

                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].residuesList])) +
                                 " residues involved.\n")
                else:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def loadAndShow(self, filename, structure, residuesList, dist_range,
                    violationState, violCutoff, method, rangeCutOff,
                    radius, colors, UnSatisfactionMarker, SatisfactionMarker):
        """Combine two previous defined functions : load and display"""
        self.LoadConstraints(filename)
        self.showNOE(structure, basename(filename), residuesList, dist_range,
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
        if filename in self.Core:
            self.Core.cleanScreen(filename)
            del self.dataControllers[filename]

def interpret(dist_range, violationState, residuesList):
    """
    """
    resList = set()
    if len(regInput.findall(residuesList)) == 0:
        for resi_range in residuesList.split("+"):
            aRange = resi_range.split("-")
            if 1 <= len(aRange) <= 2:
                resList.update(str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[-1]) + 1))
            else:
                stderr.write("Residues set definition error : " + residuesList + "\n")
    if dist_range == 'all':
        dist_range = ('intra', 'sequential', 'medium', 'long')
    else:
        dist_range = tuple(dist_range)

    if violationState == 'all':
        violationState = ('unSatisfied', 'Satisfied')
    else:
        violationState = tuple(violationState)

    return (dist_range, violationState, resList)
