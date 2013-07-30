fileList=['AtomClass.py', 'Constraint.py', 'NOE.py', "ConstraintManager.py", 'ConstraintLoading.py', 'ConstraintsDrawing.py', 'Filtering.py', 'Geom.py', 'NMRCore.py', 'Panels.py', 'NMRGUI.py', 'pymolNMR.py']

collection=""
for fileName in fileList:
    fin=open(fileName,'r')
    for line in fin:
        if line.find("import")==-1:
            collection = collection+line
    fin.close()
        
print "import re\nfrom sys import stderr, stdout\nfrom math import sqrt, pow\nfrom os.path import basename, exists\nfrom os import getcwd, chdir, path\nimport Tkinter as Tk\nimport Pmw\nimport tkFileDialog\nimport tkColorChooser\nfrom pymol.cmd import select, get_names, get_model, zoom, spectrum, extend, delete, load_cgo, alter\nfrom pymol.cgo import CYLINDER"
print "def drawConstraint(points, color, aRadius, ID):\n\tcons =[CYLINDER]+list(points[0])+list(points[1])+[aRadius]+color\n\tload_cgo(cons, ID)\n"
print "def alterBFactors(pdb, bFactor):\n\talter(pdb,\"b=\"+ str(bFactor))"
print "def zeroBFactors(pdb):\n\talterBFactors(pdb, 0)"
print "def setBfactor(selection, bFactor):\n\talterBFactors(selection, bFactor)"
print "def paintDensity(color_gradient, pdb):\n\tspectrum(\"b\", color_gradient, pdb)"
print collection
print "def __init__(self):\n\tself.menuBar.addmenuitem('Plugin', 'command', 'PyNMR', label = 'PyNMR', command = lambda s=self : pyNMR.startGUI())\n"