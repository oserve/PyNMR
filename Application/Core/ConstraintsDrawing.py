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

import MolecularViewerInterface as MVI
from ConstraintID import IDConstraint


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
        for aConstraint in selectedConstraints:
            if not aConstraint.resis[0]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[0]['number'])
            if not aConstraint.resis[1]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[1]['number'])
            if aConstraint.satisfaction == 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction == 'Satisfied':
                color = colors['Satisfied']
            MVI.drawConstraint(aConstraint.points, color, radius,
                               IDConstraint(aConstraint,
                                            self.UnSatisfactionMarker,
                                            self.SatisfactionMarker))
        return {'Residueslist': involvedResidueslist,
                'DrawnConstraints': len(selectedConstraints)}

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
        """
        densityStep = 10
        constraintList = {}
        for aConstraint in selectedConstraints:
            for resi in aConstraint.resis:
                constraintList[resi['number']] = constraintList.get(resi['number'], 0) + densityStep

        return constraintList

    def paD(self, selectedConstraints, structure, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        MVI.zeroBFactors(structure)
        for residu, density in densityList.iteritems():
            MVI.setBfactor(structure + " & i. " + residu, density)
        MVI.paintDensity(color_gradient, structure)
        return densityList
