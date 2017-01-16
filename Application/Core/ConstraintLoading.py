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


def loadConstraintsFromFile(fileName, managerName):
    """Starts constraints loading, uses appropriate function
    depending on file type
    """
    aManager = imConstraintSetManager(managerName)

    with open(fileName, 'r') as file_in:
        fileText = file_in.read().upper()

        constraintDefinition = CParsers.constraintParser.findConstraintType(fileText)

        if constraintDefinition in ('XPLOR', 'CNS'):
            aManager.format = "CNS"
            parser = CParsers.CNSParser(fileText)
        elif constraintDefinition in ('DYANA', 'CYANA'):
            aManager.format = "XEASY"
            parser = CParsers.CYANAParser(fileText)
        else:
            stderr.write("Incorrect or unsupported constraint type.\n")
        if parser is not None:
            aManager.fileText = fileText
            aManager.constraints = tuple(constraint for constraint in parser)

        return aManager
