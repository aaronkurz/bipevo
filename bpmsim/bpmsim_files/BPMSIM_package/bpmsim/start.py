from bpmsim.element import element

class start(element):
    def __init__(self, model, name, outgoing=[], incoming=[], imp=False):
        if imp:
            # If fuction called in import_BPMN
            self.model = model
            self.elements[model] = [self]
            self.name = name
            self.previous = []
            self.getStoreString = []
            self.outgoing = outgoing
            self.incoming = incoming
        else:
            # Check if everything is added correctly if not called in import_BPMN
            answer = "no"
            if not (type(model)==str and type(name)==str):
                print("Model and Name should be strings.")
            elif model in self.elements:
                print("You already added a start even to the model '%s'." % model)
                print("Do you want to replace the start event? \
                      If you replace it, all the elements in this model \
                      will be deleted.")
                answer=input("Enter 'yes' or 'no':")
                while not (answer=="yes" or answer=="no"):
                    answer=input("Please answer with 'yes' or 'no'.")
            else:
                answer = "yes"
            if answer=="yes":
                self.model = model
                self.elements[model] = [self]
                self.name = name
                self.previous = []
                self.getStoreString = []
    
    # Set additional parameters of start event
    def setStart(self, getStore=[]):
        if type(getStore) != list:
            print("Please enter a list of stores in getStore. If you don't \
                  need stores enter an empty list.")
        else:
            self.getStoreString = getStore
    
    # Simulate start event
    def runStart(self, environment, inst, log):
        # Request stores
        for sto in self.getStore:
            yield sto.get()
        # Set start and end parameters
        start = environment.now
        startProcess = environment.now
        endProcess = environment.now
        
        # Retrieve names of stores to add to logs
        nameGetSto = ""
        for sto in self.getStoreString:
            nameGetSto = nameGetSto + sto.getName() + ","
        if len(nameGetSto) > 0:
            nameGetSto = nameGetSto[:-1]
        
        # Calculate waiting and process time
        waiting = startProcess-start
        process = endProcess-startProcess
        
# =============================================================================
#         data = [inst.getInstModel(), inst.getInstName(), 'START', self.name,
#                 start, endProcess, waiting, process, 0,
#                 0,0,"", nameGetSto, ""]
# =============================================================================
        
        # Add information to logs
        data = [inst.getInstModel(), inst.getInstName(), 'START', self.name,
                start, startProcess, endProcess, waiting, process,
                0,0,"", nameGetSto, ""]
        log.append(data)
                
    def setGetStore(self, stores):
        self.getStore = stores
    
    def getGetStore(self):
        return(self.getStore)
    
    def getGetStoreString(self):
        return(self.getStoreString)