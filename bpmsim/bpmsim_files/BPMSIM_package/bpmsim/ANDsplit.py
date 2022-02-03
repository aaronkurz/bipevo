from bpmsim.element import element

class ANDsplit(element):
    def __init__(self, model, name, previousElement, outgoing=[], incoming=[], imp=False):
        if imp:
            # If function called in import_BPMN
            self.model = model
            self.elements[model].append(self)
            self.name = name
            self.previous = [previousElement]
            self.outgoing = outgoing
            self.incoming = incoming
        else:
            # Check if everything is added correctly if not called in import_BPMN
            if not (type(model)==str and type(name)==str):
                print("Model and Name should be strings.")
            elif model not in self.elements:
                print("Before adding ANDsplits to this model, you should first \
                      add a start event.")
            elif type(previousElement) == list:
                print("PreviousElement should not be a list. Use XOR and AND to \
                      make splits and joins.")
            elif previousElement not in self.elements[model]:
                print("PreviousElement is not an element of model '%s'." % model)
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
                        print("You already added an element with the name '%s' \
                              to the model '%s'." % (name, model))
                        print("The old element will be deleted.")
                        self.elements[model].remove(elem)
                        stop = False
                if not stop:         
                    self.model = model
                    self.elements[model].append(self)
                    self.name = name
                    self.previous = [previousElement]