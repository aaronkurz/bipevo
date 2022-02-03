class element():
    elements = {}
    def __init__(self, model, name, previousElement, outgoing=[], incoming=[]):       
        self.model = model
        self.name = name
        self.previous = [previousElement]
        self.outgoing = outgoing
        self.incoming = incoming
    
    def setPrevious(self, previous):
        self.previous = previous
    
    def getModel(self):
        return(self.model)    
    def getName(self):
        return(self.name)
    def getPreviousElement(self):
        return(self.previous)
    def getOutgoing(self):
        return(self.outgoing)
    def getIncoming(self):
        return(self.incoming)