"""Helper script

    Gathers all python files into one
    the final file still needs clean up
"""
from os import listdir
from os.path import basename, join
from sys import stderr, stdout

collection = list()
importCollection = set()

mainDirectory = '/Users/olivier/Pymol_scripts/PyNMR/'
directoriesList = ('Application', 'Application/Core',
                   'Application/Core/Constraints',
                   'Application/GUI', 'Application/GUI/Panels',
                   'Application/DataControllers')

importAsException = set()

projectFileList=[join(mainDirectory, directory, aFile) for directory in directoriesList for aFile in listdir(mainDirectory+directory) if aFile.endswith('py') and not '__init__' in aFile]

moduleList = [basename(aFile).split('.')[0] for aFile in projectFileList]

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
                        for aModuleName in moduleList:
                            if aModuleName in line:
                                if 'as' in line:
                                    importAsException.add(line.split(' as ')[1])
                            break
                        else:
                            importCollection.add(line)
                    else:
                        collection += line
                else:
                    collection += line

with open(mainDirectory + "/pymolNMR.py", 'r') as fin:
    for line in fin:
        if not "import" in line:
            collection += line
        else:
            importCollection.add(line)

stdout.write("".join(importCollection))
stdout.write("".join(collection))
