"""Module for drawing constraints
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
from ConstraintManager import ConstraintSetManager
from MolecularViewerInterfaces import MolecularViewerInterface as MVI


class ConstraintDrawer(object):
    """

    """
    def __init__(self, UnSatisfactionMarker="", SatisfactionMarker=""):
        """
        """
        self.UnSatisfactionMarker = UnSatisfactionMarker
        self.SatisfactionMarker = SatisfactionMarker
        self.displayedConstraintsSticks = ConstraintSetManager("")
        self.displayedConstraintsDensity = ConstraintSetManager("")

    def drC(self, selectedConstraints, radius, colors):
        """
        Draw an array of constraints according to the filter defined by user,
        using the drawConstraint function
        """
        tempList = list()
        for number, aConstraint in enumerate(selectedConstraints):
            if len(self.displayedConstraintsSticks) > number:
                try:
                    MVI.delete(self.IDConstraint(aConstraint))
                    self.displayedConstraintsSticks.removeConstraint(aConstraint)
                except ValueError:
                    pass
            if aConstraint.satisfaction() is 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction() is 'Satisfied':
                color = colors['Satisfied']
            self.displayedConstraintsSticks.append(aConstraint)
            tempList.append(tuple([aConstraint.points, color, radius, self.IDConstraint(aConstraint)]))
        # do not merge previous and next loops ! It creates a thread race which severly slows down the display in pymol
        for aConstraint in tempList:
            MVI.drawConstraint(*aConstraint)

        return self.displayedConstraintsSticks.atomsList

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
        """
        densityStep = 10
        densityList = dict()

        tempList = list()
        for number, aConstraint in enumerate(selectedConstraints):
            if len(self.displayedConstraintsDensity) > number:
                try:
                    self.displayedConstraintsDensity.removeConstraint(aConstraint)
                    MVI.delete(self.IDConstraint(aConstraint))
                except ValueError:
                    pass
            tempList.append(aConstraint)
        # do not merge previous and next loops ! It creates a thread race which severly slows down the display in pymol
        for aConstraint in tempList:
            for atom in aConstraint.atoms:
                densityList[atom] = densityList.get(atom, 0) + densityStep
            self.displayedConstraintsDensity.append(aConstraint)

        return densityList

    def paD(self, selectedConstraints, structure, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        bFactors = dict()
        for atom in densityList:
            bFactors[atom.resi_number] = bFactors.get(atom.resi_number, 0) + densityList[atom]
        MVI.zeroBFactors(structure)
        for residu, density in bFactors.iteritems():
            MVI.setBfactor(structure, residu, density)
        MVI.paintDensity(color_gradient, structure)
        return densityList.keys()

    def IDConstraint(self, aConstraint):
        """Returns name of constraints :
        Name_(constraint number)_(structureName)_(violation_state)
        """
        if aConstraint.satisfaction() is 'Satisfied':
            marker = self.SatisfactionMarker
        elif aConstraint.satisfaction() is 'unSatisfied':
            marker = self.UnSatisfactionMarker
        else:
            marker = ""

        return aConstraint.name + str(aConstraint.id['number']) + marker + aConstraint.structureName
