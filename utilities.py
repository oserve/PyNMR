from sys import stdout

def checkConstraints(manager,aPdb):
    ManagersList[manager].setPDB(aPdb)
    ManagersList[manager].setAtoms()
    n=0
    for constraint in ManagersList[manager].constraints:
        i=0
        for i in range(n,len(ManagersList[manager].constraints)):
            if not constraint.const['number']==ManagersList[manager].constraints[i].const['number']:
                if compareConstraints(constraint, ManagersList[manager].constraints[i]):
                    stdout("check contraints : " + constraint.printCons()+" "+ManagersList[manager].constraints[i].printCons()+"\n")
            i=i+1
        n=n+1

def compareConstraints(constraintA,constraintB):
    problem={'init':0,'final':0}
    for orderInit,orderFinal in [['init','final'],['final','init']]:
        if constraintA.resis[orderInit]['number']==constraintB.resis['init']['number']:
            if constraintA.resis[orderFinal]['number']==constraintB.resis['final']['number']:
                if constraintA.resis[orderInit]['atoms']==constraintB.resis['init']['atoms']:
                    if constraintA.resis[orderFinal]['atoms']==constraintB.resis['final']['atoms']:
                        for atA in cmd.get_model(constraintA.atoms[orderFinal].getID()).atom:
                            if not problem['final']:
                                for atB in cmd.get_model(constraintB.atoms['final'].getID()).atom:
                                    if atA.index==atB.index:
                                        problem['final']=1
                                        break
                            else:
                                break
                        for atA in cmd.get_model(constraintA.atoms[orderInit].getID()).atom:
                            if not problem['init']:
                                for atB in cmd.get_model(constraintB.atoms['init'].getID()).atom:
                                    if atA.index==atB.index:
                                        problem['init']=1
                                        break
                            else:
                                break
    if problem['final']==1 and problem['init']==1:
        return 1
    else:
        return 0

