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
import errors

lastDigit = re.compile(r'\d(\b|\Z)')  # look for last digit of atom type (used in AtomSet)

pdb = {}

try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def setPDB(structure):
        """
        """
        list_atoms = PymolCmd.get_model(str(structure))
        pdb.clear()
        pdb['name'] = str(structure)

        for atom in list_atoms.atom:
            signature = atom.get_signature().split(":")
            pdb.setdefault(signature[3], []).append({'name': signature[5],
                                                     'coord': atom.coord,
                                                     'segi': atom.chain})

        #with open(structure+".pyn", 'w') as fout:
        #    pickle.dump(pdb, fout)

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

    def get_names():
        return PymolCmd.get_names()


except ImportError:
    def select(selectionName, selection):
        return tuple()

    def get_model(model):
        return tuple()

    def alterBFactors(structure, bFactor):
        pass

    def spectrum(color_gradient, structure):
        pass

    def drawConstraint(points, color, aRadius, ID):
        stdout.write("Drawn " + ID + " between points " + str(points) + " with " + str(color) + " color and radius " + str(aRadius) +"\n")

    def zoom(selection):
        pass

    def delete(selectionName):
        pass

    def get_names():
        return [fileName.split(".")[0] for fileName in os.listdir(os.getcwd()) if '.pyn' in fileName]

    def getID(atomSet):
        return ""

    def setPDB(structure):
        """
        """
        with open(structure + ".pyn", 'r') as fin:
            pdb.update(pickle.load(fin))


def zeroBFactors(structure):
    alterBFactors(structure, 0)


def setBfactor(structure, residu, bFactor):
    alterBFactors(structure + " & i. " + residu, bFactor)


def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)


def checkID(atomSet):
    """
    """
    check = False
    newName = ""
    error_message = ""
    if str(atomSet.resi_number) in pdb:
        if atomSet.segid in (atom['segi'] for atom in pdb[str(atomSet.resi_number)]):
            if atomSet.atoms in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                check = True
            else:
                if '*' not in atomSet.atoms:
                    if atomSet.atoms == 'HN':
                        newName = 'H'
                    elif atomSet.atoms == 'H':
                        newName = 'HN'
                    elif lastDigit.search(atomSet.atoms):
                        digit = lastDigit.search(atomSet.atoms).group()[0]
                        newName = digit + lastDigit.sub('', atomSet.atoms)  # put final digit at the beginning
                    if newName in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                        check = True
                    else:
                        error_message = "Atom name not found"
                else:
                    nameRoot = atomSet.atoms.replace('*', '')
                    for aName in (atom['name'] for atom in pdb[str(atomSet.resi_number)]):
                        if nameRoot in aName:
                            check = True
                            break
                    if check is False:
                        error_message = "Atom name not found"
        else:
            error_message = "Wrong segment / chain"
    else:
        error_message = "Residue number not found"
    if check is False:
        errors.add_error_message("Can't find " + str(atomSet.atoms) + " in structure " + pdb['name'] + " because : " + error_message)
    if newName:
        return {'valid': check, 'NewData': {'atoms': newName}}
    else:
        return {'valid': check, 'NewData': None}


def get_coordinates(atomSet):
    """
    """
    coordinates = list()
    if '*' in atomSet.atoms:
        nameRoot = atomSet.atoms.replace('*', '')
        for atom in pdb[str(atomSet.resi_number)]:
            if atomSet.segid == atom['segi']:
                if nameRoot in atom['name']:
                    coordinates.append(atom['coord'])
    else:
        for atom in pdb[str(atomSet.resi_number)]:
            if atomSet.segid == atom['segi']:
                if atomSet.atoms == atom['name']:
                    coordinates = [atom['coord']]
                    break
    return coordinates

def createSelection(structure, Atoms):
    """
    """
    selection = structure + " and ("
    selection += " ".join("chain {} and resi {} and name {} +".format(atom.segid, atom.resi_number, atom.atoms) for atom in sorted(Atoms))
    return selection.rstrip("+") + ")"

def getModelsNames(satisfactionMarker="", unSatisfactionMarker=""):
    """
    """
    objectsLists = get_names()
    return tuple(name for name in objectsLists if not (name.find(unSatisfactionMarker) >= 0 or name.find(satisfactionMarker) >= 0))
