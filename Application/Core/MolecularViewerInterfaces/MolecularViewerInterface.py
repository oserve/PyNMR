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
from atomList import atomList, PDBAtom
from memoization import lru_cache
from .. import errors

lastDigitsRE = re.compile(r'\d+\b')  # look for last digit of atom type (used in AtomSet)

currentPDB = atomList()

try:
    import PymolInterface as Interface

except ImportError:
    import DebugMVI as Interface


def zeroBFactors(structure):
    Interface.alterBFactors(structure, 0)


def setBfactor(structure, atoms, bFactor):
    Interface.alterBFactors(createSelection(structure, atoms, residueLevel=True), bFactor)


def paintDensity(color_gradient, structure):
    Interface.spectrum(color_gradient, structure)


def setPDB(structure):
    currentPDB.clear()
    currentPDB.name = str(structure)

    currentPDB.atoms = Interface.getPDB(structure)

    get_coordinates.clear()

def select(selectionName, selection):
    return Interface.select(selectionName, selection)

def alterBFactors(structure, bFactor):
    Interface.alterBFactors(structure, bFactor)

def spectrum(color_gradient, structure):
    Interface.spectrum(color_gradient, structure)

def zoom(structure, selectedAtoms):
    selection = createSelection(structure, selectedAtoms)
    Interface.zoom(selection)
    Interface.delete('involvedRes')
    Interface.select('involvedRes', selection)

def drawConstraint(points, color, aRadius, IDNumber):
    """used to draw a NOE constraint between two sets of atoms
            using cgo from Pymol
    """
    Interface.drawConstraint(points, color, aRadius, IDNumber)

def delete(selectionName):
    Interface.delete(selectionName)

def get_names():
    return Interface.get_names()

@lru_cache(maxsize=2048) # It's probable than some atoms are used more often than others 
def get_coordinates(atomSet): # and there are typically thousands of atoms in structure
    """
    """
    complyingAtomsCoordinates = list()

    if any(wildcard in atomSet.atoms for wildcard in "*+#%"):
        if atomSet.atoms[-1] is '*':
            selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('*', '')))
            complyingAtomsCoordinates.extend(atom.coord for atom in selectedAtoms)
        if '+' in atomSet.atoms:
            selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('+', '')))
            numberOfPlusMark = atomSet.atoms.count('+')
            for atom in selectedAtoms:
                if len(*lastDigitsRE.findall(atom.name)) == numberOfPlusMark:
                    complyingAtomsCoordinates.append(atom.coord)
        if '#' in atomSet.atoms:
            nameRoot = atomSet.atoms.replace('#', '')
            for atom in currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot)):
                if len(*lastDigitsRE.findall(atom.name)) > 0:
                    complyingAtomsCoordinates.append(atom.coord)
        if '%' in atomSet.atoms:
            nameRoot = atomSet.atoms.replace('%', '')
            numberOfPercentMark = atomSet.atoms.count('%')
            for atom in currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot)):
                if len(atom.name.replace(nameRoot,'')) == numberOfPercentMark:
                    complyingAtomsCoordinates.append(atom.coord)
    else:
        complyingAtomsCoordinates = currentPDB.coordinatesForAtom(atomSet)

    if len(complyingAtomsCoordinates) == 0:
        errors.add_error_message( "Atom not found in structure : " + str(atomSet) + ", please check nomenclature.")

    return tuple(complyingAtomsCoordinates)

def createSelection(structure, Atoms, residueLevel=False):
    """
    """
    unAmbiguousAtomsList = list()
    for atomSet in Atoms:
        if any(wildcard in atomSet.atoms for wildcard in "*+#%"):
            if atomSet.atoms[-1] is '*':
                unAmbiguousAtomsList.extend(currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('*', ''))))
            if '+' in atomSet.atoms:
                selectedAtoms = currentPDB.atomsLikeAtom(atomSet._replace(atoms=atomSet.atoms.replace('+', '')))
                numberOfPlusMark = atomSet.atoms.count('+')
                for atom in selectedAtoms:
                    if len(*lastDigitsRE.findall(atom.name)) == numberOfPlusMark:
                        unAmbiguousAtomsList.append(atom)
            if '#' in atomSet.atoms:
                nameRoot = atomSet.atoms.replace('#', '')
                for atom in currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot)):
                    if len(*lastDigitsRE.findall(atom.name)) > 0:
                        unAmbiguousAtomsList.append(atom)
            if '%' in atomSet.atoms:
                nameRoot = atomSet.atoms.replace('%', '')
                numberOfPercentMark = atomSet.atoms.count('%')
                for atom in currentPDB.atomsLikeAtom(atomSet._replace(atoms=nameRoot)):
                    if len(atom.name.replace(nameRoot,'')) == numberOfPercentMark:
                        unAmbiguousAtomsList.append(atom)
        else:
            unAmbiguousAtomsList.append(PDBAtom(*currentPDB.checkSegid(atomSet), coord=[0,0,0]))

    return Interface.selectionFormat(currentPDB, unAmbiguousAtomsList, structure, residueLevel=unAmbiguousAtomsList[0].name=="")

def getModelsNames(satisfactionMarker="", unSatisfactionMarker=""):
    """
    """
    objectsLists = get_names()
    return tuple(name for name in objectsLists if not (unSatisfactionMarker in name or satisfactionMarker in name))
