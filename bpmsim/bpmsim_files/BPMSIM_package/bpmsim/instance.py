from bpmsim.element import element
from bpmsim.start import start
from bpmsim.activity import activity
from bpmsim.intermediate import intermediate
from bpmsim.XORsplit import XORsplit
from bpmsim.XORjoin import XORjoin
from bpmsim.ANDsplit import ANDsplit
from bpmsim.ANDjoin import ANDjoin

from random import randint
import numpy
#import scipy.stats

def createInstancesFixed(model, startTime=0, time=None, number=None, interval=None):
    # Check if entered values are correct
    listInst = []
    stop = False
    if type(model) != str:
        print("Model should be a string.")
        stop=True
    try:
        startTime += 0
        if startTime < 0:
            print("startTime can't be negative.")
            stop=True
    except:
        print("startTime should be a number.")
        stop = True
    if time !=None:
        try:
            time += startTime
            if time < 0:
                print("Time can't be negative.")
                stop=True
        except:
            print("Time should be a number.")
            stop = True
    if number !=None:
        try:
            number += 0
            if number < 0:
                print("Number can't be negative.")
                stop=True
        except:
            print("Number should be a number.")
            stop = True
    if interval !=None:
        try:
            interval += 0
            if interval < 0:
                print("Interval can't be negative.")
                stop=True
        except:
            print("Interval should be a number.")
            stop = True
    
    # If everything is correctly added, create instances
    if not stop:
        instStartTime = startTime
        
        # Create instances with parameters time and interval
        if number==None and time!=None and interval!=None:           
            for i in range(time): 
                if instStartTime<=time:
                    listInst.append(instance(model, "instance"+str(i+1), instStartTime))
                    instStartTime+=interval
        
        # Create instances with parameters number and interval
        elif time==None and number!=None and interval!=None:
            for i in range(number):
                listInst.append(instance(model, "instance"+str(i+1), instStartTime))
                instStartTime+=interval
        
        # Create instances with parameters time and number
        elif interval == None and time!=None and number!=None:          
            interval = float(time)/float(number-1)
            for i in range(number):
                listInst.append(instance(model, "instance"+str(i+1), instStartTime))
                instStartTime+=interval
        
        # Only two of three parameters (number, time, interval) should be set
        else:
            print("Wrong input. Please input 2 of the following:\
                  occurence time, instance numbers or interval time.")
    
    return(listInst)

def createInstanceDistribution(model, time=0, number=0, distribution=lambda:0, between01=False, normalize=False):
    # Check if entered values are correct
    returnList=[]
    stop = False
    if type(model) != str:
        print("Model should be a string.")
        stop=True
    elif type(between01) != bool:
        print("Between01 should be a boolean.")
    elif type(normalize) != bool:
        print("Normalize should be a boolean.")
    elif between01 == True and normalize == True:
        print("Between01 and Normalize cannot both be True.")
    else:
        try:
            dur = distribution()
            try:
                dur += 0
            except:
                print("The function in distribution does not return a number.")
                stop = True
        except:
            print("Wrong input for distribution. '%s' is not a function." % str(distribution))
            stop = True 
        try:
            number += 0
            if number < 0:
                print("Number can't be negative.")
                stop=True
        except:
            print("Number should be a number.")
            stop=True
        
        try:
            time += 0
            if between01 or normalize:
                if time <= 0:
                    print("Time should be higher than zero. \
                          Ohterwise start time of all instances will be zero.")
                    stop=True
        except:
            print("Time should be a number.")
            stop=True
    
    # If everything is correctly added, create instances
    if not stop:
        listInst = []
        
        # If numbers should be normalized
        if normalize:
            # As the first and last number will be zero and one afther the normalization,
            # add two extra numbers and delete the first and the last after the normalization
            # Sample duraiton
            for i in range(number+2):
                dur = distribution()
                listInst.append(dur)
            # Normalize values
            normalizedList = (numpy.array(listInst) - numpy.min(listInst)) / (numpy.max(listInst) - numpy.min(listInst))
            # Sort values so smallest number (the first instance) is first
            normalizedList.sort()
            # Delete first and last element
            normalizedList = normalizedList[1:-1]
            # Multiply with time to acquire start time of instances
            listInst = numpy.array(normalizedList) * time
        else:
            # sample duration
            for i in range(number):
                dur = distribution()
                # duration cannot be negative
                while dur < 0:
                    dur = distribution()
                listInst.append(dur)
            # Multiply with time if between zero and one
            if between01:
                listInst = numpy.array(listInst) * time
            listInst.sort()
        
        # Create instances
        for i in range(len(listInst)):
            returnList.append(instance(model, "instance"+str(i+1), listInst[i]))
    return(returnList)

def createInstancesInterDistribution(model, startTime=0, time=None, number=None, interval=lambda:0):
    # Check if entered values are correct
    returnList=[]
    stop = False
    if type(model) != str:
        print("Model should be a string.")
        stop=True
    else:
        try:
            dur = interval()
            try:
                dur += 0
            except:
                print("The function in interval does not return a number.")
                stop = True
        except:
            print("Wrong input for interval. '%s' is not a function." % str(interval))
            stop = True 
        try:
            startTime+=0
            if startTime < 0:
                print("startTime can't be negative.")
                stop=True
        except:
            print("InstStart should be a number.")
            stop=True
        if time!=None:
            try:
                time+=startTime
                if time < 0:
                    print("Time can't be negative.")
                    stop=True
            except:
                print("Time should be a number.")
                stop=True
        if number!=None:
            try:
                number+=0
                if number < 0:
                    print("Number can't be negative.")
                    stop=True
            except:
                print("Number should be a number.")
                stop=True
    
    # If everything is coorectly entered, create instances
    if not stop:
        # Create instances with number
        if time==None and number!=None:
            for i in range(number):
                returnList.append(instance(model, "instance"+str(i+1), startTime))
                # sample interval from inputed distribution
                inter = interval()
                startTime += inter
                
        # Create instances with time
        elif time!=None and number==None:
            i=0
            while startTime <= time:
                returnList.append(instance(model, "instance"+str(i+1), startTime))
                # sample interval from inputed distribution
                inter = interval()
                startTime += inter
                i+=1
        
        # Only two of both parameters (time and number) can be set
        else:
            print("Wrong input. Please input 1 of the following:\
                  occurence time or instance numbers.")
    
    return(returnList)

class instance():
    def __init__(self, model, name, startTime):
        self.InstModel = model
        self.InstName = name
        self.InstStart = startTime
    
    def getInstModel(self):
        return(self.InstModel)
    def getInstName(self):
        return(self.InstName)
    def getInstStart(self):
        return(self.InstStart)
    
    def getElements(self):
        return(element.elements[self.getInstModel()])
    
    # Retrieve start event of elements
    def getStart(self):
        for elem in self.getElements():
            if elem.__class__.__name__ == "start":
                return(elem)
    
    # Retrieve the next element
    def getNextElement(self, previousElement):
        if previousElement.__class__.__name__ == "XORsplit":
            XORlist = []
            for item in previousElement.getNextElements().items():
                for i in range(item[1]):
                    XORlist.append(item[0])
            random = randint(0,len(XORlist)-1)
            return(XORlist[random])
        elif previousElement.__class__.__name__ == "ANDsplit":
            nextElements = []
            for elem in self.getElements():
                for prev in elem.previous:
                    if previousElement == prev:
                        nextElements.append(elem)
            return(nextElements)
        else:
            for elem in self.getElements():
                for prev in elem.previous:
                    if previousElement == prev:
                        return(elem)
    
    # Retrieve last element of ANDlist
    def getLastElement(self, lst):
        last = lst[-1]
        if type(last) == list:
            return(self.getLastElement(last))
        else:
            return(last)
    
    # Retrieve the belonging join element of an ANDsplit
    def getJoin(self, previousElement):
        for elem in self.getElements():
            if elem.__class__.__name__ == "ANDjoin":
                for prev in elem.previous:
                    if previousElement == prev:
                        return(elem)
                
     # Retrieve all elements of the branches of the ANDsplit                   
    def getANDlist(self, newElement):
        tree = []
        tree.append(newElement)
        for elem in self.getNextElement(newElement):
            branch = []
            newElem = elem
            while(newElem != None):
                if newElem.__class__.__name__ == "ANDjoin":
                    break
                elif newElem.__class__.__name__ == "ANDsplit":
                    newList = self.getANDlist(newElem)
                    branch.append(newList)
                    newElem = self.getNextElement(self.getLastElement(branch))
                else:
                    branch.append(newElem)
                    newElem = self.getNextElement(newElem)
            tree.append(branch)
        tree.append(self.getJoin(self.getLastElement(tree)))
        return(tree)
    
    # Simulate the branches of an ANDsplit so they are simulataneously processed
    def runList(self, env, branch, log, inter):
        lastPartBranch = []
        for elem in branch:
            if type(elem) != list:
                if elem.__class__.__name__ == "ANDsplit":
                    branch.remove(elem)
                elif elem.__class__.__name__ == "ANDjoin":
                    indexJoin =  branch.index(elem)
                    lastPartBranch = branch[indexJoin:]
                    branch = branch[:indexJoin]
        count = len(branch)
        if count == 1:
            yield env.process(self.runBranch(env, branch[0], log, inter))
        elif count == 2:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter))
        elif count == 3:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter))
        elif count == 4:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter))
        elif count == 5:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter))
        elif count == 6:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter)) & \
            env.process(self.runBranch(env, branch[5], log, inter))
        elif count == 7:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter)) & \
            env.process(self.runBranch(env, branch[5], log, inter)) & \
            env.process(self.runBranch(env, branch[6], log, inter))
        elif count == 8:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter)) & \
            env.process(self.runBranch(env, branch[5], log, inter)) & \
            env.process(self.runBranch(env, branch[6], log, inter)) & \
            env.process(self.runBranch(env, branch[7], log, inter))
        elif count == 9:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter)) & \
            env.process(self.runBranch(env, branch[5], log, inter)) & \
            env.process(self.runBranch(env, branch[6], log, inter)) & \
            env.process(self.runBranch(env, branch[7], log, inter)) & \
            env.process(self.runBranch(env, branch[8], log, inter))
        elif count == 10:
            yield env.process(self.runBranch(env, branch[0], log, inter)) & \
            env.process(self.runBranch(env, branch[1], log, inter)) & \
            env.process(self.runBranch(env, branch[2], log, inter)) & \
            env.process(self.runBranch(env, branch[3], log, inter)) & \
            env.process(self.runBranch(env, branch[4], log, inter)) & \
            env.process(self.runBranch(env, branch[5], log, inter)) & \
            env.process(self.runBranch(env, branch[6], log, inter)) & \
            env.process(self.runBranch(env, branch[7], log, inter)) & \
            env.process(self.runBranch(env, branch[8], log, inter)) & \
            env.process(self.runBranch(env, branch[9], log, inter))
        yield env.process(self.runBranch(env, lastPartBranch, log, inter))
    
    # Simulate a branch of an ANDsplit
    def runBranch(self, env, branch, log, inter):
        if type(branch) == list:
            for elem in branch:
                if elem.__class__.__name__ == "activity":
                    yield env.process(elem.runActivity(env, self, log, inter))
                elif elem.__class__.__name__ == "intermediate":
                    yield env.process(elem.runIntermediate(env, self, log))
                elif elem.__class__.__name__ == "ANDsplit":
                    i = branch.index(elem)
                    partBranch = branch[i:]
                    yield env.process(self.runList(env, partBranch, log, inter))
                    break
                elif elem.__class__.__name__ == "end":
                    yield env.process(elem.runEnd(env, self, log))
                elif type(elem) == list:
                    yield env.process(self.runBranch(env, elem, log, inter))
        else:
            if branch.__class__.__name__ == "activity":
                yield env.process(branch.runActivity(env, self, log, inter))
            elif branch.__class__.__name__ == "intermediate":
                yield env.process(branch.runIntermediate(env, self, log))
            elif branch.__class__.__name__ == "end":
                yield env.process(branch.runEnd(env, self, log))
    
    # Simulate instance
    def runInstance(self, env, log, inter):
        # Simulate start
        st = self.getStart()
        yield env.timeout(self.InstStart)
        yield env.process(st.runStart(env, self, log))
        #self.InstStart = env.now
        newElem = st
        # Simulate other elements following on the start event
        while(newElem != None):
            newElem = self.getNextElement(newElem)
            if newElem.__class__.__name__ == "activity":
                yield env.process(newElem.runActivity(env, self, log, inter))
            elif newElem.__class__.__name__ == "intermediate":
                yield env.process(newElem.runIntermediate(env, self, log))
            elif newElem.__class__.__name__ == "ANDsplit":
                ANDlist = self.getANDlist(newElem)
                yield env.process(self.runList(env, ANDlist, log, inter))
                newElem = self.getLastElement(ANDlist)
            elif newElem.__class__.__name__ == "end":
                yield env.process(newElem.runEnd(env, self, log))