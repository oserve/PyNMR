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


class ConstraintSetManager(object):
    """Class to manage a set of constraints
    """
    def __init__(self, managerName):
        self.constraints = []
        self.residuesList = []
        self.pdb = ''
        self.name = managerName
        self.format = ""

    def __str__(self):
        return self.name + " contains " + str(len(self.constraints)) + " constraints.\n"

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    # Constraints management methods

    def setPDB(self, pdb):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.pdb = pdb
        if len(self.constraints):
            for constraint in self.constraints:
                constraint.pdbName = self.pdb

    def associateToPDB(self):
        """Invokes associatePDBAtoms function on all constraints
        """
        result = 0
        if self.pdb != '':
            if len(self.constraints):
                for constraint in self.constraints:
                    constraint.associatePDBAtoms(self.pdb)
                    result = 1
        return result

    def removeAllConstraints(self):
        """Empties an array of constraints
        """
        while len(self.constraints) > 0:
            for constraint in self.constraints:
                self.constraints.remove(constraint)

    def addConstraint(self, aConstraint):
        """Add a constraint to the constraint list of the manager and
        update the list of residues
        """
        self.constraints.append(aConstraint)
        aConstraint.setName(self.name)
        for resiNumber in aConstraint.getResisNumber():
            if resiNumber not in self.residuesList:
                self.residuesList.append(resiNumber)

    def removeConstraint(self, aConstraintNumber):
        """
        """
        if int(aConstraintNumber) <= len(self.constraints):
            del self.constraints[int(aConstraintNumber)]

