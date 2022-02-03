from bpmsim.start import start
from bpmsim.activity import activity
from bpmsim.intermediate import intermediate
from bpmsim.XORsplit import XORsplit
from bpmsim.XORjoin import XORjoin
from bpmsim.ANDsplit import ANDsplit
from bpmsim.ANDjoin import ANDjoin
from bpmsim.end import end
from bpmsim.resources import resource, store

import xml.etree.ElementTree as ET

def importSubprocess(model, subprocess, first, outgoing, incoming, startBPMN, names):
    # Save incoming and outoging sequuence flows of subprocess and add them later to the start event
    # and the end event of the subprocess
    firstIn = incoming
    lastOut = outgoing
    
    # BPMN to save all Python objects of the elements of the subproces
    BPMN = []
    
    # Count to check if the subprocess had only one start event
    count = 0
    
    # Add start event of the subprocess to BPMN
    for child in subprocess:
        # event = type of the event (start, activity, ...)
        event = child.tag.split("}")[1]
        name = child.get('name')
        if name != None:
            # Remove enter in name
            name = name.replace('\n',' ')
        if event == "startEvent":
            # Check if name is unique
            if name not in names:
                names.append(name)
            else:
                print("There are multiple elements with the name '%s' in your model.\
                      Please make sure every element has a unique name." % name)
                return(None,None)
            # Save outgoing sequence flows
            outgoing = []
            for elem in child.findall(first + "outgoing"):
                outgoing.append(elem.text)
            # Start evnet can only have one outgoing sequence flow
            if len(outgoing) > 1:
                print("A start event can only have one outgoing sequence flow.\
                      Please model splits with XOR or AND.")
                return(None,None)
            # Add incoming sequence flows of subprocess to start event
            incoming = firstIn
            # Save start event as intermediate event
            elem = intermediate(model=model, name=name, previousElement=startBPMN, 
                            outgoing=outgoing, incoming=incoming, imp=True)
            BPMN.append(elem)
            count += 1
    
    # Check if subprocess has only one start event
    if count > 1:
        print("There is more than one start event in one of the subprocesses.\
              Please make sure all your subprocess have only one start event.")
        return(None,None)
    
    # Add the other elements of the subprocess to BPMN
    for child in subprocess:
        # event = type of the event (start, activity, ...)
        event = child.tag.split("}")[1]
    
        # Only activites, intermediate events, AND, XOR and end events are added
        if event in ("task","intermediateThrowEvent","intermediateCatchEvent",
                     "parallelGateway","exclusiveGateway","endEvent","subProcess"):
            name = child.get('name')
            if name != None:
                # Remove enters in name
                name = name.replace('\n',' ')
            # Check if name is unique
            if name not in names:
                names.append(name)
            else:
                print("There are multiple elements with the name '%s' in your model.\
                      Please make sure every element has a unique name." % name)
                return(None,None)
            
            # Direction = gateway parameter to define if it is a split or a join
            direction = child.get('gatewayDirection')
            
            # Save outgoing and incoming sequence flows
            outgoing = []
            for elem in child.findall(first + "outgoing"):
                outgoing.append(elem.text)
            incoming = []
            for elem in child.findall(first + "incoming"):
                incoming.append(elem.text)
            
            # Only gateways can have more than one incoming or outogoing sequence flow
            if event in ("task","intermediateThrowEvent","intermediateCatchEvent",
                         "endEvent","subProcess"):
                if len(incoming) > 1:
                    print("Element '%s' has multiple incoming sequences flows.\
                          Please model joins with XOR or AND." % name)
                    return(None,None)
                if len(outgoing) > 1:
                    print("Element '%s' has multiple outgoing sequences flows.\
                          Please model splits with XOR or AND." % name)
                    return(None,None)
            
            # Check event type and make corresponding Python object
            if event == "task":
                elem = activity(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "intermediateThrowEvent":
                elem = intermediate(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "intermediateCatchEvent":
                elem = intermediate(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "parallelGateway":
                if direction == "Diverging":
                    if len(outgoing) > 10:
                        print("ANDsplits can maximally have 10 branches.")
                        return(None,None)
                    else:
                        elem = ANDsplit(model=model, name=name, previousElement=BPMN[0], 
                                        outgoing=outgoing, incoming=incoming, imp=True)
                        BPMN.append(elem)
                elif direction == "Converging":
                    elem = ANDjoin(model=model, name=name, previousElements=[BPMN[0]], 
                                   outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
            elif event == "exclusiveGateway":
                if direction == "Diverging":
                    elem = XORsplit(model=model, name=name, previousElement=BPMN[0], 
                                    outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
                elif direction == "Converging":
                    elem = XORjoin(model=model, name=name, previousElements=[BPMN[0]], 
                                   outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
            elif event == "endEvent":
                outgoing = lastOut
                elem = intermediate(model=model, name=name, previousElement=startBPMN, 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            
            # Add elements of subprocess
            elif event == "subProcess":
                names.remove(name)
                sub,names = importSubprocess(model, child, first, outgoing, incoming, BPMN[0], names)
                # Check if elements of subprocess are correctly added,
                # otherwise exit function
                if sub == None:
                    return(None,None)
                for s in sub:
                    BPMN.append(s)
                
    return(BPMN,names)

def importBPMN(modelName, fileName, withSubprocess=False, outputHelp=False):
    # read in xml file
    tree = ET.parse(fileName)
    root = tree.getroot()
    # get first part of tag to add in later steps
    first = root.tag.split("}")[0]+"}"
    
    # Gather all information of the process
    processes = []
    for ro in root.findall(first + "process"):
        processes.append(ro)
    
    # Save process information in a list
    process = []
    for pro in processes:
        for child in pro:
            process.append(child)
    
    # BPMN list to save all elements of model
    # names list to check is all names are unique
    model = modelName
    BPMN = []
    names = []
    
    # Count to check if model has only one start event
    count = 0
    
    # Find start event of model
    for child in process:
        # event = type of the event (start, activity, ...)
        event = child.tag.split("}")[1]
        name = child.get('name')
        if name != None:
            # remove enters in name
            name = name.replace('\n',' ')
        if event == "startEvent":
            names.append(name)
            # Save outoging sequence flows
            outgoing = []
            for elem in child.findall(first + "outgoing"):
                outgoing.append(elem.text)
            # Check if start event has only one outoging sequence flow
            if len(outgoing) > 1:
                print("Element '%s' has multiple outgoing sequences flows.\
                      A start event can only have one outgoing sequence flow.\
                      Please model splits with XOR or AND." % name)
                return
            # Add start event to BPMN list
            elem = start(model=model, name=name, outgoing=outgoing, imp=True)
            BPMN.append(elem)
            count += 1
    
    if count > 1:
        print("There can only be one start event. Please make sure your model\
              does not have more than one start event.")
        return
    
    # Add other elements of model to BPMN list
    for child in process:
        # event = type of the event (start, activity, ...)
        event = child.tag.split("}")[1]
        # Only activites, intermediate events, AND, XOR and end events are added
        if event in ("task","intermediateThrowEvent","intermediateCatchEvent",
                     "parallelGateway","exclusiveGateway","endEvent","subProcess"):
            name = child.get('name')
            if name != None:
                # remove enter in name
                name = name.replace('\n',' ')
            # Check is name is unique, otherwise exit function
            if name not in names:
                names.append(name)
            else:
                print("There are multiple elements with the name '%s' in your model.\
                      Please make sure every element has a unique name." % name)
                return
            
            # Direction = parameter of gateways (to define if it's a spli or a join)
            direction = child.get('gatewayDirection')
            # Save outgoing sequence flows
            outgoing = []
            for elem in child.findall(first + "outgoing"):
                outgoing.append(elem.text)
            # Save incoming sequence flows
            incoming = []
            for elem in child.findall(first + "incoming"):
                incoming.append(elem.text)
            
            # Only gateways can have more than one incoming or outoging sequence flow
            if event in ("task","intermediateThrowEvent","intermediateCatchEvent",
                         "endEvent","subProcess"):
                if len(incoming) > 1:
                    print("Element '%s' has multiple incoming sequences flows.\
                          Please model joins with XOR or AND." % name)
                    return
                if len(outgoing) > 1:
                    print("Element '%s' has multiple outgoing sequences flows.\
                          Please model splits with XOR or AND." % name)
                    return
            
            # Check event type and make corresponding Python object
            if event == "task":
                elem = activity(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "intermediateThrowEvent":
                elem = intermediate(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "intermediateCatchEvent":
                elem = intermediate(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            elif event == "parallelGateway":
                if direction == "Diverging":
                    if len(outgoing) > 10:
                        print("ANDsplits can maximally have 10 branches.")
                        return
                    else:
                        elem = ANDsplit(model=model, name=name, previousElement=BPMN[0], 
                                        outgoing=outgoing, incoming=incoming, imp=True)
                        BPMN.append(elem)
                elif direction == "Converging":
                    elem = ANDjoin(model=model, name=name, previousElements=[BPMN[0]], 
                                   outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
            elif event == "exclusiveGateway":
                if direction == "Diverging":
                    elem = XORsplit(model=model, name=name, previousElement=BPMN[0], 
                                    outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
                elif direction == "Converging":
                    elem = XORjoin(model=model, name=name, previousElements=[BPMN[0]], 
                                   outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
            elif event == "endEvent":
                elem = end(model=model, name=name, previousElement=BPMN[0], 
                           outgoing=outgoing, incoming=incoming, imp=True)
                BPMN.append(elem)
            
            # If subprocess and withSuprocess == True, add elements of subprocess
            # Otherwise add subprocess as activity
            elif event == "subProcess":
                if not withSubprocess:
                    elem = activity(model=model, name=name, previousElement=BPMN[0], 
                                outgoing=outgoing, incoming=incoming, imp=True)
                    BPMN.append(elem)
                else:
                    # As the the elements of the subporcess will be added, it is not important
                    # that the subprocess name is unique
                    names.remove(name)
                    # Extract Python objects and names of the elements of the subprocess
                    sub, names = importSubprocess(modelName, child, first, outgoing, incoming, BPMN[0], names)
                    # Check if elements of subprocess are correctly added,
                    # otherwise exit function
                    if sub == None:
                        return
                    for s in sub:
                        BPMN.append(s)
    
    # Function to retrieve next element
    def getElement(inc):
        for elem in BPMN:
            for out in elem.getOutgoing():
                if out == inc:
                    return(elem)
    
    # Set right elemetn in the previousElement parameter of all elements in BPMN list,
    # Currently the start event is added to every element as previousElement               
    for elem in BPMN:
        prev = []
        for inc in elem.getIncoming():
            prev.append(getElement(inc))
        elem.setPrevious(prev)
    
    # Give information to user on how to procees if outputHelp is True
    if outputHelp:
        streepjes = "-----------"
        for i in range(len(modelName)):
            streepjes += "-"
        print('#----------'+streepjes+'----------#')
        print('#----------SIMULATION '+modelName.upper()+'----------#')
        print('#----------'+streepjes+'----------#')
        
        print("")
        print("# CREATE RESOURCES")
        print('resource1 = bpmsim.resource(name="", capacity=5)')
        print('resource2 = bpmsim.resource(name="", capacity=2)')
        print('store1 = bpmsim.store(name="", capacity=20, initial=5)')
        print('store2 = bpmsim.store(name="", capacity=30, initial=0)')
        
        print("")
        print("# SET START")
        for elem in BPMN:
            if elem.__class__.__name__ == "start":
                print('bpmsim.setStart(BPMN=, name="'+elem.getName()+'", getStore=[])')
        
        print("")
        print("# SET ACTIVITIES")
        for elem in BPMN:
            if elem.__class__.__name__ == "activity":
                print('bpmsim.setActivity(BPMN=, name="'+elem.getName()+'", resources=[], amount=[], duration=lambda: 0, fixedCost=0, variableCost=0, priority=0, getStore=[], putStore=[])')
        
        print("")
        print("# SET INTERMEDIATE EVENTS")
        for elem in BPMN:
            if elem.__class__.__name__ == "intermediate":
                print('bpmsim.setIntermediate(BPMN=, name="'+elem.getName()+'", duration=lambda: 0, getStore=[], putStore=[])')
        
        print("")
        print("# SET END")
        for elem in BPMN:
            if elem.__class__.__name__ == "end":
                print('bpmsim.setEnd(BPMN=, name="'+elem.getName()+'", putStore=[])')
        
        print("")
        print("# SET XOR SPLIT")
        for elem in BPMN:
            if elem.__class__.__name__ == "XORsplit":
                split = elem.getName()
                following = []
                for nextEl in BPMN:
                    for prev in nextEl.getPreviousElement():
                        if prev == elem:
                            following.append(nextEl.getName())
                number = len(following)
                numbers = []
                for i in range(number):
                    numbers.append(str(100/number))
                print('bpmsim.setXORsplit(BPMN=, name="'+split+'", nextElementsNames=['+'"'+'","'.join(following)+'"'+'], probabilities=['+','.join(numbers)+'])')
        
        print("")
        print("# CREATE INSTANCES")
        instancesName = "instances"+modelName.replace(" ","")
        print('#'+instancesName+' = bpmsim.createInstancesFixed("'+modelName+'", startTime=0, time=None, number=None, interval=None)')
        print('#'+instancesName+' = bpmsim.createInstanceDistribution("'+modelName+'", time=0, number=0, distribution=lambda:0, between01=False, normalize=False)')
        print('#'+instancesName+' = bpmsim.createInstancesInterDistribution("'+modelName+'", startTime=0, time=None, number=None, interval=lambda:0)')
        
        print("")
        print('#-------------------------------------#')
        print('#----------SIMULATION MODELS----------#')
        print('#-------------------------------------#')
        
        print("")
        print("# SET SIMULATION PARAMETERS")
        print("# If you want to simulate MULTIPLE models simaltaneously, add ALL instances, resources and stores of ALL models here.")
        print('sim = bpmsim.simulation(instances=['+instancesName+'], resources=[resource1,resource2], stores=[store1,store2])')
        
        print("")
        print("# OUTPUT")
        print('sim.simulation(output=True, fileName="C:/........../filename")')
        print('sim.simInfo(fileName="C:/........../filename")')
        print('sim.simPlot(fileName="C:/........../filename")')
              
    return(BPMN)

# Function to set additional parameter of activities
def setActivity(BPMN, name, resources=[], amount=[], duration=lambda:0, fixedCost=0,
                variableCost=0, priority=0, getStore=[], putStore=[]):
    # Check if element is a part of BPMN and if it is an activity
    inBPMN=False
    for elem in BPMN:
        if elem.getName() == name:
            inBPMN = True
            if elem.__class__.__name__ == "activity":
                elem.setActivity(resources=resources, amount=amount,
                                 duration=duration, fixedCost=fixedCost,
                                 variableCost=variableCost, priority=priority,
                                 getStore=getStore, putStore=putStore)
            else:
                print("The element with the name '%s' is not an activity." %
                      name)
    if not inBPMN:
        print("There is no activity with the name '%s'." % name)
        print("The model contains following activities: ")
        for elem in BPMN:
            if elem.__class__.__name__ == "activity":
                print(elem.getName())

# Function to set additional parameters of intermediate events
def setIntermediate(BPMN, name, duration=lambda:0, getStore=[], putStore=[]):
    # Check if element is a part of BPMN and if it is an intermediate event
    inBPMN=False
    for elem in BPMN:
        if elem.getName() == name:
            inBPMN = True
            if elem.__class__.__name__ == "intermediate":
                elem.setIntermediate(duration=duration, getStore=getStore, putStore=putStore)
            else:
                print("The element with the name '%s' is not an intermediate event." %
                      name)
    if not inBPMN:
        print("There is no intermediate event with the name '%s'." % name)
        print("The model contains following intermediate events: ")
        for elem in BPMN:
            if elem.__class__.__name__ == "intermediate":
                print(elem.getName())

# Function to set additional parameters of start events
def setStart(BPMN, name, getStore=[]):
    # Check if element is a part of BPMN and if it is a start event
    inBPMN=False
    for elem in BPMN:
        if elem.getName() == name:
            inBPMN = True
            if elem.__class__.__name__ == "start":
                elem.setStart(getStore=getStore)
            else:
                print("The element with the name '%s' is not a start event." %
                      name)
    if not inBPMN:
        print("There is no start event with the name '%s'." % name)
        print("The model contains following start events: ")
        for elem in BPMN:
            if elem.__class__.__name__ == "start":
                print(elem.getName())

# Function to set additional parameters of end events
def setEnd(BPMN, name, putStore=[]):
    # Check if element is a part of BPMN and if it is an end event
    inBPMN=False
    for elem in BPMN:
        if elem.getName() == name:
            inBPMN = True
            if elem.__class__.__name__ == "end":
                elem.setEnd(putStore=putStore)
            else:
                print("The element with the name '%s' is not an end event." %
                      name)
    if not inBPMN:
        print("There is no end event with the name '%s'." % name)
        print("The model contains following end events: ")
        for elem in BPMN:
            if elem.__class__.__name__ == "end":
                print(elem.getName())

# Function to retrieve next element
def getElement(BPMN, elementName):
    inBPMN = False
    for elem in BPMN:
        if elem.getName()==elementName:
            inBPMN = True
            return(elem)
    if not inBPMN:
        print("There is no element with the name '%s'." % elementName)
        print("The model contains following elements: ")
        for elem in BPMN:
            print(elem.getName())
        return(None)

# Function to retireve next elements
def getNextElements(BPMN, elementsNames):
    nextElements = []
    for nextElem in elementsNames:
        new = getElement(BPMN, nextElem)
        if new != None:
            nextElements.append(new)
    return(nextElements)

# Function to set branching probabilities of XORsplit
def setXORsplit(BPMN, name, nextElementsNames, probabilities):
    # Check if element is a part of BPMN and if it is an XORsplit
    inBPMN=False
    if type(nextElementsNames) != list:
        print("'nextElementsNames' should be a list.")
    else:
        for elem in BPMN:
            if elem.getName() == name:
                inBPMN=True
                if elem.__class__.__name__ == "XORsplit":
                    nextElements = getNextElements(BPMN, nextElementsNames)
                    if len(nextElementsNames) == len(nextElements):
                        elem.setXORsplit(nextElements=nextElements, probabilities=probabilities)
                else:
                    print("The element with the name '%s' is not an XORsplit." %
                          name)
        if not inBPMN:
            print("There is no XORsplit with the name '%s'." % name)
            print("The model contains following XORsplits: ")
            for elem in BPMN:
                if elem.__class__.__name__ == "XORsplit":
                    print(elem.getName())