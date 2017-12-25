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
from pymol import cmd as PymolCmd
from pymol.cgo import CYLINDER
from Application.Core.MolecularViewerInterfaces.atomList import PDBAtom
# import pickle


def getPDB(structure):
    """
    """
    currentPDB = list()
    list_atoms = PymolCmd.get_model(str(structure))
    # PDBList = list()

    for atom in list_atoms.atom:
        signature = atom.get_signature().split(":")
        currentPDB.append(PDBAtom(atom.chain, int(signature[3]), signature[5], tuple(atom.coord)))
        # PDBList.append(PDBAtom(atom.chain, int(signature[3]), signature[5], tuple(atom.coord)))


    # with open(structure+".pyn", 'w') as fout:
    #     pickle.dump(PDBList, fout)

    return currentPDB

def select(selectionName, selection):
    if selectionName == "":
        return PymolCmd.select(selection)
    else:
        return PymolCmd.select(selectionName, selection)

def alterBFactors(structure, bFactor):
    PymolCmd.alter(structure, "b=" + str(bFactor))

def spectrum(color_gradient, structure):
    PymolCmd.spectrum("b", color_gradient, structure)

def zoom(selection):
    PymolCmd.zoom(selection)

def drawConstraint(points, color, aRadius, IDNumber):
    """used to draw a NOE constraint between two sets of atoms
            using cgo from Pymol
    """
    cons = [CYLINDER] + list(points[0]) + list(points[1]) + [aRadius] + color
    PymolCmd.load_cgo(cons, IDNumber)

def delete(selectionName):
    PymolCmd.delete(selectionName)

def get_names():
    return PymolCmd.get_names()

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
