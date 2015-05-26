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

#Module for drawing constraints
from MolecularViewerInterface import setBfactor, drawConstraint, paintDensity, zeroBFactors

class ConstraintDrawer(object):
    """

    """
    def drC(self, selectedConstraint, radius, colors):
        """
        Draw an array of constraints according to the filter defined by user,
        using the drawConstraint function
        """    
        involvedResidueslist = []
        numberOfDrawnConstraints = 0
        for aConstraint in selectedConstraint:
            if not aConstraint.resis[0]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[0]['number'])
            if not aConstraint.resis[1]['number'] in involvedResidueslist:
                involvedResidueslist.append(aConstraint.resis[1]['number'])
            if aConstraint.violated == 'violated':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.violated == 'not violated':
                color = colors['notViolated']
            drawConstraint(aConstraint.points, color, radius, aConstraint.getID())
            numberOfDrawnConstraints = numberOfDrawnConstraints + 1
        return {'Residueslist':involvedResidueslist,
                'DrawnConstraints':numberOfDrawnConstraints}

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
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
