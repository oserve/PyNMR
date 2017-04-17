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
from .. import errors
from Constraint import Constraint
from ..Geom import centerOfMass, calcDistance
from .. import MolecularViewerInterface as MVI


class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        """
        """
        super(NOE, self).__init__()
        self.points = tuple()
        self.numberOfAtomsSets = 2
        self.type = "NOE"

    def getRange(self, RangeCutOff):
        """Return the range name,
        range depends on the number of residus between the atomsets
        """
        if self.atoms[0].segid == self.atoms[1].segid:
            resi_diff = abs(int(self.atoms[0].resi_number) - int(self.atoms[1].resi_number))
            if resi_diff == 0:
                return 'intra'
            elif resi_diff == 1:
                return 'sequential'
            elif RangeCutOff >= resi_diff > 1:
                return 'medium'
            else:
                return 'long'
        else:
            return 'long'

    def setValueFromStructure(self):
        """Set actual distance of the constraint in the current structure file
        """
        try:
            coordinates = tuple(MVI.get_coordinates(atom) for atom in self.atoms)
            self.points = tuple(centerOfMass(coordinate) for coordinate in coordinates)
            self.constraintValues['actual'] = calcDistance(*coordinates)
        except (ZeroDivisionError, TypeError):
            errors.add_error_message("Issue with constraint :\n" + self.definition)
