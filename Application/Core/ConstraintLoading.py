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

# DistanceConstraints loading functions
from sys import stderr
from ConstraintManager import imConstraintSetManager
import constraintParsers as CParsers


class ConstraintLoader(object):
    """Classes used to lad constraints from
    files and returns a constraintSetManager filled
    with constraints
    """
    def __init__(self, fileName, managerName):
        """
        """
        self.fileName = fileName
        self.managerName = managerName
        self.fileText = ""

    def loadConstraintsFromFile(self):
        """
        """
        self.constraintDefinition = self.loadFile()
        return self.loadConstraints()

    def loadConstraints(self):
        """Starts constraints loading, uses appropriate function
        depending on file type
        """
        aManager = imConstraintSetManager(self.managerName)

        if self.constraintDefinition in ('XPLOR', 'CNS'):
            aManager.format = "CNS"
            parser = CParsers.CNSParser(self.fileText)
        elif self.constraintDefinition in ('DYANA', 'CYANA'):
            aManager.format = "XEASY"
            parser = CParsers.CYANAParser(self.fileText)
        else:
            stderr.write("Incorrect or unsupported constraint type.\n")
        if parser is not None:
            aManager.fileText = self.fileText
            aManager.constraints = tuple(constraint for constraint in parser)

        return aManager

    def loadFile(self):
        """
        """

        with open(self.fileName, 'r') as file_in:
            self.fileText = file_in.read().upper()

        return CParsers.constraintParser.findConstraintType(self.fileText)
