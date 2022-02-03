from bpmsim.element import element
#import numpy

class intermediate(element):
    def __init__(self, model, name, previousElement, outgoing=[], incoming=[], imp=False):
        if imp:
            # If function called in import_BPMN
            self.model = model
            self.elements[model].append(self)
            self.name = name
            self.previous = [previousElement]
            self.duration = 0
            self.getStoreString = []
            self.putStoreString = []
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
                    self.duration = 0
                    self.getStoreString = []
                    self.putStoreString = []
    
    # Set additional parameters of intermediate event
    def setIntermediate(self, duration=lambda:0, getStore=[], putStore=[]):
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
            if type(getStore) != list:
                print("Please enter a list of stores in getStore. If you don't \
                      need stores enter an empty list.")
            elif type(putStore) != list:
                print("Please enter a list of stores in putStore. If you don't \
                      need stores enter an empty list.")
            else:
                # If everything is correct, set parameters
                self.getStoreString = getStore
                self.putStoreString = putStore
                self.duration = duration
    
    def setResources(self, resources):
        self.resources = resources
    def setGetStore(self, stores):
        self.getStore = stores
    def setPutStore(self, stores):
        self.putStore = stores
    
    # Simulate intermediate event
    def runIntermediate(self, environment, inst, log):
        
        # Start waiting for resources
        start = environment.now
        for sto in self.getStore:
            yield sto.get()
        
        # Define waiting time
        waiting = environment.now - start
        
        # Define start time process
        startProcess = environment.now
        
        # Set duraiton of intermeditate event
        dur = self.duration()
        # duration should not be negative
        while dur < 0:
            dur = self.duration()
            
        yield environment.timeout(dur)
        
        # End time of process
        endProcess = environment.now
        
        for sto in self.putStore:
            yield sto.put("item")
        
        # Define waiting time to put stores
        end = environment.now
        waiting2 = end - endProcess
        waiting = waiting + waiting2
        
        # Retrieve names of stores to add to logs
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
        
        # Define process time of intermediate event
        process = endProcess-startProcess

# =============================================================================
#         data = [inst.getInstModel(), inst.getInstName(), 'intermediate', self.name,
#                 start, end, waiting, process, 0,
#                 0,0,"", nameGetSto, namePutSto]
# =============================================================================
        
        # Add information to logs
        data = [inst.getInstModel(), inst.getInstName(), 'intermediate', self.name,
                start, startProcess, end, waiting, process,
                0,0,"", nameGetSto, namePutSto]
        log.append(data)

    
    def getResources(self):
        return(self.resources)
    def getGetStore(self):
        return(self.getStore)
    def getPutStore(self):
        return(self.putStore)
    def getDuration(self):
        return(self.duration)
    def getResourcesString(self):
        return(self.resourcesString)
    def getGetStoreString(self):
        return(self.getStoreString)
    def getPutStoreString(self):
        return(self.putStoreString)