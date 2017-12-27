import collections
import functools
import gzip
import os
import os.path as path
import pickle
import re
import shutil
import sys
import tempfile
import tkColorChooser
import tkFileDialog
import Tkinter as Tk
import tkSimpleDialog
import ttk
import urllib2
from collections import (Counter, Iterable, Mapping, MutableMapping,
                         OrderedDict, Sequence, defaultdict, namedtuple)
from contextlib import contextmanager
from heapq import nsmallest
from itertools import ifilterfalse, izip, product
from math import fsum, sqrt
from operator import itemgetter, mul, sub
from os import remove
from os.path import basename, exists
from sys import stderr, stdout

from pymol import cmd as PymolCmd
from pymol.cgo import CYLINDER
from pymol.cmd import extend

"""Main module declaring the module for pymol
contains interface for command line functions :
load CNS or DYANA distances constraints files
into molecular viewer, display them on the molecule
and show unSatisfied constraints according to a cutOff
with different color (White for not unSatisfied, blue for
lower limit violation, red for upper limit violation for NOEs)
"""

"""lru_cache() implementation for python 2.X
   by R. Hettinger (found on ActiveState Recipes)
"""

class RHCounter(dict):
    'Mapping where default values are zero'
    def __missing__(self, key):
        return 0

def lru_cache(maxsize=100):
    '''Least-recently-used cache decorator.

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    '''
    maxqueue = maxsize * 10
    def decorating_function(user_function, len=len, iter=iter,
                            tuple=tuple, sorted=sorted, KeyError=KeyError):
        cache = {}                  # mapping of args to results
        queue = collections.deque() # order that keys have been used
        refcount = RHCounter()        # times each key is in the queue
        sentinel = object()         # marker for looping around the queue
        kwd_mark = object()         # separate positional and keyword args

        # lookup optimizations (ugly but fast)
        queue_append, queue_popleft = queue.append, queue.popleft
        queue_appendleft, queue_pop = queue.appendleft, queue.pop

        @functools.wraps(user_function)
        def wrapper(*args, **kwds):
            # cache key records both positional and keyword args
            key = args
            if kwds:
                key += (kwd_mark,) + tuple(sorted(kwds.items()))

            # record recent use of this key
            queue_append(key)
            refcount[key] += 1

            # get cache entry or compute if not found
            try:
                result = cache[key]
                wrapper.hits += 1
            except KeyError:
                result = user_function(*args, **kwds)
                cache[key] = result
                wrapper.misses += 1

                # purge least recently used cache entry
                if len(cache) > maxsize:
                    key = queue_popleft()
                    refcount[key] -= 1
                    while refcount[key]:
                        key = queue_popleft()
                        refcount[key] -= 1
                    del cache[key], refcount[key]

            # periodically compact the queue by eliminating duplicate keys
            # while preserving order of most recent access
            if len(queue) > maxqueue:
                refcount.clear()
                queue_appendleft(sentinel)
                for key in ifilterfalse(refcount.__contains__,
                                        iter(queue_pop, sentinel)):
                    queue_appendleft(key)
                    refcount[key] = 1


            return result

        def clear():
            cache.clear()
            queue.clear()
            refcount.clear()
            wrapper.hits = wrapper.misses = 0

        wrapper.hits = wrapper.misses = 0
        wrapper.clear = clear
        return wrapper
    return decorating_function

"""scrolledlist.py: A Tkinter widget combining a Listbox with Scrollbar(s).

  For details, see:
    http://www.nmt.edu/tcc/help/lang/python/examples/scrolledlist/
"""


DEFAULT_WIDTH = "20"
DEFAULT_HEIGHT = "10"


class ScrolledList(ttk.Frame):
    """A compound widget containing a listbox and up to two scrollbars.

      State/invariants:
        .listbox:      [ The Listbox widget ]
        .vScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .hScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .callback:     [ as passed to constructor ]
        .vscroll:      [ as passed to constructor ]
        .hscroll:      [ as passed to constructor ]
    """

    def __init__(self, master=None, width=DEFAULT_WIDTH,
                 height=DEFAULT_HEIGHT, vscroll=1, hscroll=0, callback=None,
                 listvariable=None, selectmode=Tk.BROWSE):
        """Constructor for ScrolledList.
        """
        # -- 1 --
        # [ self  :=  a new Frame widget child of master ]
        ttk.Frame.__init__(self, master)
        # -- 2 --
        self.width = width
        self.height = height
        self.vscroll = vscroll
        self.hscroll = hscroll
        self.callback = callback
        # -- 3 --
        # [ self  :=  self with all widgets created and registered ]
        self.__createWidgets(listvariable, selectmode)

    def __createWidgets(self, alistvariable, aselectmode):
        """Lay out internal widgets.
        """
        # -- 1 --
        # [ if self.vscroll ->
        #     self  :=  self with a vertical Scrollbar widget added
        #     self.vScrollbar  :=  that widget ]
        #   else -> I ]
        if self.vscroll:
            self.vScrollbar = ttk.Scrollbar(self, orient=Tk.VERTICAL)
            self.vScrollbar.grid(row=0, column=1, sticky=Tk.N+Tk.S)
        # -- 2 --
        # [ if self.hscroll ->
        #     self  :=  self with a horizontal Scrollbar widget added
        #     self.hScrollbar  :=  that widget
        #   else -> I ]
        if self.hscroll:
            self.hScrollbar = ttk.Scrollbar(self, orient=Tk.HORIZONTAL)
            self.hScrollbar.grid(row=1, column=0, sticky=Tk.E+Tk.W)
        # -- 3 --
        # [ self  :=  self with a Listbox widget added
        #   self.listbox  :=  that widget ]
        self.listbox = Tk.Listbox(self, relief=Tk.SUNKEN,
                                  width=self.width, height=self.height,
                                  borderwidth=2, listvariable=alistvariable,
                                  selectmode=aselectmode)
        self.listbox.grid(row=0, column=0)
        self.listbox.configure(exportselection=False)
        # -- 4 --
        # [ if self.vscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.vScrollbar can reposition it ]
        #     self.vScrollbar  :=  self.vScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.vscroll:
            self.listbox["yscrollcommand"] = self.vScrollbar.set
            self.vScrollbar["command"] = self.listbox.yview

        # -- 5 --
        # [ if self.hscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.hScrollbar can reposition it ]
        #     self.hScrollbar  :=  self.hScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.hscroll:
            self.listbox["xscrollcommand"] = self.hScrollbar.set
            self.hScrollbar["command"] = self.listbox.xview
        # -- 6 --
        # [ self.listbox  :=  self.listbox with an event handler
        #       for button-1 clicks that causes self.callback
        #       to be called if there is one ]
        self.listbox.bind("<Button-1>", self.__clickHandler)

    def __clickHandler(self, event):
        """Called when the user clicks on a line in the listbox.
        """
        # -- 1 --
        if not self.callback:
            return
        # -- 2 --
        # [ call self.callback(c) where c is the line index
        #   corresponding to event.y ]
        lineNo = self.listbox.nearest(event.y)
        self.callback(lineNo)
        # -- 3 --
        self.listbox.focus_set()

    def count(self):
        """Return the number of lines in use in the listbox.
        """
        return self.listbox.size()

    def __getitem__(self, k):
        """Get the (k)th line from the listbox.
        """

        # -- 1 --
        if 0 <= k < self.count():
            return self.listbox.get(k)
        else:
            raise IndexError("ScrolledList[%d] out of range." % k)

    def get(self, index):
        """
        """
        return self.listbox.get(index)

    def append(self, text):
        """Append a line to the listbox.
        """
        self.listbox.insert(Tk.END, text)

    def insert(self, linex, text):
        """Insert a line between two existing lines.
        """

        # -- 1 --
        if 0 <= linex < self.count():
            where = linex
        else:
            where = Tk.END

        # -- 2 --
        self.listbox.insert(where, text)

    def delete(self, linex):
        """Delete a line from the listbox.
        """
        if 0 <= linex < self.count():
            self.listbox.delete(linex)

    def clear(self):
        """Remove all lines.
        """
        self.listbox.delete(0, Tk.END)

    def curselection(self):
        """
        """
        return self.listbox.curselection()

    def bind(self, sequence=None, func=None, add=None):
        """
        """
        self.listbox.bind(sequence, func, add)

    def selection_set(self, first, last=None):
        """
        """
        return self.listbox.selection_set(first, last)

    def selection_clear(self, first, last=None):
        """
        """
        self.listbox.selection_clear(first, last)

    def size(self):
        """
        """
        return self.listbox.size()

    def event_generate(self, event):
        """
        """
        self.listbox.event_generate(event)

    def selectmode(self, newMode):
        """
        """
        self.listbox.configure(selectmode=newMode)

    @property
    def exportselection(self):
        """Utility method to set constraint name
        """
        return self.listbox.exportselection

    @exportselection.setter
    def exportselection(self, exportSetting):
        """Utility method to set constraint name
        """
        self.listbox.exportselection = exportSetting

# From Tom Hennigan

def notify_delegates(method):
    """Decorator to call delegate methods. When decorating a method it will
    call `on_before_method_name` and `on_after_method_name`.

    Delegate methods are called before and after the actual method is called.
    On the after method the return value from the method is passed in as the
    `ret_value` keyword arg."""

    method_name = method.__name__

    # Figure out delegate method names.
    before_method = 'on_before_' + method_name
    exception_method = 'on_exception_in_' + method_name
    after_method = 'on_after_' + method_name

    def wrapper(self, *args, **kwargs):
        delegates = self.get_delegates_for_method(method_name)

        # Call the before methods.
        for delegate in delegates:
            if hasattr(delegate, before_method):
                getattr(delegate, before_method)(*args, **kwargs)

        try:
            return_value = method(self, *args, **kwargs)
        except Exception, e:
            kwargs['exception'] = e

            for delegate in delegates:
                if hasattr(delegate, exception_method):
                    getattr(delegate, exception_method)(*args, **kwargs)

            # Raise the exception.
            raise e

        # Call the after methods.
        kwargs['ret_value'] = return_value

        for delegate in delegates:
            if hasattr(delegate, after_method):
                getattr(delegate, after_method)(*args, **kwargs)

        return return_value

    return wrapper

class DelegateProviderMixin(object):
    """Mixin for a class that has delegates. Any method can be wrapped for
    delegates using the `@notify_delegates` decorator."""

    __delegates = []

    def add_delegate(self, delegate):
        """Adds a delegate specifically listening on all delegate methods it
        can respond to."""

        self.__delegates.append((delegate, None))

    def add_delegate_for_method(self, delegate, method):
        """Adds a delegate specifically listening on a certain method."""

        self.__delegates.append((delegate, [method]))

    def add_delegate_for_methods(self, delegate, methods):
        """Adds a delegate specifically listening on certain methods."""

        self.__delegates.append((delegate, methods))

    def remove_delegate(self, delegate):
        """Removes all hooks for the given delegate on the current object."""

        to_remove = []
        for index, (delegate_test, _methods) in enumerate(self.__delegates):
            if delegate == delegate_test:
                to_remove.append(index)

        for index in to_remove:
            del self.__delegates[index]

    def get_delegates_for_method(self, method):
        """Returns all delegates that are subscribed to all methods or to just
        the specific method. Delegates are returned in insertion order and only
        appear once regardless of how many times they have been added to this
        object."""

        delegates = []
        for delegate, delegate_methods in self.__delegates:
            if not delegate_methods or method in delegate_methods:
                if not delegate in delegates:
                    delegates.append(delegate)
        return delegates


class NMRApplication(object):
    """
    """
    def __init__(self, Core, app="NoGUI"):
        """
        """
        self.NMRCommands = Core
        self.log = ""
        self.NMRCLI = NMRCLI(Core)
        if app == "NoGUI":
            stdout.write("Starting PyNMR CLI ...\n")
        else:
            stdout.write("Starting PyNMR GUI ...\n")
            self.startGUI()

    def startGUI(self):
        """
        """
        self.NMRInterface = NMRGUI()
        self.NMRInterface.startGUI()
        self.GUIBindings()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.NMRInterface.preferencesPanel.setDefaults()
        self.NMRInterface.mainPanel.constraintPanel.setDefaults()
        self.NMRInterface.mainPanel.fileSelection.updateFilelist()

    def GUIBindings(self):
        """
        """
        self.NMRInterface.mainPanel.fileSelection.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.NOEDrawing.NMRCommands = self.NMRCommands
        self.NMRInterface.mainPanel.constraintPanel.structureManagement.mainApp = self
        self.NMRInterface.preferencesPanel.mainApp = self


regInput = re.compile(r'[^0-9+\-\,\s]')

class NMRCLI(object):
    """
    """

    def __init__(self, Core):
        """
        """
        self.Core = Core
        self.dataControllers = dict()

    def showNOE(self, structure, managerName, residuesList, dist_range,
                violationState, violCutoff, method, radius, colors,
                rangeCutOff, UnSatisfactionMarker, SatisfactionMarker):
        """Command to display NMR restraints as sticks on protein structure with
        different parameters : filtering according to distance, restraints display
        options
        """
        if structure != '':
            if managerName == '' and len(self.Core) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.keys()[0]
                if managerName in self.Core:
                    dist_range, violationState, residuesList = interpretCLI(dist_range, violationState, residuesList)
                    self.Core.commandsInterpretation(managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showSticks(managerName, structure, colors, radius,
                                         UnSatisfactionMarker, SatisfactionMarker)

                    self.dataControllers[managerName] = NOEDataController(self.Core.drawer.displayedConstraintsSticks.intersection(self.Core.get(managerName, "").constraintsManagerForDataType('NOE')), managerName, structure)
                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].residuesList])) +
                                 " residues involved.\n")

                else:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def LoadConstraints(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        if exists(filename):
            self.Core.LoadConstraints(filename)
            stdout.write(str(len(self.Core[basename(filename)])) + " constraints loaded.\n")

        else:
            stderr.write("File : " + filename + " has not been found.\n")

    def showNOEDensity(self, structure, managerName, residuesList, dist_range,
                       violationState, violCutoff, rangeCutOff, method, colors):
        """Command to display NMR restraints as color map on protein structure with
        different parameters : filtering according to distance, restraints display
        options
        """
        if structure != '':
            if managerName == '' and len(self.Core) == 0:
                stderr.write("No constraints loaded.\n")
            else:
                if managerName == '':
                    managerName = self.Core.keys()[0]
                try:
                    dist_range, violationState, residuesList = interpretCLI(dist_range, violationState, residuesList)

                    self.Core.commandsInterpretation(managerName, residuesList,
                                                     dist_range, violationState, violCutoff,
                                                     method, rangeCutOff)
                    self.Core.showNOEDensity(managerName, structure, colors)
                    self.dataControllers[managerName] = NOEDataController(self.Core.drawer.displayedConstraintsDensity.intersection(self.Core.get(managerName, "").constraintsManagerForDataType('NOE')), managerName, structure)

                    stdout.write(str(len(self.dataControllers[managerName])) +
                                 " constraints used.\n")
                    stdout.write(str(len([residue for residue in self.dataControllers[managerName].residuesList])) +
                                 " residues involved.\n")
                except ValueError:
                    stderr.write("Please check constraints filename.\n")
        else:
            stderr.write("Please enter a structure name.\n")

    def loadAndShow(self, filename, structure, residuesList, dist_range,
                    violationState, violCutoff, method, rangeCutOff,
                    radius, colors, UnSatisfactionMarker, SatisfactionMarker):
        """Combine two previous defined functions : load and display"""
        self.LoadConstraints(filename)
        self.showNOE(structure, basename(filename), residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker)

    def downloadNMR(self, pdbCode, url):
        """
        """
        self.Core.downloadFromPDB(pdbCode, url)

    def cleanScreen(self, filename):
        """Call the command to clear the screen from all NMR
        restraints
        """
        if filename in self.Core:
            self.Core.cleanScreen(filename)
            del self.dataControllers[filename]

def interpretCLI(dist_range, violationState, residuesList):
    """
    """
    resList = set()
    if not regInput.findall(residuesList):
        for resi_range in residuesList.split("+"):
            aRange = resi_range.split("-")
            if 1 <= len(aRange) <= 2:
                resList.update(str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[-1]) + 1))
            else:
                stderr.write("Residues set definition error : " + residuesList + "\n")
    if dist_range == 'all':
        dist_range = ('intra', 'sequential', 'medium', 'long')
    else:
        dist_range = tuple(dist_range)

    if violationState == 'all':
        violationState = ('unSatisfied', 'Satisfied')
    else:
        violationState = tuple(violationState)

    return (dist_range, violationState, resList)


def loadConstraintsFromFile(fileName, managerName):
    """Starts constraints loading, uses appropriate function
    depending on file type
    """
    aManager = imConstraintSetManager(managerName)

    with open(fileName, 'r') as file_in:
        fileText = file_in.read().upper()

        constraintDefinition = BaseConstraintParser.findConstraintType(fileText)

        if constraintDefinition in ('XPLOR', 'CNS'):
            aManager.format = "CNS"
            parser = CNSParser(fileText)
        elif constraintDefinition in ('DYANA', 'CYANA'):
            aManager.format = "XEASY"
            parser = CYANAParser(fileText)
        else:
            stderr.write("Incorrect or unsupported constraint type : " + constraintDefinition + ".\n")
        if parser is not None:
            aManager.fileText = fileText
            aManager.constraints = tuple(constraint for constraint in parser)

        return aManager


class imConstraintSetManager(Sequence):
    """Class to manage an immutable set of constraints
    """

    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self, managerName):
        self.constraints = tuple()
        self.name = managerName

    def __str__(self):
        return "\n".join(str(constraint) for constraint in self)

    def __len__(self):
        return len(self.constraints)

    __repr__ = __str__

    def __getitem__(self, constraintIndex):
        if 0 <= constraintIndex < len(self.constraints):
            self.constraints[constraintIndex].id['number'] = constraintIndex
            return self.constraints[constraintIndex]
        else:
            raise IndexError("No constraint at index " + str(constraintIndex) + ".\n")

    # Constraints management methods

    def setPDB(self, structure):
        """Sets the name of the structure (usually a PDB File) on which the
        distance should be calculated
        """
        self.structure = structure
        for constraint in self.constraints:
            constraint.structureName = self.structure

    def associateToPDB(self):
        """read strutural data
        """
        if self.structure != '':
            setPDB(self.structure)
            return len(self.constraints) > 0
        return False

    def constraintsManagerForDataType(self, dataType):
        """
        """
        newManager = imConstraintSetManager(self.name + str(dataType))
        newManager.constraints = tuple(constraint for constraint in self.constraints if constraint.type == dataType)
        return newManager

    def constraintsManagerForAtoms(self, atomDefinitions):
        """
        """
        newManager = imConstraintSetManager(self.name + " for atoms " + str(atomDefinitions))
        newConstraints = set()
        for constraint in self.constraints:
            for atom in constraint.atoms:
                if atom in atomDefinitions:
                    newConstraints.add(constraint)
        newManager.constraints = tuple(newConstraints)
        return newManager

    @property
    def residuesList(self):
        """
        """
        resis = set()
        for constraint in self.constraints:
            resis.update(constraint.ResiNumbers)
        return resis

    def intersection(self, anotherManager):
        """
        """
        newManager = imConstraintSetManager("")
        if isinstance(anotherManager, imConstraintSetManager):
            newManager.constraints = tuple(set(self.constraints) & set(anotherManager.constraints))
            newManager.name = self.name + anotherManager.name
        else:
            raise TypeError(str(anotherManager) + " is not a " + str(type(self)) + "\n")
        return newManager

    @property
    def atomsList(self):
        """
        """
        atomList = set()
        for constraint in self.constraints:
            atomList.update(constraint.atoms)
        return atomList

    def setPartnerAtoms(self, AtomSelection):
        """
        """
        self.partnerManager = self.constraintsManagerForAtoms(AtomSelection)

    def areAtomsPartner(self, anAtom):
        """
        """
        return anAtom in self.partnerManager.atomsList


class ConstraintSetManager(imConstraintSetManager):
    """Class to manage a mutable set of constraints
    Usable as an iterator
    """

    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self, managerName):
        super(ConstraintSetManager, self).__init__(managerName)
        self.constraints = list()
        self.structure = ""
        self.format = ""
        self.fileText = ""

    # Constraints management methods

    def removeAllConstraints(self):
        """Empties an array of constraints
        """
        del self.constraints[:]

    def append(self, aConstraint):
        """Add a constraint to the constraint list of the manager and
        update the list of residues
        """
        aConstraint.id['number'] = len(self)
        self.constraints.append(aConstraint)
        if aConstraint.name == "":
            aConstraint.name = self.name

    def extend(self, constraints):
        """
        """
        for constraint in constraints:
            self.append(constraint)

    def removeConstraint(self, aConstraint):
        """
        """
        try:
            self.constraints.remove(aConstraint)
        except ValueError:
            stderr.write("Constraint " + str(aConstraint) +" is unknown\n")

    def removeConstraints(self, Constraints):
        """
        """
        for Constraint in Constraints:
            self.removeConstraint(Constraint)

"""Module for drawing constraints
"""


class ConstraintDrawer(object):
    """

    """
    def __init__(self, UnSatisfactionMarker="", SatisfactionMarker=""):
        """
        """
        self.UnSatisfactionMarker = UnSatisfactionMarker
        self.SatisfactionMarker = SatisfactionMarker
        self.displayedConstraintsSticks = ConstraintSetManager("")
        self.displayedConstraintsDensity = ConstraintSetManager("")

    def drC(self, selectedConstraints, radius, colors):
        """
        Draw an array of constraints according to the filter defined by user,
        using the drawConstraint function
        """
        tempList = list()
        for number, aConstraint in enumerate(selectedConstraints):
            if len(self.displayedConstraintsSticks) > number:
                try:
                    deleteSelection(self.IDConstraint(aConstraint))
                    self.displayedConstraintsSticks.removeConstraint(aConstraint)
                except ValueError:
                    pass
            if aConstraint.satisfaction() is 'unSatisfied':
                color = colors[aConstraint.constraintValues['closeness']]
            elif aConstraint.satisfaction() is 'Satisfied':
                color = colors['Satisfied']
            self.displayedConstraintsSticks.append(aConstraint)
            tempList.append(tuple([aConstraint.points, color, radius, self.IDConstraint(aConstraint)]))
        # do not merge previous and next loops ! It creates a thread race which severly slows down the display in pymol
        for aConstraint in tempList:
            drawConstraint(*aConstraint)

        return self.displayedConstraintsSticks.atomsList

    def constraintsDensity(self, selectedConstraints):
        """Calculate number of constraints per residue for selected constraints
        by the filter
        """
        densityList = list()

        tempList = list()
        for number, aConstraint in enumerate(selectedConstraints):
            if len(self.displayedConstraintsDensity) > number:
                try:
                    self.displayedConstraintsDensity.removeConstraint(aConstraint)
                    deleteSelection(self.IDConstraint(aConstraint))
                except ValueError:
                    pass
            tempList.append(aConstraint)
        # do not merge previous and next loops ! It creates a thread race which severly slows down the display in pymol
        for aConstraint in tempList:
            densityList.extend(atom._replace(atoms="") for atom in aConstraint.atoms)
            self.displayedConstraintsDensity.append(aConstraint)

        return densityList

    def paD(self, selectedConstraints, structure, color_gradient):
        """Uses b-factors to simulate constraint density on structure
        """
        densityList = self.constraintsDensity(selectedConstraints)
        bFactors = Counter(densityList)
        zeroBFactors(structure)
        for atom, density in Counter(atom._replace(atoms="") for atom in densityList).iteritems():
            setBfactor(structure, [atom], density)
        paintDensity(color_gradient, structure)
        return bFactors.keys()

    def IDConstraint(self, aConstraint):
        """Returns name of constraints :
        Name_(constraint number)_(structureName)_(violation_state)
        """
        if aConstraint.satisfaction() is 'Satisfied':
            marker = self.SatisfactionMarker
        elif aConstraint.satisfaction() is 'unSatisfied':
            marker = self.UnSatisfactionMarker
        else:
            marker = ""

        return aConstraint.name + str(aConstraint.id['number']) + marker + aConstraint.structureName


"""Module for error logging
"""


error_messages = list()


def add_error_message(message):
    """
    """
    error_messages.append(str(message))


def get_error_messages():
    """
    """
    for message in error_messages:
        yield message

def erase_all_error_messages():
    """
    """
    del error_messages[:]

@contextmanager
def errorLog():
    """
    """
    try:
        yield None
    finally:
        sys.stderr.write("\n".join(get_error_messages()) + '\n')
        erase_all_error_messages()


def NOEFilter(residuesList, dist_range, violationState, violCutoff, method, RangeCutOff):
    """
    """
    calcDistance.method = method
    def constraintFilter(aConstraint):
        """
        """
        if aConstraint.getRange(RangeCutOff) in dist_range:
            if any(str(aResiNumber) in residuesList for aResiNumber in aConstraint.ResiNumbers):
                return aConstraint.satisfaction(violCutoff) in violationState
        return False

    return constraintFilter


def centerOfMass(coords):
    """ Adapted from : Andreas Henschel 2006
    assumes equal weights for atoms (usually protons)
    """

    try:
        sumCoords = (fsum(coord) for coord in izip(*coords))
        numCoords = len(coords)
        return tuple(coord/numCoords for coord in sumCoords)
    except ValueError:
        return (0, 0, 0)


def calcDistance(*coords):
    """    Calculate distance according to :
    ((sum of all distances^-6)/number of distances)^-1/6
    or (sum of all distances^-6)^-1/6

    calcDistance.method should be set before use
    """
    result = None

    try:
        distance_list = (sqrt(fsum(sub(*coord) ** 2 for coord in izip(*atoms))) for atoms in product(*coords))
        sum6 = fsum(pow(distance, -6) for distance in distance_list)
        if calcDistance.method == 'ave6':
            number_of_distances = reduce(mul, (len(coord) for coord in coords))
        elif calcDistance.method == 'sum6':
            number_of_distances = 1
        result = pow(sum6/number_of_distances, -1./6)
    except(ValueError, TypeError):
        add_error_message("Problem using coordinates : " +
                                 str(coords) + "\n" +
                                 " and distances list : " +
                                 str([distance for distance in distance_list]) + "\n")
    except AttributeError:
        sys.stderr.write("Please set calcDistance.method before using calcDistance()\n")

    return result


class NMRCore(MutableMapping):
    """Low Level Interface Class
    for loading and displaying constraints
    """
    def __init__(self):
        self.ManagersList = dict()
        self.constraintFilter = None
        self.drawer = ConstraintDrawer()

    def __getitem__(self, key):
        """Return a constraint Manager
        """
        try:
            return self.ManagersList[key]
        except ValueError:
            stderr.write("No constraintManager named " + str(key) + "\n")

    def __setitem__(self, key, item):
        self.ManagersList[key] = item

    def __delitem__(self, key):
        try:
            del self.ManagersList[key]
        except ValueError:
            stderr.write("No constraintManager named " + str(key) + "\n")

    def __iter__(self):
        return self.ManagersList.__iter__()

    def __len__(self):
        return len(self.ManagersList)

    def get(self, key, default=None):
        """
        """
        try:
            return self.ManagersList[key]
        except ValueError:
            return default

    def keys(self):
        """
        """
        return self.ManagersList.keys()

    def LoadConstraints(self, filename):
        """load NMR distance constraints, call for the correct file format
        (CNS/CYANA),
        """
        managerName = path.basename(filename)
        self[managerName] = loadConstraintsFromFile(filename, managerName)

    def showSticks(self, managerName, structure, colors, radius,
                   UnSatisfactionMarker, SatisfactionMarker):
        """Display distance constraints as sticks between groups of atoms.
        """
        self.drawer.UnSatisfactionMarker, self.drawer.SatisfactionMarker = UnSatisfactionMarker, SatisfactionMarker
        self.showConstraints(managerName, structure, colors=colors, radius=radius, displayFunction=self.drawer.drC)

    def showNOEDensity(self, managerName, structure, gradient):
        """Display number of constraints per residue as a simulated density
        which is then paint on the model according to a color gradient
        """
        self.showConstraints(managerName, structure, gradient=gradient, displayFunction=self.drawer.paD)

    def showConstraints(self, managerName, structure, displayFunction=None, colors=None,
                        radius=None, gradient=None):
        """Seeks for constraints that fit criteria and call the appropriate display function.
        """
        with errorLog():
            self[managerName].setPDB(structure)
            try:
                if self[managerName].associateToPDB():
                    selectedConstraints = (aConstraint for aConstraint in self[managerName] if self.constraintFilter(aConstraint))
                    if colors:
                        selectedAtoms = displayFunction(selectedConstraints,
                                                        radius, colors)
                    if gradient:
                        selectedAtoms = displayFunction(selectedConstraints,
                                                        self[managerName].structure,
                                                        gradient)
                    if selectedAtoms:
                        zoom(self[managerName].structure, selectedAtoms)
                else:
                    add_error_message("No structure selected.")
            except ValueError:
                add_error_message("No constraints to draw ! You might want to load a few of them first ...")

    def commandsInterpretation(self, managerName, residuesList, dist_range, violationState,
                               violCutoff, method, rangeCutOff):
        """Setup Filter for constraints
        """
        if not residuesList:
            residuesList = set(str(aResidueNumber) for aResidueNumber in self[managerName].residuesList)
        self.constraintFilter = NOEFilter(residuesList, dist_range, violationState,
                                          violCutoff, method, rangeCutOff)

    def cleanScreen(self):
        """Remove all sticks
        """
        for aConstraint in self.drawer.displayedConstraintsSticks:
            deleteSelection(self.drawer.IDConstraint(aConstraint))
        self.drawer.displayedConstraintsSticks.removeAllConstraints()

    def saveConstraintsFile(self, aManagerName, fileName):
        """Save the selected constraint file under the format
        it has been loaded.
        """
        with open(fileName, 'w') as fout:
            fout.write(self[aManagerName].fileText)

    def downloadFromPDB(self, pdbCode, url):
        """Download constraint file from wwwPDB
        if available.
        """
        PDBConstraintsFileName = pdbCode.lower() + ".mr"
        zippedFileName = PDBConstraintsFileName + ".gz"
        workdir = os.getcwd()
        tempDownloadDir = tempfile.mkdtemp()
        os.chdir(tempDownloadDir)
        try:
            restraintFileRequest = urllib2.urlopen(urllib2.Request(url+zippedFileName))
            localFile = open(zippedFileName, 'wb')
            shutil.copyfileobj(restraintFileRequest, localFile)
            localFile.close()
            restraintFileRequest.close()
            with gzip.open(zippedFileName, 'rb') as zippedFile:
                decodedFile = zippedFile.read()
                with open(PDBConstraintsFileName, 'w') as restraintFile:
                    restraintFile.write(decodedFile)
            if path.exists(zippedFileName):
                os.remove(zippedFileName)
                self.LoadConstraints(PDBConstraintsFileName)
                os.remove(PDBConstraintsFileName)
                os.chdir(workdir)
                os.removedirs(tempDownloadDir)
        except IOError:
            sys.stderr.write("Error while downloading or opening " +
                             pdbCode + " NMR Restraints file from PDB.\n")

    def getModelsNames(self, satisfactionMarker="", unSatisfactionMarker=""):
        return getModelsNames(satisfactionMarker, unSatisfactionMarker)


Atoms = namedtuple("Atoms", ['segid', 'resi_number', 'atoms'])


class BaseConstraintParser(Iterable):
    """
    """

    XEASYReg = re.compile(r'\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\w+\s+\d+')
    AtTypeReg = re.compile(r'[CHON][A-Z]*')
    atoms = defaultdict(lambda: Atoms)

    def __init__(self, text):
        """
        """
        self.text = (aLine.strip() for aLine in text.split('\n'))
        self.inFileTab = list()
        self.segments = list()

    def __iter__(self):
        self.prepareFile()
        for parsingResult in self.parseConstraints():
            if parsingResult is not None:
                if len(parsingResult["residues"]) == 2:  # 2 residues (matches also H-Bonds)
                    if any(residue['name'] == "O" for residue in parsingResult["residues"]): # filters H-Bonds
                        stderr.write("Unsupported constraint type : " + parsingResult["definition"] + "\n")
                    else:
                        aConstraint = NOE()
                        # No other constraint type supported ... for now !
                        aConstraint.definition = parsingResult["definition"]
                        aConstraint.atoms = BaseConstraintParser.parseAtoms(parsingResult["residues"])
                        aConstraint.setConstraintValues(parsingResult["values"][0],
                                                        parsingResult["values"][1],
                                                        parsingResult["values"][2])
                        yield aConstraint
                else:
                    stderr.write("Unsupported constraint type :" + parsingResult["definition"] + "\n")
            else:
                stderr.write("Error while loading : " + parsingResult["definition"] + "\n")

    def prepareFile(self):
        """
        """
        raise NotImplementedError

    def parseConstraints(self):
        """Should return an iterator
        """
        raise NotImplementedError

    @staticmethod
    def findConstraintType(fileText):
        """
        """
        if "ASSI" in fileText:
            typeDefinition = 'CNS'
        elif BaseConstraintParser.XEASYReg.search(fileText):
            typeDefinition = 'CYANA'
        else:
            typeDefinition = None
        return typeDefinition

    @staticmethod
    def parseAtoms(parsingResult):
        """
        """
        atomList = list()
        for aResult in parsingResult:
            currentResidue = dict()
            if "resid" in aResult:
                currentResidue["resi_number"] = int(aResult["resid"])
            else:
                currentResidue["resi_number"] = int(aResult["resi"])
            currentResidue["atoms"] = aResult["name"]
            currentResidue["segid"] = aResult.get("segid", 'A')
            residueKey = ''.join(str(value) for value in currentResidue.values()) 
            atomList.append(BaseConstraintParser.atoms[residueKey](**currentResidue))
        return atomList


SegResiReg = re.compile(r"(SEGI\w*\s+[\w\d]+\s+AND\s+)?(RESI\w*\s+\d+\s+AND\s+NAME\s+\w\w?\d*[\*#\+%]*)")
RegFloat = re.compile(r'\s+[-+]?[0-9]*\.?[0-9]+'*3)


class CNSParser(BaseConstraintParser):
    """
    """
    def __init__(self, text):
        """
        """
        self.validConstraints = list()
        BaseConstraintParser.__init__(self, text)

    def prepareFile(self):
        """
        """
        for txt in self.text:
            if '!' in txt:
                exclamIndex = txt.find('!')
                stderr.write('Comment excluded : ' + txt[exclamIndex:-1] + "\n")
                txt = txt[0:exclamIndex].replace('!', '')
                if txt == '':
                    continue
            if 'OR ' in txt:
                self.inFileTab[-1] = self.inFileTab[-1] + txt
                continue
            self.inFileTab.append(txt)

        del self.validConstraints[:]

        for line in (aline.replace('"', ' ') for aline in self.inFileTab):
            if "ASSI" in line:
                line = line.replace("GN", "")
                self.validConstraints.append(line.replace("ASSI", ""))
            elif SegResiReg.search(line) is not None:
                self.validConstraints[-1] = self.validConstraints[-1] + line
        self.validConstraints = (constraint for constraint in self.validConstraints if re.search(r'\d', constraint))

    def parseConstraints(self):
        """Split CNS/XPLOR type constraint into a dictionnary, containing the name of
        the residues (as arrays), and the values of the parameter associated to
        the constraint. It should be independant from the type of constraint
        (dihedral, distance, ...)
        """
        for aCNSConstraint in self.validConstraints:
            try:
                residuesList = SegResiReg.finditer(aCNSConstraint, re.IGNORECASE)

                constraintParsingResult = dict()
                residues = list()
                for aResidue in residuesList:
                    residueParsingResult = dict()
                    try:
                        segid = aResidue.group(1).split()[1]
                    except AttributeError:
                        segid = ''
                    residueParsingResult["segid"] = segid

                    for aDefinition in aResidue.group(2).split(" AND "):
                        definitionArray = aDefinition.split()
                        residueParsingResult[definitionArray[0].strip().lower()] = definitionArray[1].strip()

                    residues.append(residueParsingResult)
                constraintParsingResult["residues"] = residues

                if 'OR ' in aCNSConstraint: # only for NOE
                    constraintParsingResult["residues"] = constraintAmbiguity(constraintParsingResult["residues"])

                constraintParsingResult["values"] = constraintValues(aCNSConstraint)
                constraintParsingResult["definition"] = aCNSConstraint

            except ZeroDivisionError:
                stderr.write('Can not parse : ' + aCNSConstraint + '\n')
                constraintParsingResult = None
            yield constraintParsingResult


def constraintAmbiguity(constraintResidues):
    """
    """
    sortedResidues = [[constraintResidues[0]], []]
    for residue in constraintResidues[1:]:
        if residuesLooksLike(constraintResidues[0], residue):
            sortedResidues[0].append(residue)
        else:
            sortedResidues[1].append(residue)

    results = []
    for resiList in sortedResidues:
        names = [residue['name'] for residue in resiList]
        ambiguousResidue = resiList[0]
        if len(set(names)) != 1:
            ambiguousResidue = resiList[0]
            for index, letters in enumerate(izip(*names)):
                if len(set(letters)) != 1:
                    ambiguousResidue['name'] = resiList[0]['name'][:index] + "*"
                    break       
        results.append(ambiguousResidue)
    return results

def constraintValues(aCNSConstraint):
    """
    """
    constraintValues = RegFloat.findall(aCNSConstraint)
    if constraintValues:
        constraintValuesList = constraintValues[0].split()
    else:
        constraintValuesList = tuple()
    return tuple(float(aValue) for aValue in constraintValuesList)

def residuesLooksLike(residueA, residueB):
    if residueA.get("segid", "A") == residueA.get("segid", "A"):
        if residueA["resid"] == residueB["resid"]:
            if len(residueA["name"]) > 1:
                if len(residueA["name"]) == len(residueB["name"]):
                    return residueA["name"][0:-1] == residueB["name"][0:-1]
    return False


class CYANAParser(BaseConstraintParser):
    """
    """
    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def prepareFile(self):
        """
        """
        self.inFileTab = self.text

    def parseConstraints(self):
        """
        """
        for aConstraintLine in self.inFileTab:
            if len(aConstraintLine) > 1 and aConstraintLine.find('#') == 0:
                stderr.write(aConstraintLine + " skipped. Commented out.\n")
                parsed = None
            cons_tab = aConstraintLine.split()
            try:
                parsed = {"residues":
                    [{'resid': int(cons_tab[0]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[2])).group()},
                    {'resid': int(cons_tab[3]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[5])).group()}]}
                parsed["values"] = ([str(1.8 + (float(cons_tab[6]) - 1.8)/2), '1.8', cons_tab[6]])
                parsed["definition"] = aConstraintLine
            except:
                stderr.write("Unknown error while loading constraint " + ":\n" +
                             aConstraintLine + "\n")
                parsed = None
            yield parsed

    @staticmethod
    def convertTypeDyana(atType):
        """
        Adapt xeasy nomenclature Q to pymol *
        """
        if 'Q' in atType:
            newType = atType.replace('Q', 'H', 1) + ('*')
            # Q is replaced by H and a star at the end of the atom type
            # avoid QQ (QQD-> HD*)
            return newType.replace('Q', '')
        else:
            return atType


class Constraint(object):
    """
    Abstract Constraint Class
    Contains informations about constraints
    atoms, model value, theoretical value,
    constraint number, constraint name
    and methods that allows to get these informations
    or to determine if the constraints is unSatisfied or not
    """

    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def __init__(self):
        """
        """
        self.id = dict()
        self.cutOff = 0
        self.definition = ''
        self.atoms = list()
        self.constraintValues = dict()
        self.numberOfAtomsSets = 0
        self.structureName = ""
        self.type = ""

    def __str__(self):
        """
        """
        return self.definition

    __repr__ = __str__

    def __eq__(self, anotherConstraint):
        """
        """
        return isinstance(anotherConstraint, self.__class__) and all(AAtom == SAtom for AAtom, SAtom in izip(anotherConstraint.atoms, self.atoms)) # assume sorted

    @property
    def name(self):
        """Utility method to get constraint name
        """
        return self.id.get('name', "")

    @name.setter
    def name(self, aName):
        """Utility method to set constraint name
        """
        self.id['name'] = aName

    def setConstraintValues(self, constraintValue, Vmin, Vplus):
        """
        Set constraints values for violations
        determination
        """
        self.constraintValues['constraint'] = float(constraintValue)
        self.constraintValues['min'] = float(Vmin)
        self.constraintValues['plus'] = float(Vplus)

    def setValueFromStructure(self):
        """
        """
        raise NotImplementedError

    @property
    def ResiNumbers(self):
        """Utility method
        """
        return (atom.resi_number for atom in self.atoms)

    def satisfaction(self, cutOff=-1):
        """Set violation state, with optional additional cutoff
        """
        if cutOff >= 0:
            self.cutOff = cutOff
        self.setValueFromStructure()
        try:
            if self.constraintValues['actual'] <= (self.constraintValues['constraint'] - self.constraintValues['min'] - self.cutOff):
                self.constraintValues['closeness'] = 'tooClose'
                return 'unSatisfied'
            elif self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + self.cutOff):
                self.constraintValues['closeness'] = 'tooFar'
                return 'unSatisfied'
            else:
                return 'Satisfied'
        except KeyError:
            return None


class NOE(Constraint):
    """
    NOE inherits from Constraint
    Contains additional methods specific to NOE constraint
    """

    def __init__(self):
        """
        """
        super(NOE, self).__init__()
        self.points = tuple()
        self.numberOfAtomsSets = 2
        self.type = "NOE"

    def getRange(self, RangeCutOff):
        """Return the range name,
        range depends on the number of residus between the atomsets
        """
        if self.atoms[0].segid == self.atoms[1].segid:
            resi_diff = abs(int(self.atoms[0].resi_number) - int(self.atoms[1].resi_number))
            if resi_diff == 0:
                return 'intra'
            elif resi_diff == 1:
                return 'sequential'
            elif RangeCutOff >= resi_diff > 1:
                return 'medium'
            else:
                return 'long'
        else:
            return 'long'

    def setValueFromStructure(self):
        """Set actual distance of the constraint in the current structure file
        """
        try:
            coordinates = tuple(get_coordinates(atom) for atom in self.atoms)
            self.points = tuple(centerOfMass(coordinate) for coordinate in coordinates)
            self.constraintValues['actual'] = calcDistance(*coordinates)
        except (ZeroDivisionError, TypeError):
            add_error_message("Issue with constraint :\n" + self.definition)


PDBAtom = namedtuple("PDBAtom", ['segid', 'resi_number', 'name', 'coord'])


class atomList(object): # used as singleton
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

    def append(self, anAtom):
        """
        """
        if isinstance(anAtom, PDBAtom):
            self.atoms.append(anAtom)
            self.segidSet = False
        else:
            raise TypeError(str(anAtom) + " is not atom.\n")

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
        if 0 <= index < len(self.atoms):
            return self.atoms[index]
        else:
            raise IndexError("No atom at index " + str(index) + ".\n")

    def __iter__(self):
        return self.atoms.__iter__()

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

lastDigitsRE = re.compile(r'\d+\b')  # look for last digit of atom type (used in AtomSet)

currentPDB = atomList()

def setPDB(structure):
    currentPDB.clear()
    currentPDB.name = str(structure)

    currentPDB.atoms = getPDB(structure)

    get_coordinates.clear()

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

    if not complyingAtomsCoordinates:
        add_error_message( "Atom not found in structure : " + str(atomSet) + ", please check nomenclature.")

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

    return selectionFormat(currentPDB, unAmbiguousAtomsList, structure, residueLevel=unAmbiguousAtomsList[0].name=="")

def getModelsNames(satisfactionMarker="", unSatisfactionMarker=""):
    """
    """
    objectsLists = get_names()
    return tuple(name for name in objectsLists if not (unSatisfactionMarker in name or satisfactionMarker in name))


def getPDB(structure):
    """
    """
    currentPDB = list()
    list_atoms = PymolCmd.get_model(str(structure))

    for atom in list_atoms.atom:
        signature = atom.get_signature().split(":")
        currentPDB.append(PDBAtom(atom.chain, int(signature[3]), signature[5], tuple(atom.coord)))

    return currentPDB

def select(selectionName, selection):
    if selectionName == "":
        return PymolCmd.select(selection)
    else:
        return PymolCmd.select(selectionName, selection)

def zeroBFactors(structure):
    alterBFactors(structure, 0)

def setBfactor(structure, atoms, bFactor):
    alterBFactors(createSelection(structure, atoms, residueLevel=True), bFactor)

def paintDensity(color_gradient, structure):
    spectrum(color_gradient, structure)

def alterBFactors(structure, bFactor):
    PymolCmd.alter(structure, "b=" + str(bFactor))

def spectrum(color_gradient, structure):
    PymolCmd.spectrum("b", color_gradient, structure)

def zoom(structure, selectedAtoms):
    selection = createSelection(structure, selectedAtoms)
    PymolCmd.zoom(selection)
    deleteSelection('involvedRes')
    select('involvedRes', selection)

def drawConstraint(points, color, aRadius, IDNumber):
    """used to draw a NOE constraint between two sets of atoms
            using cgo from Pymol
    """
    cons = [CYLINDER] + list(points[0]) + list(points[1]) + [aRadius] + color
    PymolCmd.load_cgo(cons, IDNumber)

def deleteSelection(selectionName):
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



class atomTypeListController(Mapping):
    """
    """

    def __init__(self):
        """
        """
        Mapping.__init__(self)
        self.atomTypes = defaultdict(list)

    def __getitem__(self, key):
        """
        """
        return self.atomTypes[key]

    def __iter__(self):
        """
        """
        return sorted(self.atomTypes.keys()).__iter__()

    def __len__(self):
        """
        """
        return len(self.atomTypes)

    def clear(self):
        """
        """
        self.atomTypes.clear()

    def addAtom(self, atom):
        """
        """
        self.atomTypes[atom.atoms].append(atom)


class resiNumberListController(Mapping):
    """
    """

    def __init__(self):
        """
        """
        Mapping.__init__(self)
        self.resiNumbers = defaultdict(list)

    def __getitem__(self, key):
        """
        """
        return self.resiNumbers[key]

    def __iter__(self):
        """
        """
        return sorted(self.resiNumbers.keys(), key=lambda x: int(x.split('\\')[0])).__iter__()

    def __len__(self):
        """
        """
        return len(self.resiNumbers)

    def clear(self):
        """
        """
        self.resiNumbers.clear()

    def addAtom(self, atom):
        """
        """
        self.resiNumbers["{}\ ({})".format(atom.resi_number, atom.segid)].append(atom)



class NOEDataController(object):
    """
    """

    def __init__(self, dataSource, aManagerName, structure):
        """
        """
        self.structure = structure
        self.name = aManagerName
        self.dataType = 'NOE'
        self.selectedAtoms = list()
        self.manager = dataSource

    def __len__(self):
        """
        """
        return len(self.manager)

    @property
    def residuesList(self):
        """
        """
        return (str(residue) for residue in sorted(self.manager.residuesList, key=int))

    def setSelectedAtoms(self, aSelection):
        """
        """
        self.selectedAtoms = aSelection
        self.manager.setPartnerAtoms(aSelection)

    @property
    def displayedAtoms(self):
        """
        """
        return sorted(self.manager.atomsList)

    @property
    def partnerAtoms(self):
        """
        """
        partners = set()
        if self.selectedAtoms:
            for anAtom in self.selectedAtoms:
                self.manager.setPartnerAtoms([anAtom])
                partners.update(atom for atom in self.manager.atomsList if self.manager.areAtomsPartner(atom) and atom != anAtom)
            return sorted(partners)
        else:
            raise UnboundLocalError("Partner list not registered.\n")

    def constraintsForAtoms(self, atomsList):
        """
        """
        if len(atomsList) == 2:
            consManager = self.manager.constraintsManagerForAtoms([atomsList[0]]).intersection(self.manager.constraintsManagerForAtoms([atomsList[1]]))
            return consManager.constraints
        else:
            raise ValueError("There should be 2 items in the list, " + str(len(atomsList)) + " found.\n")

    def constraintValueForAtoms(self, atomsList):
        """
        """
        return [(constraint.constraintValues, constraint.satisfaction()) for constraint in self.constraintsForAtoms(atomsList)]



class NMRGUI(Tk.Toplevel):
    """
    """
    def __init__(self):
        """
        """
        Tk.Toplevel.__init__(self)
        self.title('PymolNMR')
        self.resizable(width=False, height=False)
        self.noteBook = ttk.Notebook(self)
        self.mainPanel = mainPanel(self.noteBook)
        self.preferencesPanel = PreferencesPanel(self.noteBook)
        self.About = About(self.noteBook)
        self.panelsList = list()

    def createPanels(self):
        """Main Frames (not IBM ;-)
        """

        self.noteBook.grid(row=0, column=0)

        self.noteBook.add(self.mainPanel, text="Main")
        self.panelsList.append(self.mainPanel)

        self.panelsList.append(self.preferencesPanel)
        self.noteBook.add(self.preferencesPanel, text="Preferences")

        self.noteBook.add(self.About, text="Help")

    def startGUI(self):
        """
        """
        self.createPanels()
        self.setDelegations()

    def setDelegations(self):
        """
        """
        self.mainPanel.NOEDrawing.mainGUI = self
        self.preferencesPanel.mainGUI = self
        self.mainPanel.fileSelection.mainGUI = self

    def getInfo(self):
        """
        """
        infos = dict()
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


class DependantColumnsTableView(ttk.Frame, DelegateProviderMixin):
    """
    """
    def __init__(self, masterView=None, NumberOfResiLists=1, dataSource = None):
        """
        """
        ttk.Frame.__init__(self, class_='DependantColumnsTableView', master=masterView)
        self.dataSource = dataSource
        self.TkVars = tuple(Tk.StringVar() for number in xrange(NumberOfResiLists * 2))
        self.listTitleLabels = tuple(ttk.Label(self) for number in xrange(NumberOfResiLists * 2))

        self.scrolledLists = list()
        for index, aVar in enumerate(self.TkVars):
            aList = ScrolledList(self, listvariable=aVar, width=10)
            if index % 2 == 0:
                aList.selectmode(Tk.EXTENDED)
            aList.bind('<<ListboxSelect>>', self.updateDisplay)
            self.scrolledLists.append(aList)

        self.selectedList = None
        self.selectedRows = None

    def grid(self, *args, **kwargs):
        """
        """
        super(DependantColumnsTableView, self).grid(*args, **kwargs)
        for index, aList in enumerate(self.scrolledLists):
            self.listTitleLabels[index].grid(row=0, column=index*2, columnspan=2)
            aList.grid(row=1, column=index*2, columnspan=2)
        try:
            self.TkVars[0].set(" ".join(self.dataSource.valuesForColumn(0)))
        except AttributeError:
            stderr.write(str(self) + " has no dataSource.\n")

    def clear(self):
        """
        """
        for aList in self.scrolledLists:
            aList.clear()
    
    def setColumnTitles(self, titleList):
        """
        """
        try:
            for index, title in enumerate(titleList):
                self.listTitleLabels[index].configure(text = title)

        except KeyError:
            stderr.write('There are more titles than lists avalaible.\n')

    @notify_delegates
    def changeSelection(self, evt):
        """
        """
        w = evt.widget
        listBoxes = [listBox.listbox for listBox in self.scrolledLists]
        self.selectedList = listBoxes.index(w)
        self.selectedRows = tuple(w.curselection() for w in self.scrolledLists)

    def updateDisplay(self, evt):
        """
        """
        self.changeSelection(evt)
        for listIndex in xrange(self.selectedList + 1, len(self.TkVars)):
            self.TkVars[listIndex].set('')
        try:
            for index in xrange(1, len(self.TkVars)):
                self.TkVars[index].set(" ".join(self.dataSource.valuesForColumn(index)))
        except AttributeError:
            stderr.write(str(self) + " has no dataSource.\n")


class NOEDataViewer(Tk.Toplevel, DelegateProviderMixin):
    """
    """
    def __init__(self, dataController):
        Tk.Toplevel.__init__(self, class_='NOEDataViewer')
        self.NOEView = DependantColumnsTableView(masterView=self, NumberOfResiLists=2)
        self.NOEVController = NOEViewController(dataController, self, self.NOEView)
        self.NOEView.dataSource = self.NOEVController
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self, textvariable=self.constraintSelectionText,
                                          justify=Tk.CENTER)
        self.NOEValues = dict()
        self.NOEValueLabels = dict()
        for valueType in ('constraint', 'min', 'plus', 'actual'):
            self.NOEValues[valueType] = Tk.DoubleVar()
            self.NOEValueLabels[valueType] = ttk.Label(self, textvariable=self.NOEValues[valueType], width=3)

        self.add_delegate(self.NOEVController)
        self.NOEView.add_delegate(self.NOEVController)

        self.widgetCreation()
    
    @notify_delegates
    def widgetCreation(self):
        ttk.Label(self, text='Select NOE residue and / or atom to see their counterparts :').grid(row=1, column=0, columnspan=8)
        self.labelConstraints.grid(row=0, column=0, columnspan=8)
        ttk.Label(self, text='1st residue').grid(row=2, column=0, columnspan=4)
        ttk.Label(self, text='2nd residue').grid(row=2, column=4, columnspan=4)
        self.NOEView.grid(row=3, column=0, columnspan=8)
        self.NOEView.setColumnTitles(('Name', 'Atom', 'Name', 'Atom'))

        columnPosition = 0
        for key, aLabel in self.NOEValueLabels.iteritems():
            ttk.Label(self, text=key).grid(row=4, column=columnPosition, sticky=Tk.W)
            aLabel.grid(row=4, column=columnPosition + 1)
            aLabel.state(['disabled'])
            columnPosition += 2

    def setTitle(self, NumberOfConstraints, numberOfResiduesInvolved):
        """
        """
        self.constraintSelectionText.set(str(NumberOfConstraints) + " constraints used, involving " +
                                    str(numberOfResiduesInvolved) + " residues")

    def setLabelsState(self, state):
        """
        """
        if 'disabled' in state:
            for value in self.NOEValues.itervalues():
                value.set(0)
        for aLabel in self.NOEValueLabels.itervalues():
            aLabel.state(state)

    def setLabelValues(self, values, state):
        """
        """
        style = ttk.Style()
        style.configure("Red.TLabel", foreground="red")
        style.configure("Green.TLabel", foreground="green")

        for key, value in self.NOEValues.iteritems():
            value.set(round(float(values[key]), 1))

        if state == 'Satisfied':
            self.NOEValueLabels['constraint'].configure(style="Green.TLabel")
        if state == 'unSatisfied':
            self.NOEValueLabels['constraint'].configure(style="Red.TLabel")



class NOEViewController(object):
    """
    """
    def __init__(self, dataController, NOEView, NOETableView):
        self.NOEDataController = dataController
        self.listsControllers = (resiNumberListController(), atomTypeListController(), resiNumberListController(), atomTypeListController())
        self.NOETableView = NOETableView
        self.NOEView = NOEView

    def on_before_widgetCreation(self, *args, **kwargs):
        """
        """
        for atom in self.NOEDataController.displayedAtoms:
            self.listsControllers[0].addAtom(atom)

    def on_after_widgetCreation(self, *args, **kwargs):
        """
        """
        self.NOEView.setTitle(len(self.NOEDataController), len([residue for residue in self.NOEDataController.residuesList]))

    def on_after_changeSelection(self, *args, **kwargs):
        """
        """
        if self.NOETableView.selectedList == 0:
            self.selectResidueDisplayed()
        if self.NOETableView.selectedList == 1:
            self.selectAtomDisplayed()
        if self.NOETableView.selectedList == 2:
            self.selectResiduePartner()
        if self.NOETableView.selectedList == 3:
            self.selectAtomPartner()

    def selectResidueDisplayed(self):
        """
        """
        self.NOEView.setLabelsState(['disabled'])
        for index_controller in xrange(1, len(self.listsControllers)):
            self.listsControllers[index_controller].clear()

        if self.NOETableView.selectedRows[0]:
            selectedAtoms = list()
            for resi_number_index in self.NOETableView.selectedRows[0]:
                selectedAtoms.extend(self.listsControllers[0].values()[resi_number_index])
            self.NOEDataController.setSelectedAtoms(selectedAtoms)
            for atom in self.NOEDataController.partnerAtoms:
                self.listsControllers[2].addAtom(atom)

            if len(self.NOETableView.selectedRows[0]) == 1:
                for atom in selectedAtoms:
                    self.listsControllers[1].addAtom(atom)

            zoom(self.NOEDataController.structure, self.NOEDataController.partnerAtoms+selectedAtoms)

    def selectAtomDisplayed(self):
        """
        """
        self.NOEView.setLabelsState(['disabled'])
        for index_controller in xrange(2, len(self.listsControllers)):
            self.listsControllers[index_controller].clear()

        if len(self.NOETableView.selectedRows[1]) == 1:
            selectedAtoms = [self.listsControllers[1].values()[atomNumber] for atomNumber in self.NOETableView.selectedRows[1]]
            self.NOEDataController.setSelectedAtoms(selectedAtoms[0])
            for atom in self.NOEDataController.partnerAtoms:
                self.listsControllers[2].addAtom(atom)
            zoom(self.NOEDataController.structure, self.NOEDataController.partnerAtoms+selectedAtoms[0])

    def selectResiduePartner(self):
        """
        """
        selection = self.NOETableView.selectedRows[2]

        if len(selection) == 1:
            if len(self.NOETableView.selectedRows[1]) == 1:
                selectedPartnerAtoms = self.listsControllers[2].values()[selection[0]]
                self.listsControllers[3].addAtom(selectedPartnerAtoms[0])
                zoom(self.NOEDataController.structure, self.NOEDataController.selectedAtoms+selectedPartnerAtoms)

    def selectAtomPartner(self):
        """
        """
        selection = self.NOETableView.selectedRows[3]
        partnerAtoms = self.listsControllers[3].values()

        if len(selection) == 1:
            zoom(self.NOEDataController.structure, partnerAtoms[0]+self.NOEDataController.selectedAtoms)

            constraintValues = self.NOEDataController.constraintValueForAtoms(partnerAtoms[0]+self.NOEDataController.selectedAtoms)
            if constraintValues:
                self.NOEView.setLabelsState(['!disabled'])
                self.NOEView.setLabelValues(*constraintValues[0])

    def valuesForColumn(self, index):
        """
        """
        return self.listsControllers[index]
    



class About(ttk.Frame):
    """
    """
    def __init__(self, master=None):
        """
        """
        ttk.Frame.__init__(self, master)
        self.aboutFrame = ttk.LabelFrame(self, text=u'About')
        self.aboutFrame.grid(row=1, column=0)
        ttk.Label(self.aboutFrame, justify=Tk.CENTER, text=u"This Pymol plugin" +
                  " has been written \nbecause I thought it would be useful to" +
                  "check \nmy NOEs during my postdocship. I hope it'll" +
                  " \nhelp you as well. Feel free to send \nany comments to " +
                  ": github.com/oserve/PyNMR\nThis plugin is free and may be " +
                  "copied as \nlong as you respect the copyright."
                  ).grid(row=0, column=0)
        self.helpFrame = ttk.LabelFrame(self, text=u'Quick Help')
        self.helpFrame.grid(row=0, column=0)
        ttk.Label(self.helpFrame, text=u'- First open a file or ' +
                  'download one frome the PDB\n  using a structure PDB code\n' +
                  '- Then select which type of constraint you want\n' +
                  '- You can select residue numbers (X+Y+Z)\n  or a range ' +
                  '(X-Z) or both (default is all)\n - After that, select the ' +
                  'structure you want\n to' +
                  ' display the constraints on.\n - Finally, click on the' +
                  ' display you want\n (sticks or colormap)'
                  ).grid(row=0, column=0)

"""
Definitions for application defaults
"""

configFileName = "pymolNMR.cfg"
defaults = dict()

standardDefaults = {'radius': 0.03, 'cutOff': 0.3,
					'colors':
						{
							'Satisfied': [1, 1, 1, 1, 1, 1],
							'tooFar': [ 1, 0, 0, 1, 0, 0],
							'tooClose': [ 0, 0, 1, 0, 0, 1]
						},
		'gradient': 'blue_white_red', 'method': 'sum6',
		'UnSatisfactionMarker': '_US_', 'SatisfactionMarker': '_S_',
		'rangeCutOff': 5,
		'urlPDB': 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/',
		'gradientColorList' : (
            "blue_green", "blue_magenta", "blue_red", "blue_white_green",
            "blue_white_magenta", "blue_white_red", "blue_white_yellow",
            "blue_yellow", "cbmr", "cyan_magenta", "cyan_red",
            "cyan_white_magenta", "cyan_white_red", "cyan_white_yellow",
            "cyan_yellow", "gcbmry", "green_blue", "green_magenta",
            "green_red", "green_white_blue", "green_white_magenta",
            "green_white_red", "green_white_yellow", "green_yellow",
            "green_yellow_red", "magenta_blue", "magenta_cyan",
            "magenta_green", "magenta_white_blue", "magenta_white_cyan",
            "magenta_white_green", "magenta_white_yellow", "magenta_yellow",
            "rainbow", "rainbow2", "rainbow2_rev", "rainbow_cycle",
            "rainbow_cycle_rev", "rainbow_rev", "red_blue", "red_cyan",
            "red_green", "red_white_blue", "red_white_cyan", "red_white_green",
            "red_white_yellow", "red_yellow", "red_yellow_green", "rmbc",
            "yellow_blue", "yellow_cyan", "yellow_cyan_white", "yellow_green",
            "yellow_magenta", "yellow_red", "yellow_white_blue",
            "yellow_white_green", "yellow_white_magenta", "yellow_white_red",
            "yrmbcg")
        }


def registerDefaults(newDefaults):
    """
    """
    defaults.update(newDefaults)


def defaultForParameter(parameter):
    """
    """
    return defaults[parameter]


def setToStandardDefaults():
    """
    """
    defaults.update(standardDefaults)
    if exists(configFileName):
        remove(configFileName)


def saveDefaults():
    """
    """
    with open(configFileName, 'w') as configFile:
        pickle.dump(defaults, configFile)


def loadDefaults():
    """
    """
    if exists(configFileName):
        configFile = open(configFileName, 'r')
        defaults.update(pickle.load(configFile))
        configFile.close()
    else:
        setToStandardDefaults()


regInput = re.compile(r'[^0-9+\-\,\s]')


class ConstraintSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text=u"Constraints Selection")
        self.consRangeFrame = RangeSelectionPanel(self)
        self.violationsFrame = ViolationSelectionPanel(self)
        self.structureManagement = StructureSelectionPanel(self)
        self.panelsList = (self.consRangeFrame, self.violationsFrame, self.structureManagement)
        self.widgetCreation()

    def widgetCreation(self):
        # Creation of range input
        self.consRangeFrame.grid(row=0, column=0)

        # Creation of Violations inputs
        self.violationsFrame.grid(row=0, column=1)

        # Creation of structure inputs
        self.structureManagement.grid(row=1, column=0, columnspan=2)

    def getInfo(self):
        infos = dict()
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos

    def setDefaults(self):
        self.violationsFrame.cutOff.set(defaultForParameter("cutOff"))
        self.structureManagement.comboPDB.values = getModelsNames(defaultForParameter('SatisfactionMarker'), defaultForParameter('UnSatisfactionMarker'))


class RangeSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Range Selection")

        self.RangesVars = dict()
        self.RangesCB = dict()
        self.RangesFunctions = dict()
        self.ranges = ('intra', 'sequential', 'medium', 'long')
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, consRange in enumerate(self.ranges):
            self.RangesVars[consRange] = Tk.IntVar(self)
            self.RangesCB[consRange] = ttk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesVars["all"] = Tk.IntVar(self)
        self.RangesCB["all"] = ttk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition + 1, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        """
        """
        state_all = self.RangesVars["all"].get()
        for consRange in self.ranges:
            self.RangesVars[consRange].set(state_all)

    def tick(self):
        """
        """
        self.RangesVars["all"].set(1)
        if any(self.RangesVars[aRange].get() == 0 for aRange in self.ranges):
            self.RangesVars["all"].set(0)

    def getInfo(self):
        """
        """
        ranges = tuple(aRange for aRange in self.ranges if self.RangesVars[aRange].get() == 1)
        return {"residuesRange": ranges}


class ViolationSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Constraint state :")

        self.ViolationsVars = dict()
        self.UnSatisfiedCB = dict()
        self.cutOff = Tk.DoubleVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, violationType in enumerate(('unSatisfied', 'Satisfied')):
            self.ViolationsVars[violationType] = Tk.IntVar(self)
            self.UnSatisfiedCB[violationType] = ttk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatisfiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W, columnspan=2)
            self.ViolationsVars[violationType].set(1)

        rowPosition += 1
        ttk.Label(self, text=u'Distance CutOff :').grid(row=rowPosition,
                                                        column=0, columnspan=2)

        rowPosition += 1
        self.spinBox_cutOff = Tk.Spinbox(self, textvariable=self.cutOff,
                                         from_=0.0, to=10.0, increment=0.1,
                                         format='%2.1f', width=6)
        self.spinBox_cutOff.grid(row=rowPosition, column=0)
        ttk.Label(self, text=u'\u212b').grid(row=rowPosition, column=1)

    def getInfo(self):
        """
        """
        violationStates = tuple(violationType for violationType in ('unSatisfied', 'Satisfied') if self.ViolationsVars[violationType].get() == 1)
        return {"cutOff": self.cutOff.get(), "violationState": violationStates}


class StructureSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Structure")
        self.residueRanges = Tk.StringVar()
        self.structureList = Tk.StringVar()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u"Structure :").grid(row=0, column=0)
        self.comboPDB = ttk.Combobox(self, state='readonly',
                                     textvariable=self.structureList)
        self.comboPDB.grid(row=0, column=1)
        self.comboPDB.bind('<Enter>', self.updatePdbList)

        ttk.Label(self, text=u'Residues ranges :').grid(row=2, column=0, sticky=Tk.W)
        self.entry_res = ttk.Entry(self, textvariable=self.residueRanges)
        self.entry_res.grid(row=2, column=1)
        self.residueRanges.set('all')

    def getInfo(self):
        """
        """
        return {"structure": self.structureList.get(),
                "ranges": interpret(self.residueRanges.get())}

    def updatePdbList(self, event):
        """
        """
        infos = self.mainApp.NMRInterface.getInfo()
        self.comboPDB['values'] = getModelsNames(infos['SatisfactionMarker'], infos['UnSatisfactionMarker'])

def interpret(residuesList):
    """
    """
    resList = set()
    if not regInput.findall(residuesList):
        for resi_range in residuesList.split("+"):
            aRange = resi_range.split("-")
            if 1 <= len(aRange) <= 2:
                resList.update(str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[-1]) + 1))
            else:
                stderr.write("Residues set definition error : " + residuesList + "\n")

    return resList



class FileSelectionPanel(ttk.LabelFrame):
    """This panel allows to import constraint file
    into the Core. Also it allows the selection of the file
    for the following calculations.
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text="Constraints Files")
        self.constraintsFileList = Tk.StringVar()
        self.infoLabelString = Tk.StringVar()
        self.loadFileButton = ttk.Button(self, text=u"Load file",
                                         command=self.loadFile)
        self.removeFileButton = ttk.Button(self, text=u"Remove file",
                                           command=self.removeFile)
        self.constraintsList = ScrolledList(self, listvariable=self.constraintsFileList)
        self.downloadButton = ttk.Button(self, text=u"Download \nfrom PDB",
                                         command=self.downloadRestraintFileWin)
        self.saveButton = ttk.Button(self, text=u'Save File',
                                     command=self.saveFile)
        self.infoLabel = ttk.Label(self, textvariable=self.infoLabelString)
        self.selectedFile = ""
        self.widgetCreation()
        self.NMRCommands = ""  # Must be set by application at run time
        self.mainGUI = ""  # Must be set at run time

    def widgetCreation(self):
        """
        """
        self.constraintsList.exportselection = 0
        self.constraintsList.grid(row=0, column=1, rowspan=4)
        self.loadFileButton.grid(row=0, column=0)
        self.removeFileButton.grid(row=1, column=0)
        self.downloadButton.grid(row=2, column=0)
        self.saveButton.grid(row=3, column=0)
        self.infoLabel.grid(row=4, column=0, columnspan=2)
        self.constraintsList.bind('<<ListboxSelect>>', self.onStructureSelect)

    def loadFile(self):
        """Use a standard Tk dialog to get filename,
        constraint type is selected prior to the opening of dialog.
        Use the filename to load the constraint file in the Core.
        """
        filename = tkFileDialog.askopenfilename(
            title="Open a constraint file")
        if len(filename):
            self.NMRCommands.LoadConstraints(filename)
            self.updateFilelist()

    def updateFilelist(self):
        """
        """
        fileList = " ".join(self.NMRCommands.keys()).strip()
        self.constraintsFileList.set(fileList)
        if not fileList:
            self.infoLabelString.set('')
        else:
            self.constraintsList.listbox.activate(len(fileList) - 1)

    def removeFile(self):
        """
        """
        toRemove = self.selectedFile
        if toRemove:
            del self.NMRCommands[toRemove]
        self.updateFilelist()

    def saveFile(self):
        """
        """
        toSave = self.selectedFile
        if toSave:
            filename = tkFileDialog.asksaveasfilename(
                title="Save constraint file as", initialfile=toSave)
            if filename is not None:
                self.NMRCommands.saveConstraintsFile(toSave, filename)

    def downloadRestraintFileWin(self):
        """
        """
        pdbCode = tkSimpleDialog.askstring('PDB NMR Restraints',
                                           'Please enter a 4-digit pdb code:',
                                           parent=self)
        if pdbCode:
            infos = self.mainGUI.getInfo()
            self.NMRCommands.downloadFromPDB(pdbCode, infos["urlPDB"])
            self.updateFilelist()

    def onStructureSelect(self, evt):
        """
        """
        # Note here that Tkinter passes an event object
        w = evt.widget
        selection = w.curselection()
        if len(selection) == 1:
            index = int(selection[0])
            self.selectedFile = w.get(index)
            self.infoLabelString.set("Contains " +
                                     str(len(self.NMRCommands[self.selectedFile])) +
                                     " Constraints (" + self.NMRCommands[self.selectedFile].format + ")")

    def getInfo(self):
        """
        """
        if self.selectedFile:
            return {"constraintFile": self.selectedFile}
        else:
            return {"constraintFile": ""}




class mainPanel(ttk.Frame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.Frame.__init__(self, master)
        self.fileSelection = FileSelectionPanel(self)
        self.constraintPanel = ConstraintSelectionPanel(self)
        self.NOEDrawing = NOEDrawingPanel(self)
        self.panelsList = (self.fileSelection, self.constraintPanel)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.fileSelection.grid(row=0, column=0)
        self.constraintPanel.grid(row=1, column=0)
        self.NOEDrawing.grid(row=2, column=0)

    def getInfo(self):
        """
        """
        infos = dict()
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos



class NOEDrawingPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text="NOE Representation")
        self.sticksButton = ttk.Button(self, text="Sticks",
                                       command=self.showSticks)
        self.densityButton = ttk.Button(self, text="Density",
                                        command=self.showDensity)
        self.cleanButton = ttk.Button(self, text="Clean Sticks",
                                      command=self.cleanAll)
        self.mainGUI = None  # Must be set at run time
        self.NMRCommands = None  # Must be set by application at run time
        self.dataControllers = dict()
        self.dataViewers = dict()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.sticksButton.grid(row=0, column=0)
        self.densityButton.grid(row=0, column=1)
        self.cleanButton.grid(row=0, column=2)

    def showSticks(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])

            self.NMRCommands.showSticks(infos["constraintFile"],
                                        infos["structure"],
                                        infos["colors"],
                                        infos["radius"],
                                        infos["UnSatisfactionMarker"],
                                        infos["SatisfactionMarker"])

            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands.drawer.displayedConstraintsSticks.intersection(self.NMRCommands.get(infos["constraintFile"], "").constraintsManagerForDataType('NOE')),
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]])

    def showDensity(self):
        """
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.commandsInterpretation(infos["constraintFile"],
                                                    infos["ranges"],
                                                    infos["residuesRange"],
                                                    infos["violationState"],
                                                    infos["cutOff"],
                                                    infos["method"],
                                                    infos["rangeCutOff"])
            self.NMRCommands.showNOEDensity(infos["constraintFile"],
                                            infos["structure"],
                                            infos["gradient"])

            self.dataControllers[infos["constraintFile"]] = NOEDataController(self.NMRCommands.drawer.displayedConstraintsDensity.intersection(self.NMRCommands.get(infos["constraintFile"], "").constraintsManagerForDataType('NOE')),
                                                                              infos["constraintFile"],
                                                                              infos["structure"])
            self.dataViewers[infos["constraintFile"]] = NOEDataViewer(self.dataControllers[infos["constraintFile"]])

    def cleanAll(self):
        """Remove all displayed sticks
        """
        infos = self.mainGUI.getInfo()

        if self.infoCheck(infos):
            self.NMRCommands.cleanScreen()
            try:
                self.dataViewers[self.mainGUI.getInfo()["constraintFile"]].destroy()
                del self.dataViewers[self.mainGUI.getInfo()["constraintFile"]]
                del self.dataControllers[self.mainGUI.getInfo()["constraintFile"]]
            except KeyError:
                pass


    @staticmethod
    def infoCheck(infos):
        """
        """
        return all(item != "" for item in infos.values())




class SticksPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        self.satisfactions = ("Satisfied", "tooFar", "tooClose")
        self.satisfactionColorButtons = dict()
        ttk.LabelFrame.__init__(self, master, text=u"NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius,
                                         from_=0.00, to=0.5, increment=0.01,
                                         format='%1.2f', width=4)
        for satisfaction in self.satisfactions:
            self.satisfactionColorButtons[satisfaction] = ttk.Button(self,
                                                                     text=u"Choose color",
                                                                     command=lambda satisfaction=satisfaction: self.setColor(satisfaction))
        self.UnSatisfactionMarker = Tk.StringVar(self)
        self.SatisfactionMarker = Tk.StringVar(self)
        self.UnSatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.UnSatisfactionMarker, width=6)
        self.SatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.SatisfactionMarker, width=6)
        self.colors = dict()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Stick radius (\u212b):').grid(row=0, column=0)
        self.spinBox_Radius.grid(row=0, column=1)
        ttk.Label(self, text=u'Satisfied constraint').grid(row=1, column=0)
        self.satisfactionColorButtons["Satisfied"].grid(row=1, column=1)
        ttk.Label(self, text=u"Atoms too far").grid(row=2, column=0)
        self.satisfactionColorButtons["tooFar"].grid(row=2, column=1)
        ttk.Label(self, text=u"Atoms too close").grid(row=3, column=0)
        self.satisfactionColorButtons["tooClose"].grid(row=3, column=1)
        ttk.Label(self, text=u'Unsatisfied Marker :').grid(row=4, column=0)
        self.UnSatisfactionMarkerEntry.grid(row=4, column=1)
        ttk.Label(self, text=u'Satisfied Marker :').grid(row=5, column=0)
        self.SatisfactionMarkerEntry.grid(row=5, column=1)

    def setDefaults(self):
        """
        """
        self.colors = defaultForParameter("colors")
        self.UnSatisfactionMarker.set(defaultForParameter("UnSatisfactionMarker"))
        self.SatisfactionMarker.set(defaultForParameter("SatisfactionMarker"))
        self.radius.set(defaultForParameter("radius"))

    def getInfo(self):
        """
        """
        return {"radius": self.radius.get(),
                "colors": self.colors,
                "UnSatisfactionMarker": self.UnSatisfactionMarker.get(),
                "SatisfactionMarker": self.SatisfactionMarker.get()}

    def setColor(self, satisfaction):
        """
        """
        currentColor = self.float2hex(self.colors[satisfaction])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors[satisfaction] = self.int2floatColor(result[0])

    @staticmethod
    def int2floatColor(color):
        """
        """
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0,
                color[0]/255.0, color[1]/255.0, color[2]/255.0]

    @staticmethod
    def float2hex(color):
        """From stackoverflow
        """
        return '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))

class DensityPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE density Preferences")
        self.gradient = Tk.StringVar()
        self.gradientSelection = ttk.Combobox(self, state="readonly",
                                              textvariable=self.gradient)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Gradient :').grid(row=0, column=0)
        self.gradientSelection.grid(row=0, column=1)

    def getInfo(self):
        """
        """
        return {"gradient": self.gradient.get()}


class PreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE Preferences")
        self.panelsList = list()
        self.methodsList = ((u"\u03a3 r-6", "sum6"), (u"(\u03a3 r-6)/n", "ave6"))
        self.selectedMethod = Tk.StringVar()
        self.sticksPanel = SticksPreferencesPanel(self)
        self.panelsList.append(self.sticksPanel)
        self.densityPanel = DensityPreferencesPanel(self)
        self.panelsList.append(self.densityPanel)
        self.savePrefButton = ttk.Button(self, text=u"Save preferences",
                                         command=self.savePrefs)
        self.resetButton = ttk.Button(self, text=u"Defaults",
                                      command=self.resetPrefs)
        self.rangeCutOff = Tk.IntVar(self)
        self.rangeCutOffEntry = Tk.Spinbox(self, textvariable=self.rangeCutOff,
                                           from_=1, to=20, increment=1, width=2)
        self.url = Tk.StringVar(self)
        self.urlTextField = ttk.Entry(self, textvariable=self.url)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, justify=Tk.CENTER, text=u'NOE Distance calculation :\n(> 2 atoms)').grid(
            row=0, column=0, rowspan=2)

        for position, (methodName, method) in enumerate(self.methodsList):
            ttk.Radiobutton(self, text=methodName, variable=self.selectedMethod,
                            value=method).grid(row=position, column=1)
        position += 1
        ttk.Label(self, text=u'Residue range cut-off :').grid(row=position, column=0)

        self.rangeCutOffEntry.grid(row=position, column=1)
        position += 1
        self.sticksPanel.grid(row=position, column=0, columnspan=2)
        position += 1
        self.densityPanel.grid(row=position, column=0, columnspan=2)
        position += 1
        ttk.Label(self, text=u'PDB.org URL for download').grid(row=position, column=0, columnspan=2)
        position += 1
        self.urlTextField.grid(row=position, column=0, columnspan=2)
        position += 1
        self.savePrefButton.grid(row=position, column=0)
        self.resetButton.grid(row=position, column=1)

    def savePrefs(self):
        """
        """
        registerDefaults(self.mainGUI.getInfo())
        saveDefaults()

    def resetPrefs(self):
        """
        """
        setToStandardDefaults()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.densityPanel.gradient.set(defaultForParameter("gradient"))
        self.selectedMethod.set(defaultForParameter("method"))
        self.url.set(defaultForParameter("urlPDB"))
        self.rangeCutOff.set(defaultForParameter("rangeCutOff"))
        self.densityPanel.gradientSelection['values'] = defaultForParameter('gradientColorList')
        self.sticksPanel.setDefaults()

    def getInfo(self):
        """
        """
        infos = {"method": self.selectedMethod.get(),
                 "rangeCutOff": self.rangeCutOff.get(),
                 "urlPDB": self.url.get()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


loadDefaults()

Core = NMRCore()

pyNMR = NMRApplication(Core, app="NoGUI")

def __init__(self):
    """Add the plugin to Pymol main menu
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'PyNMR',
                             label='PyNMR...',
                             command=lambda s=self: NMRApplication(Core, app="GUI"))


PyNMRCLI = pyNMR.NMRCLI

def showNOE(structure='', managerName="", residuesList='all',
            dist_range='all', violationState='all',
            violCutoff=defaultForParameter("cutOff"),
            method=defaultForParameter('method'),
            radius=defaultForParameter("radius"),
            colors=defaultForParameter("colors"),
            rangeCutOff=defaultForParameter("rangeCutOff"),
            UnSatisfactionMarker=defaultForParameter("UnSatisfactionMarker"),
            SatisfactionMarker=defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.showNOE(structure, managerName, residuesList, dist_range,
                     violationState, violCutoff, method, radius, colors,
                     rangeCutOff, UnSatisfactionMarker, SatisfactionMarker)

def LoadConstraints(filename=""):
    """
    """
    PyNMRCLI.LoadConstraints(filename)

def showNOEDensity(structure='', managerName="", residuesList='all',
                   dist_range='all', violationState='all',
                   violCutoff=defaultForParameter("cutOff"),
                   rangeCutOff=defaultForParameter("rangeCutOff"),
                   method=defaultForParameter('method'),
                   colors=defaultForParameter("gradient")):
    """
    """
    PyNMRCLI.showNOEDensity(structure, managerName, residuesList,
                            dist_range, violationState, violCutoff, rangeCutOff,
                            method, colors)

def loadAndShow(filename, structure='', residuesList='all', dist_range='all',
                violationState='all',
                violCutoff=defaultForParameter("cutOff"),
                method=defaultForParameter('method'),
                rangeCutOff=defaultForParameter("rangeCutOff"),
                radius=defaultForParameter("radius"),
                colors=defaultForParameter("colors"),
                UnSatisfactionMarker=defaultForParameter("UnSatisfactionMarker"),
                SatisfactionMarker=defaultForParameter("SatisfactionMarker")):
    """
    """
    PyNMRCLI.loadAndShow(filename, structure, residuesList, dist_range,
                         violationState, violCutoff, method, rangeCutOff,
                         radius, colors, UnSatisfactionMarker,
                         SatisfactionMarker)

def downloadNMR(pdbCode, url=defaultForParameter("urlPDB")):
    """
    """
    PyNMRCLI.downloadNMR(pdbCode, url)

def cleanScreen(filename):
    """
    """
    PyNMRCLI.cleanScreen(filename)


extend("LoadConstraints", LoadConstraints)
extend("showNOE", showNOE)
extend("showNOEDensity", showNOEDensity)
extend("loadAndShow", loadAndShow)
extend("downloadNMR", downloadNMR)
extend("cleanScreen", cleanScreen)
