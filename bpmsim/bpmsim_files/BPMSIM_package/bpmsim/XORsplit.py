from bpmsim.element import element
import math

class XORsplit(element):
    def __init__(self, model, name, previousElement, outgoing=[], incoming=[], imp=False):
        if imp:
            # If function called in import_BPMN
            self.model = model
            self.elements[model].append(self)
            self.name = name
            self.previous = [previousElement]
            self.nextElements = {}
            self.outgoing = outgoing
            self.incoming = incoming
        else:
            # Check if everything is added correctly if not called in import_BPMN
            if not (type(model)==str and type(name)==str):
                print("Model and Name should be strings.")
            elif model not in self.elements:
                print("Before adding XORsplits to this model, you should first \
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
                    self.nextElements = {}
    
    # Set additional parameters of XORsplit
    def setXORsplit(self, nextElements, probabilities):
        # Check is alle entered values are correct
        correct = False
        if type(nextElements) != list or type(probabilities) != list:
            print("Please enter a list of elements and a list of probabilities.")
        elif len(nextElements) != len(probabilities):
            print("Please enter as much probabilities as elements.")
        elif sum(probabilities) != 100:
            print("Total sum of probabilities should be 100.")
        else:
            # Check if elements are following elements of split
            correct = True
            nextElem = []
            model = self.getModel()
            for elem in self.elements[model]:
                previous = elem.getPreviousElement()
                for prev in previous:
                    if prev == self:
                        nextElem.append(elem)
            for elem in nextElements:
                if elem in nextElem:
                    nextElem.remove(elem)
                else:
                    print("'%s' is not an element after '%s'." %
                          (elem.getName(), self.getName()))
                    correct = False
            # Check if all following elements are added
            if nextElem != []:
                print("There are more elements following on '%s', \
                      please add them to 'nextElements'." % self.getName())
                print("Elements missing are:")
                for elem in nextElem:
                    print(elem.getName())
                correct = False
        
        # Check if probabilities is integer, otherwise multiply with 10
        if correct:
            total = 1
            for i in probabilities:
                number = i
                frac, whole = math.modf(number)
                count = 1
                while frac > 0:
                    count = count * 10
                    number = number * 10
                    frac, whole = math.modf(number)
                if count > total:
                    total = count
            
            # Add elements and probabilities to dicitonary
            for i in range(len(nextElements)):
                self.nextElements[nextElements[i]] = int(probabilities[i] * total)

    def getNextElements(self):
        return(self.nextElements)