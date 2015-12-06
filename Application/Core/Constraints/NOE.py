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
from Constraint import Constraint
from ..Geom import centerOfMass, calcDistance


class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        """
        """
        super(NOE, self).__init__()
        self.points = {}
        self.numberOfAtomsSets = 2
        self.type = "NOE"

    def setViolationState(self, cutOff):
        """Set violation state, with optional additional cutoff
        """
        if self.constraintValues['actual'] <= (self.constraintValues['constraint'] - self.constraintValues['min'] - cutOff):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooClose'
        elif self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + cutOff):
            self.satisfaction = 'unSatisfied'
            self.constraintValues['closeness'] = 'tooFar'
        else:
            self.satisfaction = 'Satisfied'

    def getRange(self, RangeCutOff):
        """Return the range name, according to the usual NMR specification
        range depends on the number of residus between the atomsets
        """
        if not int(self.resis[0]['number']) - int(self.resis[1]['number']):
            return 'intra'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) == 1:
            return 'sequential'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) > 1 and abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) <= RangeCutOff:
            return 'medium'
        elif abs(int(self.resis[0]['number']) - int(self.resis[1]['number'])) > RangeCutOff:
            return 'long'
        else:
            stderr.write('How come ?\n')

    def setDistance(self, method):
        """Set actual distance of the constraint in the current structure file
        """
        self.points[0] = centerOfMass(self.atoms[0].getID())
        self.points[1] = centerOfMass(self.atoms[1].getID())
        self.constraintValues['actual'] = calcDistance(self.atoms[0].getID(), self.atoms[1].getID(), method)
        if self.constraintValues['actual'] <= 0:
            return False
        else:
            return True

    def getResisNumber(self):
        """Utility method
        """
        return [self.resis[0]['number'], self.resis[1]['number']]
