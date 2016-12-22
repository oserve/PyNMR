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

import errors
import MolecularViewerInterface as MVI
from Geom import set_method


class ConstraintFilter(object):
    """

    """

    def __init__(self, structure, residuesList, dist_range, violationState,
                 violCutoff, method, RangeCutOff):
        """Defines parameters for filtering the constraints
        """
        self.residuesList = residuesList
        self.range = dist_range
        self.violationState = violationState
        self.cutOff = violCutoff
        self.structure = structure
        self.method = method
        self.rangeCutOff = RangeCutOff
        MVI.setPDB(self.structure)
        set_method(self.method)

    def filterAConstraint(self, aConstraint):
        """Filter the constraints to be drawn.
        """
        if aConstraint.getRange(self.rangeCutOff) in self.range:
            if any(aResiNumber in self.residuesList for aResiNumber in aConstraint.ResiNumbers):
                if aConstraint.isValid():
                    if aConstraint.setValueFromStructure():
                        aConstraint.setViolationState(self.cutOff)
                        if aConstraint.isSatisfied() in self.violationState:
                            return True
                    else:
                        errors.add_error_message("Distance issue with constraint :\n" + aConstraint.definition)
                else:
                    errors.add_error_message("Selection issue with constraint :\n" + aConstraint.definition)
        return False

    def constraints(self, constraintList):
        for aConstraint in constraintList:
            if self.filterAConstraint(aConstraint):
                yield aConstraint
            else:
                pass
