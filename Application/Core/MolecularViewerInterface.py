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
import pickle
import os
from sys import stdout
from atomList import atomList, PDBAtom
from memoization import lru_cache
import errors

lastDigitsRE = re.compile(r'\d+\b')  # look for last digit of atom type (used in AtomSet)

currentPDB = atomList()

try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def setPDB(structure):
        """
        """
        list_atoms = PymolCmd.get_model(str(structure))
        currentPDB.clear()
        currentPDB.name = str(structure)
        # PDBList = list()

        for atom in list_atoms.atom:
            signature = atom.get_signature().split(":")
            currentPDB.append(PDBAtom(atom.chain, int(signature[3]), signature[5], tuple(atom.coord)))
            # PDBList.append(PDBAtom(atom.chain, int(signature[3]), signature[5], tuple(atom.coord)))


        # with open(structure+".pyn", 'w') as fout:
            # pickle.dump(PDBList, fout)
        get_coordinates.clear()

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


except ImportError:
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
        stdout.write("Zoom on " + selection+".\n")

    def delete(selectionName):
        stdout.write("Deleted "+selectionName+".\n")

    def get_names():
        return [fileName.split(".")[0] for fileName in os.listdir(os.getcwd()) if '.pyn' in fileName]

    def setPDB(structure):
        """
        """
        with open(structure + ".pyn", 'r') as fin:
            currentPDB.atoms = pickle.load(fin)
        get_coordinates.clear()


def zeroBFactors(structure):
    alterBFactors(structure, 0)


def setBfactor(structure, residu, bFactor):
    alterBFactors(structure + " & i. " + str(residu), bFactor)


def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)


@lru_cache(maxsize=2048) # It's probable than some atoms are used more often than others 
def get_coordinates(atomSet): # and there are typically thousans of atoms in structure
    """
    """
    if any(wildcard in atomSet.atoms for wildcard in "*+#%"):
        if atomSet.atoms[-1] is '*':
            try:
                selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('*', '')))
                return tuple(atom.coord for atom in selectedAtoms)
            except ValueError:
                errors.add_error_message("Ambiguous atoms not found in structure : " + str(atomSet) + ", please check nomenclature.")
                return tuple()
        if '+' in atomSet.atoms:
            try:
                complyingAtomsCoordinates = list()
                selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('+', '')))
                numberOfPlusMark = atomSet.atoms.count('+')
                for atom in selectedAtoms:
                    if len(*lastDigitsRE.findall(atom.name)) == numberOfPlusMark:
                        complyingAtomsCoordinates.append(atom.coord)
                return complyingAtomsCoordinates

            except ValueError:
                errors.add_error_message("Ambiguous atoms not found in structure : " + str(atomSet) + ", please check nomenclature.")
                return tuple()
        if '#' in atomSet.atoms:
            try:
                complyingAtomsCoordinates = list()
                nameRoot = atomSet.atoms.replace('#', '')
                selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot))
                for atom in selectedAtoms:
                    if len(*lastDigitsRE.findall(atom.name)) > 0:
                        complyingAtomsCoordinates.append(atom.coord)
                return complyingAtomsCoordinates
            except ValueError:
                errors.add_error_message("Ambiguous atoms not found in structure : " + str(atomSet) + ", please check nomenclature.")
                return tuple()
        if '%' in atomSet.atoms:
            try:
                complyingAtomsCoordinates = list()
                nameRoot = atomSet.atoms.replace('#', '')
                selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot))
                numberOfPercentMark = atomSet.atoms.count('%')
                for atom in selectedAtoms:
                    if len(atom.name.replace(nameRoot,'')) == numberOfPercentMark:
                        complyingAtomsCoordinates.append(atom.coord)
                return complyingAtomsCoordinates

            except ValueError:
                errors.add_error_message("Ambiguous atoms not found in structure : " + str(atomSet) + ", please check nomenclature.")
                return tuple()
    else:
        try:
            return currentPDB.coordinatesForAtom(atomSet)
        except ValueError:
            errors.add_error_message( "Atom not found in structure : " + str(atomSet) + ", please check nomenclature.")
            return tuple()


def createSelection(structure, Atoms):
    """
    """
    selection = structure + " and ("
    try:
        selection += " ".join("chain {} and resi {} and name {} +".format(currentPDB.segids[currentPDB.ConstraintsSegid.index(atom.segid)], atom.resi_number, atom.atoms) for atom in sorted(Atoms))
    except ValueError: # should be an absence of segid
        selection += " ".join("resi {} and name {} +".format(atom.resi_number, atom.atoms) for atom in sorted(Atoms))
    return selection.rstrip("+") + ")"

def getModelsNames(satisfactionMarker="", unSatisfactionMarker=""):
    """
    """
    objectsLists = get_names()
    return tuple(name for name in objectsLists if not (unSatisfactionMarker in name or satisfactionMarker in name))
