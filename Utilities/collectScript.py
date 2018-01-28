"""Helper script

    Gathers all python files into one
    the final file still needs clean up
"""
from os import walk
from os.path import basename, join
from sys import stderr, stdout

collection = ""
importCollection = set()

mainDirectory = '/Users/olivier/Pymol_scripts/PyNMR/'

importAsException = set()

ExceptDirs = ("Tests", "Utilities")
ExceptFiles = ("__init__.py", "PyNMR.py", "DebugMVI.py")

projectFileList = list()
for item in walk(mainDirectory):
    if '.' not in item[0]:
        if all(ExceptDir not in item[0] for ExceptDir in ExceptDirs):
            for aFile in item[2]:
                if aFile.endswith('.py') and all(aFile != ExceptFile for ExceptFile in ExceptFiles):
                    projectFileList.append(join(item[0], aFile))

moduleList = set(basename(aFile).split('.')[0] for aFile in projectFileList)

for aFile in projectFileList:
    stderr.write('Parsing file : ' + aFile + '\n')
    with open(aFile, 'r') as fin:
        importException = False
        for line in fin:
            if not 'try' in line:
                importException = True
            if not 'except' in line:
                importException = False
            if not "import" in line:
                if not line.startswith('#'):
                    for importAs in importAsException:
                        if importAs in line:
                            line.replace(importAs+'.', '')
                    collection += line
            else:
                if not importException:
                    if not '"""' in line:
                        if any(aModuleName in line for aModuleName in moduleList):
                            if ' as ' in line:
                                importAsException.add(line.split(' as ')[1])
                        else:
                            importCollection.add(line)
                    else:
                        collection += line
                else:
                    collection += line
        collection += '\n'

stdout.write("".join(importCollection))
stdout.write("".join(collection))
