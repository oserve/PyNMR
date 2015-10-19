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
from sys import stderr


class ConstraintFilter(object):
    """

    """

    def __init__(self, pdb, residuesList, dist_range, violationState,
                 violCutoff, method, RangeCutOff):
        """Defines parameters for filtering the constraints
        """
        self.parameters = {}
        self.parameters['residuesList'] = residuesList
        self.parameters['range'] = dist_range
        self.parameters['violationState'] = violationState
        self.parameters['cutOff'] = violCutoff
        self.parameters['pdb'] = pdb
        self.parameters['method'] = method
        self.parameters['rangeCutOff'] = RangeCutOff

    def filter(self, aConstraint):
        """Filter the constraints to be drawn (there should be a better
        way to implement it)
        """
        if aConstraint.getRange(self.parameters['rangeCutOff']) in self.parameters['range']:
            inList = 0
            for aNumber in aConstraint.getResisNumber():
                if aNumber in self.parameters['residuesList']:
                    inList = 1
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
                        stderr.write("Distance issue with constraint :\n"
                                     + aConstraint.definition + "\n")
                        return 0
                else:
                    stderr.write("Selection issue with constraint :\n"
                                 + aConstraint.definition + "\n")
                    return 0
            else:
                return 0
        else:
            return 0

    def filterConstraints(self, constraintList):
        """
        """
        selectedConstraint = []
        for aConstraint in constraintList:
            if self.filter(aConstraint):
                selectedConstraint.append(aConstraint)
        return selectedConstraint
