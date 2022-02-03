import simpy
import matplotlib.pyplot as plt
import numpy as np

from bpmsim.element import element
from bpmsim.activity import activity
from bpmsim.XORsplit import XORsplit
from bpmsim.ANDjoin import ANDjoin
from bpmsim.resources import resource, store
from bpmsim.instance import instance
import csv
import xlsxwriter
from matplotlib.backends.backend_pdf import PdfPages

class simulation():
    def __init__(self, instances, resources=[], stores=[]):
        stop = False
        # check if parameters are lists:
        if type(resources) != list:
            print("Please enter a list of resources.")
        elif type(stores) != list:
            print("Please enter a list of stores.")
        elif type(instances) != list:
            print("Please enter a list of instances.")
        else:
            isList = True
            for model in instances:
                if type(model) != list:
                    print("Please enter a list of lists of instances.\
                          For example [instances1, instances2] and instances1 \
                          and instances2 are both a list of instances.")
                    isList = False
                    stop = True
                    break
                if isList:
                    # check if instances are from the class instance
                    for inst in model:
                        if type(inst) != instance:
                            print("Please enter instances of class 'instance'.\
                                  You can create them with the functions \
                                  createInstancesFixed, createInstancesDistribution \
                                  or createInstancesInterDistribution.")
                            stop = True
                            break
                
            # check if resources are from the class resource
            for res in resources:
                if type(res) != resource:
                    print("Please enter resources of class 'resource'. Resource \
                          '%s' is not an element of class 'resource'." % res)
                    stop = True
            
            # check if stores are from the class stores
            for sto in stores:
                if type(sto) != store:
                    print("Please enter stores of class 'store'. Store \
                          '%s' is not an element of class 'store'." % sto)
                    stop = True
                    
            if not stop:
                self.instances = instances
                self.resources = resources
                self.stores = stores
    
    # Execute simulation of all models
    def simulation(self, output=False, fileName=None, stop=None):
        
        # Save instances of the lists in one new list
        instObjects = []
        for model in self.instances:
            for inst in model:
                instObjects.append(inst)
        
        # Save model names
        model = []
        for inst in instObjects:
            name = inst.getInstModel()
            if name not in model:
                model.append(name)
        
        # Check if activities and XORsplit are set for simulation
        wrong = False
        for name in model:
            for elem in element.elements[name]:
                if elem.__class__.__name__ == "activity":
                    if elem.getDuration() == None:
                        print("Please set the activity parameters with \
                              'setActivity' for the activity '%s'." %
                              elem.getName())
                        wrong = True
                elif elem.__class__.__name__ == "XORsplit":
                    if not bool(elem.getNextElements()):
                        print("Please set the XORsplit '%s' with \
                              'setXORsplit'." % elem.getName())
                        wrong = True
           
        if not wrong:
            # Generate SimPy environment
            env = simpy.Environment()
            
            # Create SimPy resources within this environment
            resourceObjects = {}
            for res in self.resources:
                resourceObjects[res.getName()] = simpy.PreemptiveResource(env, capacity=res.getCapacity())
            storeObjects = {}
            for sto in self.stores:
                storeObjects[sto.getName()] = simpy.Store(env, capacity=sto.getCapacity())
                if sto.getInitital() > 0:
                    for i in range(sto.getInitital()):
                        storeObjects[sto.getName()].put("item")
            
            # Add SimPy resources to activities, start events, intermediate events and end events
            for key in element.elements.keys():
                if key in model:
                    for elem in element.elements[key]:
                        if elem.__class__.__name__ == "activity":
        
                            oldResources = elem.getResourcesString()
                            newResources = []
                            for res in oldResources:
                                newResources.append(resourceObjects[res.getName()])
                            elem.setResources(newResources)
                            
                            oldGetStores = elem.getGetStoreString()
                            newGetStores = []
                            for sto in oldGetStores:
                                newGetStores.append(storeObjects[sto.getName()])
                            elem.setGetStore(newGetStores)
                            
                            oldPutStores = elem.getPutStoreString()
                            newPutStores = []
                            for sto in oldPutStores:
                                newPutStores.append(storeObjects[sto.getName()])
                            elem.setPutStore(newPutStores)
                        
                        elif elem.__class__.__name__ == "intermediate":
        
                            oldGetStores = elem.getGetStoreString()
                            newGetStores = []
                            for sto in oldGetStores:
                                newGetStores.append(storeObjects[sto.getName()])
                            elem.setGetStore(newGetStores)
                            
                            oldPutStores = elem.getPutStoreString()
                            newPutStores = []
                            for sto in oldPutStores:
                                newPutStores.append(storeObjects[sto.getName()])
                            elem.setPutStore(newPutStores)
                        
                        elif elem.__class__.__name__ == "start":
        
                            oldGetStores = elem.getGetStoreString()
                            newGetStores = []
                            for sto in oldGetStores:
                                newGetStores.append(storeObjects[sto.getName()])
                            elem.setGetStore(newGetStores)
                        
                        elif elem.__class__.__name__ == "end":
                            
                            oldPutStores = elem.getPutStoreString()
                            newPutStores = []
                            for sto in oldPutStores:
                                newPutStores.append(storeObjects[sto.getName()])
                            elem.setPutStore(newPutStores)
            
            # Create list to save the logs of the simulatoin
            log = []
            
            # Create object to throw exception if interruption occurs, this code does not yet work
            inter = simpy.Interrupt
            
            # Iterate the list of instances and simulate all instances
            for inst in instObjects:
                env.process(inst.runInstance(env, log, inter))
            
            # Simulate: env.run until stop or without stop
            if stop != None:
                if type(stop) not in (int, float, complex):
                    print("Stop should be a number.")
                else:
                    env.run(until=stop)
            else:
                env.run()
             
            # Print output if requested
            if output:
                for elem in log:
                    print("%s - %s - %s - start waiting: %f - start: %f - end: %f" % 
                          (elem[0], elem[1], elem[3], elem[4], elem[5], elem[6]))
            
            # Save lofs in csv file if requested
            if fileName != None:
                if type(fileName) != str:
                    print("OutputCSV should be a string.")
                else:
                    fileName = fileName + ".csv"
# =============================================================================
#                     head = ["Model", "Instance", "element", "Name", 
#                             "Start", "End", "Waiting Time", "Process Time", "Interrupted",
#                             "Fixed Cost", "Variable Cost", "Resources", "GetStores", "PutStores"]
# =============================================================================
                    head = ["Model", "Instance", "element", "Name", 
                            "Start Waiting", "Start", "End", "Waiting Time", "Process Time",
                            "Fixed Cost", "Variable Cost", "Resources", "GetStores", "PutStores"]
                    with open(fileName, 'w', newline='') as f:
                        writer = csv.writer(f, delimiter=";")
                        writer.writerow(head)
                        for elem in log:
                            writer.writerow(elem)
            self.log = log
    
    def getLogs(self):
        return(self.log)
    
    # Retrieve general information of the simulation
    def getInfoSimulation(self, model):
        # 0cycle time, 1total waiting, 2total process, 3count activity, 4total cost, 5start, 6end, 7cycle efficiency
        infoSim = [0,0,0,0,0,999999999999,0,0]
        infoResources = {}
        #for mod, inst, elem, name, startprocess, endprocess, waiting, process, inter, fixed, variable, res, getsto, putsto in self.log:
        for mod, inst, elem, name, startWaiting, startprocess, endprocess, waiting, process, fixed, variable, res, getsto, putsto in self.log:
            stop = False
            if model != None:
                if mod != model:
                    stop = True
            if not stop:
                # Total waiting time
                infoSim[1] += waiting
                
                # Start simulation
                if elem=="START":
                    if startWaiting < infoSim[5]:
                        infoSim[5] = startWaiting
                
                # End simulation
                elif elem=="END":
                    if endprocess > infoSim[6]:
                        infoSim[6] = endprocess
                
                elif elem=="activity":
                    # Total process time
                    infoSim[2] += process
                    # TOtal number of activities
                    infoSim[3] += 1
                    # Total cost
                    infoSim[4] += fixed + variable
                
                # Total process time of every resource to calculate resource efficiency
                if res != "":
                    multiples = res.split(',')
                    for m in multiples:     
                        if m not in infoResources:
                            infoResources[m] = process
                        else:
                            infoResources[m] += process
        
        # Calculate total cycle time of simulation
        infoSim[0] = infoSim[6] - infoSim[5]
        
        # Calculate cycle time efficiency
        if infoSim[2]+infoSim[1] != 0:
            infoSim[7] = infoSim[2] / (infoSim[2]+infoSim[1])
        
        # Calculate resource efficiency
        returnResources = []
        for lst in self.resources, self.stores:
            for elem in lst:
                if elem.getName() in infoResources:
                    resEfficiency = (1/elem.getCapacity())*(infoResources[elem.getName()]/infoSim[0])
                    returnResources.append([elem.getName(),resEfficiency])
                    
        # Retrieve number of instances of every model
        numberOfInstances = []
        for mod in self.instances:
            for inst in mod:
                if model != None:
                    if inst.getInstModel() != model:
                        break
                modelName = inst.getInstModel() + " instances"
                numberOfInstances.append([modelName, len(mod)])
                break
        
        returnList = infoSim[0:5]
        returnList.append(infoSim[7])
        # numberOfInstances: modelName, number of instances
        # returnList: cycle time, total waiting, total process, count activity, total cost, cycle efficiency
        # returnResources: resourceName, resourceEfficiency
        return(numberOfInstances,returnList,returnResources)
    
    # Retrieve information per instance
    def getInfoInstance(self,model):
        # models: information per model and then per instance
        models = {}
        #for mod, inst, elem, name, startprocess, endprocess, waiting, process, inter, fixed, variable, res, getsto, putsto in self.log:
        for mod, inst, elem, name, startWaiting, startprocess, endprocess, waiting, process, fixed, variable, res, getsto, putsto in self.log:
            stop = False
            if model != None:
                if mod != model:
                    stop = True
            if not stop:
                if mod not in models:
                    models[mod] = {}
                    # start, end, number of activities, cost, cycle time, waiting time, process time
                    models[mod][inst] = [0,0,0,0,0,0,0]
                if inst not in models[mod]:
                    models[mod][inst] = [0,0,0,0,0,0,0]
                
                # Total waiting time of instance
                models[mod][inst][5] += waiting
                
                # Start time of instance
                if elem == "START":
                    models[mod][inst][0] = startWaiting
                
                # End time of instance
                elif elem == "END":
                    models[mod][inst][1] = endprocess
                
                elif elem == "activity":
                    # Total number of activities of instance
                    models[mod][inst][2] += 1
                    # Total cost of instance
                    models[mod][inst][3] += fixed + variable
                    # Total process time of instance
                    models[mod][inst][6] += process
        
        # Calculate cycle time of instances
        for mod in models:
            for inst in models[mod]:
                models[mod][inst][4] = models[mod][inst][1] - models[mod][inst][0]
        
        # models: mod: instance: start, end, number of activities, cost, cycle time, waiting time, process time
        return(models)
    
    # Retrieve information of the models
    def getInfoModel(self,model):
        models = self.getInfoInstance(model)
        # {models: instances}
        # {instances: # 0start, 1end, 2number of activities, 3cost, 4cycle time, 5waiting time, 6process time}

        modelList = {}
        for mod in models:
            if mod not in modelList:
                # 0Cycle Time, 5Waiting Time, 10Process Time, 15Number of Activities, 20Cost
                # Min, +1Avg, +2Max, +3Total, +4Count
                modelList[mod] = [9999999999,0,0,0,0,
                                  9999999999,0,0,0,0,
                                  9999999999,0,0,0,0,
                                  9999999999,0,0,0,0,
                                  9999999999,0,0,0,0]
        
            for inst in models[mod]:
                # Cycle Time, Waiting Time, Process Time, Number of Activies, Cost
                lst = [[0,models[mod][inst][4]],[5,models[mod][inst][5]],
                       [10,models[mod][inst][6]],[15,models[mod][inst][2]],
                       [20,models[mod][inst][3]]]
                for num,var in lst:
                    # Minimum
                    if var < modelList[mod][num]:
                        modelList[mod][num] = var
                    # Maximum
                    if var > modelList[mod][num+2]:
                        modelList[mod][num+2] = var
                    # Total
                    modelList[mod][num+3] += var
                    # Count
                    modelList[mod][num+4] += 1
        
        returnlist = []
        for mod in modelList:
            data = [str(mod)]
            lst = [0,5,10,15,20]
            for num in lst:
                # Average = Total/count
                modelList[mod][num+1] = modelList[mod][num+3]/modelList[mod][num+4]
                # Add min, avg, max
                data.append(modelList[mod][num])
                data.append(modelList[mod][num+1])
                data.append(modelList[mod][num+2])
            returnlist.append(data)
        
        # returnList: minimum, average, maximum of
        # cycle time, waiting time, process time, number of activities, cost
        return(returnlist)
    
    # Retrieve information per activity
    def getInfoActivities(self,model):
        activities = {}
        #for mod, inst, elem, name, startprocess, endprocess, waiting, process, inter, fixed, variable, res, getsto, putsto in self.log:
        for mod, inst, elem, name, startWaiting, startprocess, endprocess, waiting, process, fixed, variable, res, getsto, putsto in self.log:
            stop = False
            if model != None:
                if mod != model:
                    stop = True
            if not stop:
                if elem=="activity":
                    if name not in activities:
                        activities[name] = [9999999999,0,0,0,0,
                                            9999999999,0,0,0,0,
                                            9999999999,0,0,0,0]
                    lst = [[0,waiting],[5,process],[10,fixed+variable]]
                    for num,var in lst:
                        # minimum
                        if var < activities[name][num]:
                            activities[name][num] = var
                        # maximum
                        if var > activities[name][num+2]:
                            activities[name][num+2] = var
                        # totel
                        activities[name][num+3] += var
                        # count
                        activities[name][num+4] += 1
        returnlist = []
        totalActivities = []
        for act in activities:
            data = [str(act)]
            data2 = [str(act)]
            lst = [0,5,10] # waiting, process, cost
            for num in lst:
                # average
                activities[act][num+1] = activities[act][num+3]/activities[act][num+4]
                data.append(activities[act][num]) # minimum
                data.append(activities[act][num+1]) # average
                data.append(activities[act][num+2]) # maximum
                data2.append(activities[act][num+3]) # total
            data2.append(activities[act][4]) # count
            returnlist.append(data)
            totalActivities.append(data2)
        
        # maxWaiting: activity name, waiting time, number of times activity appeared in simualtion
        maxWaiting = ["",0,0]
        # maxProcess: activity name, process time, number of times activity appeared in simualtion
        maxProcess = ["",0,0]
        # maxCost: activity name, cost, number of times activity appeared in simualtion
        maxCost = ["",0,0]
        for act in totalActivities:
            # ACT: activityName, total waiting time, total prcoess time, total cost
            if act[1] > maxWaiting[1]:
                maxWaiting[0] = act[0]
                maxWaiting[1] = act[1]
                maxWaiting[2] = act[4]
            if act[2] > maxProcess[1]:
                maxProcess[0] = act[0]
                maxProcess[1] = act[2]
                maxProcess[2] = act[4]
            if act[3] > maxCost[1]:
                maxCost[0] = act[0]
                maxCost[1] = act[3]
                maxCost[2] = act[4]
        returnList2 = [maxWaiting,maxProcess,maxCost]
        
        # returnList: for every activity min, avg, max waiting time, process time and cost
        # returnList2: maxWaiting, maxProcess, maxCost
        return(returnlist, returnList2)
    
    # Retrieve infromation per resource
    def getInfoResources(self,model):
        # resources: resource: min waiting, avg waiting, maximum waiting, total waiting, count waiting
        resources = {}
        #for mod, inst, elem, name, startprocess, endprocess, waiting, process, inter, fixed, variable, res, getsto, putsto in self.log:
        for mod, inst, elem, name, startWaiting, startprocess, endprocess, waiting, process, fixed, variable, res, getsto, putsto in self.log:
            stop = False
            if model != None:
                if mod != model:
                    stop = True
            if not stop:
                if res != "":
                    multiples = res.split(',')
                    for m in multiples:     
                        if m not in resources:
                            resources[m] = [9999999999,0,0,0,0]
                        lst = [[0,waiting]]
                        for num,var in lst:
                            # Minimum
                            if var < resources[m][num]:
                                resources[m][num] = var
                            # Maximum
                            if var > resources[m][num+2]:
                                resources[m][num+2] = var
                            # Total
                            resources[m][num+3] += var
                            # Count
                            resources[m][num+4] += 1
                            
                if getsto != "":
                    multiples = getsto.split(',')
                    for m in multiples:
                        if m not in resources:
                            resources[m] = [9999999999,0,0,0,0]
                        lst = [[0,waiting]]
                        for num,var in lst:
                            # Minimum
                            if var < resources[m][num]:
                                resources[m][num] = var
                            # Maximum
                            if var > resources[m][num+2]:
                                resources[m][num+2] = var
                            # Total
                            resources[m][num+3] += var
                            # Count
                            resources[m][num+4] += 1
                            
                if putsto != "":
                    multiples = putsto.split(',')
                    for m in multiples:
                        if m not in resources:
                            resources[m] = [9999999999,0,0,0,0]
                        lst = [[0,waiting]]
                        for num,var in lst:
                            # Minimum
                            if var < resources[m][num]:
                                resources[m][num] = var
                            # Maximum
                            if var > resources[m][num+2]:
                                resources[m][num+2] = var
                            # Total
                            resources[m][num+3] += var
                            # Count
                            resources[m][num+4] += 1

        returnlist = []
        for res in resources:
            data = [str(res)]
            lst = [0]
            for num in lst:
                resources[res][num+1] = resources[res][num+3]/resources[res][num+4]
                data.append(resources[res][num])
                data.append(resources[res][num+1])
                data.append(resources[res][num+2])
            returnlist.append(data)
        
        # returnList: resource, min waiting, avg waiting, max waiting
        return(returnlist)
        
    def simInfo(self, fileName=None):
        if type(fileName) != str:
            print("fileName should be a string.")
        else:
            # Create xlsx file
            fileName = fileName + ".xlsx"
            workbook = xlsxwriter.Workbook(fileName)
            
            # Set different formats for cells
            borderline=2
            head_left = workbook.add_format({'bold':True, 'bg_color':'white','font_size':9,'top':borderline,'left':borderline})
            head = workbook.add_format({'bold':True, 'bg_color':'white','center_across':True,'font_size':9,'top':borderline})
            head_right = workbook.add_format({'bold':True, 'bg_color':'white','center_across':True,'font_size':9,'top':borderline,'right':borderline})
            
            h_left = workbook.add_format({'bold':True, 'bg_color':'white','font_size':9,'left':borderline})
            h = workbook.add_format({'bold':True, 'bg_color':'white','center_across':True,'font_size':9})
            h_right = workbook.add_format({'bold':True, 'bg_color':'white','center_across':True,'font_size':9,'right':borderline})
            h_bottom_left =  workbook.add_format({'bold':True, 'bg_color':'white','font_size':9,'bottom':borderline,'left':borderline})   
            
            text_left = workbook.add_format({'bg_color':'white','font_size':9,'left':borderline})
            text = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9})
            text_right = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'right':borderline})
            text_top_right = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'top':borderline,'right':borderline})
            
            textlast_left = workbook.add_format({'bg_color':'white','font_size':9,'bottom':borderline,'left':borderline})
            textlast = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'bottom':borderline})
            textlast_right = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'bottom':borderline,'right':borderline})
            
            # Save models
            multipleModels = False
            modelNames = []
            #for mod, inst, elem, name, startprocess, endprocess, waiting, process, inter, fixed, variable, res, getsto, putsto in self.log:
            for mod, inst, elem, name, startWaiting, startprocess, endprocess, waiting, process, fixed, variable, res, getsto, putsto in self.log:
                if mod not in modelNames:
                    modelNames.append(mod)
            if len(modelNames) > 1:
                multipleModels = True
                simModels = []
                lstModels = []
            
            # Retrieve general information of the simulation
            infoSim = workbook.add_worksheet('General')
            dataSimInstances, dataSim, dataSimRes = self.getInfoSimulation(None)
            
            worksheet1 = workbook.add_worksheet('Models')
            head11 = ["Cycle Time", "Waiting Time", "Process Time",
                      "Number of activities", "Cost"]
            head12 = ["Name","Minimum","Average","Maximum",
                     "Minimum","Average","Maximum",
                     "Minimum","Average","Maximum",
                     "Minimum","Average","Maximum",
                     "Minimum","Average","Maximum"]
            data1 = self.getInfoModel(None)
            
            worksheet2 = workbook.add_worksheet('Activities')
            head21 = ["Waiting Time", "Process Time", "Cost"]
            head22 = ["Name","Minimum","Average","Maximum",
                     "Minimum","Average","Maximum",
                     "Minimum","Average","Maximum"]
            data2, totAct1 = self.getInfoActivities(None)
            
            worksheet3 = workbook.add_worksheet('Resources')
            head31 = ["Waiting Time"]
            head32 = ["Name","Minimum","Average","Maximum"]
            data3 = self.getInfoResources(None)
            
            # Retrieve information per model
            if multipleModels:
                for m in modelNames:
                    modelName = m.replace(" ", "")
                    modelName = modelName[0:20]
                    first, second, third = self.getInfoSimulation(m)
                    one, two = self.getInfoActivities(m)
                    simModels.append([workbook.add_worksheet(str(modelName)+" General"),first, second, third, two])
                    lstModels.append([workbook.add_worksheet(str(modelName)+" Model"),head11,head12,self.getInfoModel(m)])
                    lstModels.append([workbook.add_worksheet(str(modelName)+" Activities"),head21,head22,one])
                    lstModels.append([workbook.add_worksheet(str(modelName)+" Resources"),head31,head32,self.getInfoResources(m)])
            
            # Print generated information to excel file
            lst = [[worksheet1,head11,head12,data1],[worksheet2,head21,head22,data2],[worksheet3,head31,head32,data3]]
            if multipleModels:
                for l in lstModels:
                    lst.append(l)

            for worksheet, head1, head2, data in lst:
                if len(data) > 0:
                    worksheet.set_column(1,1,35)
                    
                    row=1
                    col=1
                    worksheet.write(row,col,"",head_left)
                    col+=1 
                    for hd in head1[:-1]:
                        worksheet.merge_range(row,col,row,col+2,hd,head)
                        col+=3
                        
                    worksheet.merge_range(row,col,row,col+2,head1[-1], head_right)
                    
                    row = 2
                    col=1
                    worksheet.write(row,col,head2[0],h_left)
                    col+=1
                    worksheet.write_row(row,col,head2[1:-1],h)
                    col+=len(head2[1:-1])
                    worksheet.write(row,col,head2[-1],h_right)
                    
                    row=3
                    col=1
                    for d in data[:-1]:
                        worksheet.write(row,col,d[0],text_left)
                        col+=1
                        worksheet.write_row(row,col,d[1:-1],text)
                        col+=len(d[1:-1])
                        worksheet.write(row,col,d[-1],text_right)
                        row+=1
                        col=1
                    
                    worksheet.write(row,col,data[-1][0],textlast_left)
                    col+=1
                    worksheet.write_row(row,col,data[-1][1:-1],textlast)
                    col+=len(data[-1][1:-1])
                    worksheet.write(row,col,data[-1][-1],textlast_right)
        
            if multipleModels:
                simModels.append([infoSim,dataSimInstances,dataSim,dataSimRes,totAct1])
            else:
                simModels= [[infoSim,dataSimInstances,dataSim,dataSimRes,totAct1]]
            
            head = ["Total Cycle Time", "Total Waiting Time", "Total Process Time",
                    "Total Number of Activities", "Total Cost",
                    "Cycle Time Efficiency"]
            headSecond = [["Bottleneck Waiting Time: ", "% of Total Waiting Time", "% of Total Number of Activities"],
                          ["Bottleneck Process Time: ", "% of Total Process Time", "% of Total Number of Activities"],
                          ["Bottleneck Cost: ", "% of Total Cost", "% of Total Number of Activities"]]
            
            for sheet, dataInst, data, dataRes, totAct in simModels:
                
                # Waiting Time, Process Time, Cost
                if data[1] > 0:
                    totAct[0][1] = totAct[0][1]/data[1]
                    totAct[0][2] = totAct[0][2]/data[3]
                if data[2] > 0:
                    totAct[1][1] = totAct[1][1]/data[2]
                    totAct[1][2] = totAct[1][2]/data[3]
                if data[4] > 0:
                    totAct[2][1] = totAct[2][1]/data[4]
                    totAct[2][2] = totAct[2][2]/data[3]
                
                text_right_procent = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'num_format':'0.00%','right':borderline})
                textlast_right_procent = workbook.add_format({'bg_color':'white','center_across':True,'font_size':9,'num_format':'0.00%','bottom':borderline,'right':borderline})
                
                dataRows = []
                for inst in dataInst:
                    dataRows.append(inst)
                dataRows.append(["",""])
                for i in range(len(data)):
                    info = [head[i],data[i]]
                    dataRows.append(info)
                dataRows.append(["",""])
                for i in dataRes:
                    headName = "Resource Efficiency " + i[0]
                    dataRows.append([headName,i[1], text_right_procent])
                dataRows.append(["",""])
                for i in range(len(totAct)):
                    headName = headSecond[i][0] + totAct[i][0]
                    dataRows.append([headName, ""])
                    dataRows.append([headSecond[i][1], totAct[i][1], text_right_procent])
                    dataRows.append([headSecond[i][2], totAct[i][2], text_right_procent])
                
                sheet.set_column(1,1,35)
                row = 1
                col = 1
                sheet.write(row,col,dataRows[0][0],head_left)
                col+=1
                sheet.write(row,col,dataRows[0][1],text_top_right)
                row+=1
                col=1
                for r in dataRows[1:-1]:
                    sheet.write(row,col,r[0],h_left)
                    col+=1
                    if len(r) == 3:
                        sheet.write(row, col, r[1], r[2])
                    else:
                        sheet.write(row,col,r[1],text_right)
                    row+=1
                    col=1
                sheet.write(row,col,dataRows[-1][0],h_bottom_left)
                col+=1
                if len(dataRows[-1]) == 3:
                    sheet.write(row,col,dataRows[-1][1],textlast_right_procent)
                else:
                    sheet.write(row,col,dataRows[-1][1],textlast_right)
            
            workbook.close()
    
    # Generate requested plot      
    def plotHist(self, data, model, title, bins, color, pdf):
        fig, axs = plt.subplots()
        dataPoints,b,o = axs.hist(data,bins=bins, orientation="horizontal", color=color, rwidth=0.9) # rwidht = 0.9, color='blue'
        axs.set_yticks(b,[])
        axs.set_xticks([],[])
        axs.spines['top'].set_visible(False)
        axs.spines['right'].set_visible(False)
        axs.spines['bottom'].set_visible(False)
        axs.spines['left'].set_visible(False)
        bin_centers = 0.5*np.diff(b) + b[:-1]
        total = 0
        for x in dataPoints:
            total += x
        for x,y in zip(dataPoints,bin_centers):
            if x > 0:
                percent = str(round((x/total)*100,2))
                plt.text(x,y," "+str(int(x))+" ("+percent+"%)",ha='left', va='center',size=8)
        plt.tick_params(labelsize=8, color='white', direction ='in')
        plt.title(model + ' - Histogram of ' + title)
        pdf.savefig(bbox_inches='tight', pad_inches=0.2)
        plt.close()
    
    # Generate graphs of the simulation per model  
    def simPlot(self, fileName):
        if type(fileName) != str:
            print("fileName should be a string.")
        else:
            fileName = fileName + ".pdf"
            instancesModel = self.getInfoInstance(None)
            # {model: instances}
            # {instances: 0 start, 1 end, 2 number of activities, 3 cost, 4 cycle time, 5 waiting time, 6 process time}        
            modelData = {}
            for mod in instancesModel:
                modelData[mod] = {'cycle':[],'waiting':[],'process':[],'nract':[],'cost':[]}
                for inst in instancesModel[mod]:
                    modelData[mod]['cycle'].append(instancesModel[mod][inst][4])
                    modelData[mod]['waiting'].append(instancesModel[mod][inst][5])
                    modelData[mod]['process'].append(instancesModel[mod][inst][6])
                    modelData[mod]['nract'].append(instancesModel[mod][inst][2])
                    modelData[mod]['cost'].append(instancesModel[mod][inst][3])
            colors = ["lightblue","olive","darkred","darkgoldenrod","darkslateblue"]
            count=0
            with PdfPages(fileName) as pdf:
                for mod in instancesModel:
                    color = colors[count]
                    self.plotHist(modelData[mod]['cycle'], mod, 'Cycle Times', 10, color, pdf)
                    self.plotHist(modelData[mod]['waiting'], mod, 'Waiting Times', 10, color, pdf)
                    self.plotHist(modelData[mod]['process'], mod, 'Process Times', 10, color, pdf)
                    self.plotHist(modelData[mod]['nract'], mod, 'Number of Activities', 10, color, pdf)
                    self.plotHist(modelData[mod]['cost'], mod, 'Cost', 10, color, pdf)
                    count+=1
                    if count == len(colors):
                        count=0