"""Helper script

    Gathers all python files into one
    the final file needs clean up
"""
from os import chdir, listdir
from sys import stderr, stdout

collection = ""
importCollection = ""

mainDirectory = "/Users/olivier/Pymol_scripts/PyNMR"
directoriesList = ['/Application', '/Application/Core',
                   '/Application/Core/Constraints',
                   '/Application/GUI', '/Application/GUI/Panels']

for directory in directoriesList:
    chdir(mainDirectory+directory)
    fileList = listdir('.')
    for aFile in fileList:
        fileComponents = aFile.split('.')
        if len(fileComponents) == 2:
            if fileComponents[1] == 'py':
                if fileComponents[0] != '__init__':
                    stderr.write('Parsing file : '+aFile+'\n')
                    fin = open(aFile, 'r')
                    for line in fin:
                        if line.find("import") == -1:
                            if line.find('#') != 0:
                                collection = collection + line
                        else:
                            if line.find('"""') == -1:
                                if importCollection.find(line) == -1:
                                    importCollection = importCollection + line
                            else:
                                collection = collection + line
                    fin.close()

fin = open(mainDirectory + "/pymolNMR.py", 'r')
for line in fin:
    if line.find("import") == -1:
        collection = collection + line
    else:
        importCollection = importCollection + line
fin.close()

stdout.write(importCollection)
stdout.write(collection)
