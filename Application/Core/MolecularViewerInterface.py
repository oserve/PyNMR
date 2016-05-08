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
import re

lastDigit = re.compile(r'\d(\b|\Z)')  # look for last digit of atom type (used in AtomSet)

try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def select(selectionName, selection):
        if selectionName == "":
            return PymolCmd.select(selection)
        else:
            return PymolCmd.select(selectionName, selection)

    def get_model(model):
        return PymolCmd.get_model(model)

    def alterBFactors(structure, bFactor):
        PymolCmd.alter(structure, "b=" + str(bFactor))

    def spectrum(color_gradient, structure):
        PymolCmd.spectrum("b", color_gradient, structure)

    def zoom(selection):
        PymolCmd.zoom(selection)

    def drawConstraint(points, color, aRadius, ID):
        """used to draw a NOE constraint between two sets of atoms
                using cgo from Pymol
        """
        cons = [CYLINDER] + list(points[0]) + list(points[1]) + [aRadius] + color
        PymolCmd.load_cgo(cons, ID)

    def delete(selectionName):
        PymolCmd.delete(selectionName)

    def createSelection(Items):
        selection = ""
        if len(Items) > 2:
            selection = Items.pop(0) + " &"
            for residue in Items:
                selection += " resi " + residue + " +"
        return selection.rstrip("+")

    def get_names():
        return PymolCmd.get_names()

    def getID(atomSet):
        """return ID of the atom for selection
            by Pymol functions. Form : structure & i. Number & n. atomType
        """
        selection = atomSet.structure + " & i. " + str(atomSet.number) + " & n. " + str(atomSet.atType)
        if atomSet.segid != "":
            selection = selection + " & c. " + atomSet.segid
        if not select("", selection):  # often due to different format (e.g. : HB2 -> 2HB)
            if atomSet.atType == 'HN':
                atomSet.atType = 'H'
            elif atomSet.atType == 'H':
                atomSet.atType = 'HN'
            elif lastDigit.search(atomSet.atType):
                digit = lastDigit.search(atomSet.atType).group()[0]
                atomSet.atType = digit + lastDigit.sub('', atomSet.atType)  # put final digit at the beginning
            atomSet.atType = '*' + atomSet.atType
            selection = atomSet.structure + " & i. " + str(atomSet.number) + " & n. " + str(atomSet.atType)
            if atomSet.segid != "":
                selection = selection + " & c. " + atomSet.segid
            if not select("", selection):
                selection = "noID"
        return selection


except ImportError:
    def select(selectionName, selection):
        return []

    def get_model(model):
        return []

    def alterBFactors(structure, bFactor):
        pass

    def spectrum(color_gradient, structure):
        pass

    def drawConstraint(points, color, aRadius, ID):
        pass

    def zoom(selection):
        pass

    def delete(selectionName):
        pass

    def createSelection(Items):
        if len(Items) > 2:
            selection = Items.pop(0) + " &"
            for residue in Items:
                selection += " resi " + residue + " +"
        return selection.rstrip("+")

    def get_names():
        return []

    def getID(atomSet):
        return ""


def zeroBFactors(structure):
    alterBFactors(structure, 0)


def setBfactor(selection, bFactor):
    alterBFactors(selection, bFactor)


def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)
