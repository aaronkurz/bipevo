import bpmsim
import scipy.stats
import random

order = bpmsim.importBPMN(modelName="Order Fulfillment",
                          withSubprocess=True,
                          outputHelp=True,
                          fileName="C:/Users/Droomelot/Downloads/Order Fulfillment.bpmn")

creditClerk = bpmsim.importBPMN(modelName="Credit Application Clerk",
                                outputHelp=True,
                                fileName="C:/Users/Droomelot/Downloads/Credit Application Clerk.bpmn")

creditCreditOfficer = bpmsim.importBPMN(modelName="Credit Application Credit Officer",
                                        outputHelp=True,
                                        fileName="C:/Users/Droomelot/Downloads/Credit Application CreditOfficer.bpmn")

clerk = bpmsim.resource(name="Clerk", capacity=3)
creditOfficer = bpmsim.resource(name="Credit Officer", capacity=2)
storeOrder = bpmsim.store(name="Order store", capacity=3, initial=3)
storeApplication = bpmsim.store(name="Application store", capacity=2400)

#------------------------------------------------#
#----------SIMULATION ORDER FULFILLMENT----------#
#------------------------------------------------#

# SET START
bpmsim.setStart(BPMN=order, name="Purchase Order Received", getStore=[storeOrder])

# SET ACTIVITIES
priorOrder = 1
def getNumber():
    number = random.randint(8,12)
    return(number)
    
bpmsim.setActivity(BPMN=order, name="Check stock availability", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=2,scale=0.5),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Retrieve product from warehouse", resources=[clerk], amount=[1],
                   duration=lambda: getNumber(),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Manufacture Product", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.expon.rvs(loc=15),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Confirm Order", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.expon.rvs(loc=3),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Archive order", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.expon.rvs(loc=3),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)

bpmsim.setActivity(BPMN=order, name="Check raw materials availability", resources=[clerk], amount=[1],
                   duration=lambda: 20,
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Request raw materials from supplier 1", resources=[clerk], amount=[1],
                   duration=lambda: 10,
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Obtain raw materials from supplier 1", resources=[clerk], amount=[1],
                   duration=lambda: 5,
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Request raw materials from supplier 2", resources=[clerk], amount=[1],
                   duration=lambda: 12,
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Obtain raw materials from supplier 2", resources=[clerk], amount=[1],
                   duration=lambda: 7,
                   fixedCost=5, variableCost=0.5, priority=priorOrder)

bpmsim.setActivity(BPMN=order, name="Get shipment address", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=5,scale=1),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Emit invoice", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=4,scale=2),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Receive payment", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=6,scale=3),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)
bpmsim.setActivity(BPMN=order, name="Ship product", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=8,scale=2),
                   fixedCost=5, variableCost=0.5, priority=priorOrder)

# SET INTERMEDIATE EVENTS
bpmsim.setIntermediate(BPMN=order, name="Stock availability checked", duration=lambda: 0, getStore=[], putStore=[])
bpmsim.setIntermediate(BPMN=order, name="Raw materials acquired", duration=lambda: 0, getStore=[], putStore=[])
bpmsim.setIntermediate(BPMN=order, name="Order confirmed", duration=lambda: 0, getStore=[], putStore=[])
bpmsim.setIntermediate(BPMN=order, name="Order shipped and invoiced", duration=lambda: 0, getStore=[], putStore=[])

# SET END
bpmsim.setEnd(BPMN=order, name="Order fulfilled", putStore=[storeOrder])

# SET XOR SPLIT
bpmsim.setXORsplit(BPMN=order,name="in stock?",
                   nextElementsNames=["Retrieve product from warehouse","Stock availability checked"],
                   probabilities=[70,30])
bpmsim.setXORsplit(BPMN=order,name="supplier?",
                   nextElementsNames=["Request raw materials from supplier 1","Request raw materials from supplier 2"],
                   probabilities=[50,50])

# CREATE INSTANCES
instancesOrder = bpmsim.createInstanceDistribution("Order Fulfillment", time=48000, number=800,
                                                   distribution=lambda: scipy.stats.beta.rvs(a=2,b=5),
                                                   between01=True, normalize=False)

#-------------------------------------------------------#
#----------SIMULATION CREDIT APPLICATION CLERK----------#
#-------------------------------------------------------#

# SET START
bpmsim.setStart(BPMN=creditClerk, name="Credit application received", getStore=[])

# SET ACTIVITIES
bpmsim.setActivity(BPMN=creditClerk, name="Check credit history", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=10,scale=2),
                   fixedCost=5, variableCost=0.5, priority=-1)
bpmsim.setActivity(BPMN=creditClerk, name="Check income sources", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=10,scale=4),
                   fixedCost=5, variableCost=0.5, priority=0)
bpmsim.setActivity(BPMN=creditClerk, name="Send e-mail to customer", resources=[clerk], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=10,scale=2),
                   fixedCost=5, variableCost=0.5)

# SET INTERMEDIATE EVENTS
bpmsim.setIntermediate(BPMN=creditClerk, name="Credit Application checked",
                       duration = lambda:0,putStore=[storeApplication])

# SET END
bpmsim.setEnd(BPMN=creditClerk, name="Customer notified", putStore=[])

# SET XOR SPLIT

# CREATE INSTANCES
instancesClerk = bpmsim.createInstancesInterDistribution("Credit Application Clerk",
                                                         startTime=0, time=None, number=2400,
                                                         interval=lambda:scipy.stats.norm.rvs(loc=20,scale=1))

#----------------------------------------------------------------#
#----------SIMULATION CREDIT APPLICATION CREDIT OFFICER----------#
#----------------------------------------------------------------#

# SET START
bpmsim.setStart(BPMN=creditCreditOfficer, name="Credit application received", getStore=[storeApplication])

# SET ACTIVITIES
bpmsim.setActivity(BPMN=creditCreditOfficer, name="Assess application", resources=[creditOfficer], amount=[1],
                   duration=lambda: scipy.stats.expon.rvs(loc=20),
                   fixedCost=5, variableCost=1)
bpmsim.setActivity(BPMN=creditCreditOfficer, name="Receive customer feedback")
bpmsim.setActivity(BPMN=creditCreditOfficer, name="Notify rejection", resources=[creditOfficer], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=10,scale=2),
                   fixedCost=5, variableCost=1)
bpmsim.setActivity(BPMN=creditCreditOfficer, name="Make credit offer", resources=[creditOfficer], amount=[1],
                   duration=lambda: scipy.stats.norm.rvs(loc=10,scale=2),
                   fixedCost=5, variableCost=1)

# SET INTERMEDIATE EVENTS

# SET END
bpmsim.setEnd(BPMN=creditCreditOfficer, name="Credit application processed", putStore=[])

# SET XOR SPLIT
bpmsim.setXORsplit(BPMN=creditCreditOfficer,name="decision review requested",
                   nextElementsNames=["start loop","end join credit"],
                   probabilities=[30,70])
bpmsim.setXORsplit(BPMN=creditCreditOfficer,name="application?",
                   nextElementsNames=["Notify rejection","Make credit offer"],
                   probabilities=[20,80])

# CREATE INSTANCES
instancesCreditOfficer = bpmsim.createInstancesFixed("Credit Application Credit Officer",
                                                     startTime=0, time=None, number=2400, interval=0)

#-----------------------------------------#
#----------SIMULATION ALL MODELS----------#
#-----------------------------------------#

# SET SIMULATION PARAMETERS
sim = bpmsim.simulation(instances=[instancesOrder, instancesClerk, instancesCreditOfficer],
                        resources=[clerk, creditOfficer],stores=[storeOrder, storeApplication])

# OUTPUT
sim.simulation(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_output")
sim.simInfo(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_info")
sim.simPlot(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_plot")

#--------------------------------------------------------#
#----------SIMULATION CREDIT APPLICATION MODELS----------#
#--------------------------------------------------------#

# SET SIMULATION PARAMETERS
sim = bpmsim.simulation(instances=[instancesClerk, instancesCreditOfficer],
                        resources=[clerk, creditOfficer],stores=[storeApplication])

# OUTPUT
sim.simulation(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_output_credit")
sim.simInfo(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_info_credit")
sim.simPlot(fileName="C:/Users/Droomelot/Documents/SCHOOL/Masterproef/DEMONSTRATION_plot_credit")