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
from sys import stdout
import os
import pickle


def select(selectionName, selection):
    stdout.write("Selected " + selection + " with name " + selectionName + ".\n")
    return tuple()

def alterBFactors(structure, bFactor):
    stdout.write("Set BFactor " + str(bFactor) + " to " + structure + ".\n")

def spectrum(color_gradient, structure):
    stdout.write("Applied gradient " + color_gradient + " on structure " + structure + ".\n")

def drawConstraint(points, color, aRadius, ID):
    stdout.write("Drawn " + ID + " between points " + str(points) + " with " + str(color) + " color and radius " + str(aRadius) +"\n")

def zoom(selection):
    stdout.write("Zoom on " + selection + ".\n")

def delete(selectionName):
    stdout.write("Deleted " + selectionName + ".\n")

def get_names():
    return [fileName.split(".")[0] for fileName in os.listdir(os.getcwd()) if '.pyn' in fileName]

def getPDB(structure):
    """
    """
    with open(structure + ".pyn", 'r') as fin:
        atoms = pickle.load(fin)

    return atoms

def selectionFormat(currentPDB, unAmbiguousAtomsList, structure, residueLevel):
    selection = ""
    for molChain in currentPDB.segids:
        resiList = [atom for atom in unAmbiguousAtomsList if atom.segid == molChain or atom.segid == '']
        if resiList:
            selection += structure + " and (chain " + molChain + " and ("
            if not residueLevel:
                selection += " ".join("resi {} and name {} +".format(atom.resi_number, atom.name) for atom in resiList)
            else:
                selection += " ".join("resi {} +".format(atom.resi_number) for atom in resiList)
            selection = selection.rstrip("+ ")
            selection += ")) + " 
    return selection.rstrip("+ ) ") + "))"
