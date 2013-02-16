fileList=['AtomClass.py', 'Constraint.py', 'NOE.py', "ConstraintManager.py", 'ConstraintLoading.py',  'ConstraintsDrawing.py', 'Filtering.py', 'Geom.py', 'MolecularViewerInterface.py', 'NMRCore.py', 'Panels.py', 'NMRGUI.py', 'pymolNMR.py']

collection=""
for fileName in fileList:
    fin=open(fileName,'r')
    if line.find("import")==-1:
        collection = collection+line
    fin.close()

print "import re\nfrom sys import stderr, stdout\nfrom math import sqrt, pow\nfrom os.path import basename, exists\nfrom os import getcwd, chdir, path\nimport Tkinter as Tk\nimport Pmw\nimport tkFileDialog\nimport tkColorChooser\nfrom pymol import cmd"
print collection
print "def __init__(self):\n\tself.menuBar.addmenuitem('Plugin', 'command', 'PyNMR', label = 'PyNMR', command = lambda s=self : pyNMR.NMRInterface.startGUI()\n"