from bpmsim.element import element
#import scipy.stats
#import numpy

class activity(element):
    def __init__(self, model, name, previousElement, outgoing=[], incoming=[], imp=False):
        if imp:
            # If fuction called in import_BPMN
            self.model = model
            self.elements[model].append(self)
            self.name = name
            self.previous = [previousElement]
            self.duration = None
            self.outgoing = outgoing
            self.incoming = incoming
        else:
            # Check if everything is added correctly if not called in import_BPMN
            if not (type(model)==str and type(name)==str):
                print("Model and Name should be strings.")
            elif model not in self.elements:
                print("Before adding activities to this model, you should first \
                      add a start event.")
            elif type(previousElement) == list:
                print("PreviousElement should not be a list. Use XOR and AND to \
                      make splits and joins.")
            elif previousElement not in self.elements[model]:
                print("PreviousElement is not an element of model %s." % model)
                print("Please first define the previous element or set\
                      previousElement equal to an element you already defined.")
            elif previousElement.__class__.__name__ == "end":
                print("Previous element is of type 'end'. This is not possible.")
            else:
                stop = False
                if previousElement.__class__.__name__ == "start" or \
                    previousElement.__class__.__name__ == "activity" or \
                    previousElement.__class__.__name__ == "intermediate" or \
                    previousElement.__class__.__name__ == "XORjoin" or \
                    previousElement.__class__.__name__ == "ANDjoin":
                    for elem in self.elements[model]:
                        if elem.getPreviousElement() == [previousElement]:
                            print("The element '%s' already has '%s' as previous \
                                  element." % (elem.getName(), previousElement.getName()))
                            stop = True
                for elem in self.elements[model]:
                    if elem.getName() == name:
                        print("You already added an activity with the name '%s' \
                              to the model '%s'." % (name, model))
                        print("The old element will be deleted.")
                        self.elements[model].remove(elem)
                        stop = False
                if not stop:
                    self.model = model
                    self.elements[model].append(self)
                    self.name = name
                    self.previous = [previousElement]
                    self.duration = None
    
    # Set additional parameters of activity
    def setActivity(self, resources=[], amount=[], duration=lambda:0, fixedCost=0,
                    variableCost=0, priority=0, getStore=[], putStore=[]):
        # If preemptive resources would de added, this should be added in parameters of function.
        # right now this does not yet functions
        preempt = False
        
        # Check if all input values are correct
        stop = False
        try:
            dur = duration()
            try:
                dur += 0
            except:
                print("The function in duration does not return a number.")
                stop = True
        except:
            print("Wrong input for duration. '%s' is not a function." % str(duration))
            stop = True  

        if not stop:
            if type(resources) != list or type(amount) != list:
                print("Please enter a list of resources and the amount you need \
                      of every resource in the variables 'resources' and \
                      'amount'. If you don't need any resources enter an empty list.")
            elif len(resources) != len(amount):
                print("Please enter as much elements in the variable resources \
                      as in the variable amount.")
            elif type(getStore) != list:
                print("Please enter a list of stores in getStore. If you don't \
                      need stores enter an empty list.")
            elif type(putStore) != list:
                print("Please enter a list of stores in putStore. If you don't \
                      need stores enter an empty list.")
            elif type(fixedCost) not in (int, float, complex):
                print("Fixed Cost should be a number.")
            elif type(variableCost) not in (int, float, complex):
                print("Variable Cost should be a number.")
            else:
                # If everything is correct, set parameters
                self.resourcesString = []
                for res in range(len(resources)):
                    for i in range(amount[res]):
                        self.resourcesString.append(resources[res])
                self.getStoreString = getStore
                self.putStoreString = putStore
                self.priority = priority
                self.preempt = preempt
                self.duration = duration
                self.fixedCost = fixedCost
                self.variableCost = variableCost
    
    def setResources(self, resources):
        self.resources = resources
    def setGetStore(self, stores):
        self.getStore = stores
    def setPutStore(self, stores):
        self.putStore = stores
    
    # Simulate avtivity
    def runActivity(self, environment, inst, log, inter):
        # Start waiting for resources
        startWaiting = environment.now
        
        # Request resources and stores
        useList = []        
        for res in self.resources:
            useList.append(res.request(priority=self.priority, preempt = self.preempt))
        for use in useList:
            yield use
        for sto in self.getStore:
            yield sto.get()
        
        # Start process (resources are acquired)
        startProcess = environment.now
        
        # Define waiting time
        waiting = startProcess - startWaiting
        #count = 0
        
        # Define actiity duraiton
        dur = self.duration()
        # duration should not be negative
        while dur < 0:
            dur = self.duration()
        
        # Put activity in sleeping mode
        yield environment.timeout(dur)
        
        # Preemption: not yet added: wrong order of activities...
# =============================================================================
#         durCount = dur
#         while durCount > 0:
#             try:
#                 start = environment.now
#                 print("Start Process " + inst.getInstName() + " " + self.getName() + " " + str(environment.now))
#                 yield environment.timeout(durCount)
#                 durCount = 0
#             except inter as interrupt:
#                 for i in range(len(self.resources)):
#                     self.resources[i].release(useList[i])
#                 count += 1
#                 print("Interrupted " + inst.getInstName() + " " + self.getName() + " " + str(environment.now))
#                 usage = environment.now - start
#                 durCount = durCount - usage
#                 startWaitingInter = environment.now
#                 useList = []
#                 for res in self.resources:
#                     useList.append(res.request(priority=self.priority, preempt = self.preempt))
#                 for use in useList:
#                     yield use
#                 startProcess = environment.now
#                 wait = startProcess - startWaitingInter
#                 waiting += wait
# =============================================================================
        
        # End of process
        endProcess = environment.now
        
        # Release stores and resources
        for sto in self.putStore:
            yield sto.put("item")
        for i in range(len(self.resources)):
            self.resources[i].release(useList[i])
        
        # Define waiting time to put store
        end = environment.now
        waiting2 = end-endProcess
        waiting = waiting + waiting2
        
        # Retrieve names of resources and stores to add to logs
        nameRes = ""
        for res in self.resourcesString:
            nameRes = nameRes + res.getName() + ","
        if len(nameRes) > 0:
            nameRes = nameRes[:-1]
            
        nameGetSto = ""
        for sto in self.getStoreString:
            nameGetSto = nameGetSto + sto.getName() + ","
        if len(nameGetSto) > 0:
            nameGetSto = nameGetSto[:-1]
            
        namePutSto = ""
        for sto in self.putStoreString:
            namePutSto = namePutSto + sto.getName() + "," 
        if len(namePutSto) > 0:
            namePutSto = namePutSto[:-1]
        
        # Define variable cost
        variable = self.variableCost * dur
        
# =============================================================================
#         data = [inst.getInstModel(), inst.getInstName(), 'activity', self.name,
#                 startWaiting, end, waiting, dur, count, 
#                 self.fixedCost, variable, nameRes, nameGetSto, namePutSto]
# =============================================================================
        
        # Add information to logs
        data = [inst.getInstModel(), inst.getInstName(), 'activity', self.name,
                startWaiting, startProcess, end, waiting, dur, 
                self.fixedCost, variable, nameRes, nameGetSto, namePutSto]
        log.append(data)

    def getResources(self):
        return(self.resources)
    def getPriority(self):
        return(self.priority)
    def getPreempt(self):
        return(self.preempt)
    def getGetStore(self):
        return(self.getStore)
    def getPutStore(self):
        return(self.putStore)
    def getDuration(self):
        return(self.duration)
    def getFixedCost(self):
        return(self.fixedCost)
    def getVariableCost(self):
        return(self.variableCost)
    def getResourcesString(self):
        return(self.resourcesString)
    def getGetStoreString(self):
        return(self.getStoreString)
    def getPutStoreString(self):
        return(self.putStoreString)