class resource():
    def __init__(self, name, capacity):
        # Check if entered values are correct
        if type(name) != str:
            print("Name should be a string.")
        elif name == "":
            print("Name cannot be an empty string.")
        elif type(capacity) != int:
            print("Capacity should be an integer.")
        else:
            self.name = name
            self.capacity = capacity
        
    def getName(self):
        return(self.name)
    def getCapacity(self):
        return(self.capacity)
        
class store():
    def __init__(self, name, capacity, initial=0):
        # Check if entered values are correct
        if type(name) != str:
            print("Name should be a string.")
        elif name == "":
            print("Name cannot be an empty string.")
        elif type(capacity) != int:
            print("Capacity should be an integer.")
        elif type(initial) != int:
            print("Initial should be an integer.")
        else:
            self.name = name
            self.capacity = capacity
            self.initial = initial
    
    def getName(self):
        return(self.name)
    def getCapacity(self):
        return(self.capacity)
    def getInitital(self):
        return(self.initial)