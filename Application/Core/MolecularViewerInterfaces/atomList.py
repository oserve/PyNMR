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
from collections import namedtuple, MutableSequence
from sys import stderr

from Application.Core.MolecularViewerInterfaces.memoization import lru_cache

PDBAtom = namedtuple("PDBAtom", ['segid', 'resi_number', 'name', 'coord'])


class atomList(MutableSequence): # used as singleton
    """
    """
    def __init__(self, name=""):
        """
        """
        self.name = name
        self.atoms = list()
        self.ConstraintsSegid = list()
        self.segidList = list()
        self.segidSet = False

    def __setitem__(self, index, anAtom):
        if isinstance(anAtom, PDBAtom):
            self.atoms[index] = anAtom
            self.segidSet = False
        else:
            raise TypeError(str(anAtom) + " is not atom.\n")    

    def __delitem__(self, index):
        del self.atoms[index]

    def insert(self, index, anAtom):
        self.atoms.insert(index, anAtom)

    def clear(self):
        """
        """
        del self.atoms[:]
        self.name = ""

    def __len__(self):
        """
        """
        return len(self.atoms)

    def __getitem__(self, index):
        """
        """
        try:
            return self.atoms[index]
        except IndexError:
            raise IndexError("No atom at index " + str(index) + ".\n")

    @lru_cache(maxsize=10) # Most expensive loop with lowest probability of changes
    def atomsForSegid(self, aSegid=None):
        """
        """
        selectedAtoms = atomList(self.name)
        if aSegid is not None and len(aSegid) > 0:
            if aSegid in self.segids:
                selectedAtoms.atoms = [atom for atom in self.atoms if atom.segid == aSegid]
            else:
                if aSegid in self.ConstraintsSegid:
                    newSegid = self.segids[self.ConstraintsSegid.index(aSegid)]
                else:
                    self.ConstraintsSegid.append(aSegid)
                    newSegid = self.segids[self.ConstraintsSegid.index(aSegid)]
                selectedAtoms.atoms = [atom for atom in self.atoms if atom.segid == newSegid]
            return selectedAtoms
        else:
            return self

    def checkSegid(self, anAtom):
        """
        """
        if anAtom.segid is not None and len(anAtom.segid) > 0:
            if not anAtom.segid in self.segids:
                if anAtom.segid in self.ConstraintsSegid:
                    newSegid = self.segids[self.ConstraintsSegid.index(anAtom.segid)]
                else:
                    self.ConstraintsSegid.append(anAtom.segid)
                    newSegid = self.segids[self.ConstraintsSegid.index(anAtom.segid)]
            return anAtom._replace(segid=newSegid)
        return anAtom

    def atomsForResidueNumber(self, aNumber=None):
        """
        """
        selectedAtoms = atomList(self.name)
        if aNumber is not None or "":
            selectedAtoms.atoms = [atom for atom in self.atoms if atom.resi_number == aNumber]
            return selectedAtoms
        else:
            return self

    def atomsForAtomName(self, aName=None):
        """
        """
        selectedAtoms = atomList(self.name)
        if aName is not None or "":
            selectedAtoms.atoms = [atom for atom in self.atoms if atom.name == aName]
            return selectedAtoms
        else:
            return self

    def coordinatesForAtom(self, anAtom):
        """
        """
        try:
            selectedSeg = self.atomsForSegid(anAtom.segid)
            selectedResi = selectedSeg.atomsForResidueNumber(anAtom.resi_number)
            selectedAtom = selectedResi.atomsForAtomName(anAtom.atoms)
        except AttributeError:
            stderr.write(str(anAtom) + " is not an atom.\n")

        return tuple(atom.coord for atom in selectedAtom)

    def atomsLikeAtom(self, anAtom):
        """
        """
        try:
            selectedSeg = self.atomsForSegid(anAtom.segid)
            selectedResi = selectedSeg.atomsForResidueNumber(anAtom.resi_number)
            selectedAtoms = atomList(self.name)
            selectedAtoms.atoms = [atom for atom in selectedResi if anAtom.atoms in atom.name]
            return selectedAtoms
        except AttributeError:
            stderr.write(str(anAtom) + " is not an atom.\n")

    @property
    def segids(self):
        """
        """
        if self.segidSet is False: # Expensive, and mostly useless, to calculate it everytime
            for atom in self.atoms:
                if atom.segid not in self.segidList:
                    self.segidList.append(atom.segid)
            self.segidSet = True
        return self.segidList

