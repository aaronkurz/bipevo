from bpmsim.element import element

class ANDjoin(element):
    def __init__(self, model, name, previousElements, outgoing=[], incoming=[], imp=False):
        if imp:
            # If function called in import_BPMN
            self.model = model
            self.elements[model].append(self)
            self.name = name
            self.previous = previousElements
            self.outgoing = outgoing
            self.incoming = incoming
            #self.split = None
        else:
            # Check if everything is added correctly if not called in import_BPMN
            correct = False
            if not (type(model)==str and type(name)==str):
                print("Model and Name should be strings.")
            elif model not in self.elements:
                print("Before adding XORsplits to this model, you should first \
                      add a start event.")
            elif type(previousElements) != list:
                print("PreviousElements should be a list.")
            else:
                correct = True
                for elem in previousElements:
                    if elem not in self.elements[model]:
                        correct = False
                        print("'%s' is not an element of model '%s'." %
                              (elem.getName(), model))
                        print("Please first define the previous element or set \
                              previousElement equal to an element you already \
                              defined.")
                    elif elem.__class__.__name__ == "end":
                        correct = False
                        print("Previous element is of type 'end'. This is not possible.")
                    elif elem.__class__.__name__ == "start" or \
                        elem.__class__.__name__ == "activity" or \
                        elem.__class__.__name__ == "intermediate" or \
                        elem.__class__.__name__ == "XORjoin" or \
                        elem.__class__.__name__ == "ANDjoin":
                        for el in self.elements[model]:
                            if el.getPreviousElement() == [elem]:
                                print("The element '%s' already has '%s' as previous \
                                      element." % (el.getName(), elem.getName()))
                                correct = False
                for elem in self.elements[model]:
                    if elem.getName() == name:
                        print("You already added an element with the name '%s' \
                              to the model '%s'." % (name, model))
                        print("If you want to add an element to this ANDjoin, \
                              please use the function 'addElement'.")
                        print("The old element will be deleted. Please make \
                              sure to add all previous elements or add them \
                              later with the addElement function.")
                        self.elements[model].remove(elem)
                        correct = False
            if correct:
                self.model = model
                self.elements[model].append(self)
                self.name = name
                self.previous = previousElements
                #self.split = None
    
    # Possible to add previous elements after element is already created
    def addElement(self, previous):
        if type(previous) != list:
            previous = [previous]
        if type(previous) == list:
            correct = True
            for elem in previous:
                if elem not in self.elements[self.getModel()]:
                    correct = False
                    print("'%s' is not an element of model '%s'." %
                          (elem.getName(), self.getModel()))
                    print("Please first define the previous element or set \
                          previousElement equal to an element you already \
                          defined.")
                elif elem.__class__.__name__ == "end":
                    correct = False
                    print("Previous element is of type 'end'. This is not possible.")
                elif elem in self.getPreviousElement():
                    correct = False
                    print("The element '%s' is already part of the previous \
                          elements of the ANDjoin '%s'." % 
                          (elem.getName(), self.getName()))
                elif elem.__class__.__name__ == "start" or \
                    elem.__class__.__name__ == "activity" or \
                    elem.__class__.__name__ == "intermediate" or \
                    elem.__class__.__name__ == "XORjoin" or \
                    elem.__class__.__name__ == "ANDjoin":
                    for el in self.elements[self.getModel()]:
                        if el.getPreviousElement() == [elem]:
                            print("The element '%s' already has '%s' as previous \
                                  element." % (el.getName(), elem.getName()))
                            correct = False
            if correct:
                for elem in previous:
                    self.previous.append(elem)