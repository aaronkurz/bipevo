import os

from bipevo.differential_evolution import env_differential_evolution
from bipevo.simulation import env_simulation
import shutil
import matplotlib.pyplot as plt

DATA_STORING = True
record = []
number_of_evaluations = 0

BPMN_FILE_PATH = None
CURRENT_PROCESS = None
ACTIVITY_NAMES = None
DURATION_DIST_ACT = None
DURATION_INSTANCE_GEN_DIST = None
NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC = None
COST_PER_ACTIVITY = None
WAITING_WEIGHTS = None
NUMBER_OF_ACTIVITIES = None
POPSIZE = None
AMOUNT_RESOURCES_NEEDED_ACTIVITY = None


# TODO get closer to paper fitness function; float for amount_of_resources since scipy DE does not support integer
#  constraint --> should be done by rounding
#  https://stackoverflow.com/questions/35494782/scipy-differential-evolution-with-integers
# Another TODO: make the "boilerplate" hidden and let user put it in config
def fitness_func(amount_of_resources: [float], cost_waitingweight_tuple) -> float:
    int_amount_of_resources = [round(x) for x in amount_of_resources]
    for elem in int_amount_of_resources:
        assert isinstance(elem, int), "Resource allocation not integer!"
    assert cost_waitingweight_tuple[0] == COST_PER_ACTIVITY, "Mismatch between cost in specified and cost " \
                                                             "during simulation. This problem is most likely " \
                                                             "NOT caused by faulty user-input."
    assert cost_waitingweight_tuple[1] == WAITING_WEIGHTS, "Mismatch between wait-weights in specified and " \
                                                           "during simulation. This problem is most likely " \
                                                           "NOT caused by faulty user-input."

    current_cost = 0.0
    current_waiting = 0.0
    sim_env = env_simulation.Environment(
        file_name=CURRENT_PROCESS,
        file_path=BPMN_FILE_PATH,
        number_of_activities=NUMBER_OF_ACTIVITIES,
        activity_names=ACTIVITY_NAMES,
        duration_activities=DURATION_DIST_ACT,
        duration_instance_gen=DURATION_INSTANCE_GEN_DIST,
        amount_of_instances_sim=NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC,
        amount_needed_for_activity=AMOUNT_RESOURCES_NEEDED_ACTIVITY
    )
    sim_env.run(int_amount_of_resources)
    average_waiting_times = sim_env.get_average_waiting_times()
    for i in range(len(int_amount_of_resources)):
        current_cost += cost_waitingweight_tuple[0][i] * int_amount_of_resources[i]
        current_waiting += cost_waitingweight_tuple[0][i] * average_waiting_times[i]
    eval_result = current_cost + current_waiting

    global number_of_evaluations
    number_of_evaluations += 1
    if DATA_STORING:
        record.append(eval_result)
    return eval_result


class Environment:
    CURRENT_PROCESS = None
    BPMN_FILE_PATH = None
    NUMBER_OF_ACTIVITIES = None
    MIN_RESOURCES_ON_ACTIVITY = None  # alpha in paper
    MAX_RESOURCES_ON_ACTIVITY = None  # beta in paper
    COST_PER_ACTIVITY = None
    ACTIVITY_NAMES = None
    DURATION_DIST_ACT = None
    DURATION_INSTANCE_GEN_DIST = None
    WAITING_WEIGHTS = None
    NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC = None
    POPSIZE = None
    AMOUNT_RESOURCES_NEEDED_ACTIVITY = None

    # TODO
    def is_ready(self):
        if self.POPSIZE is not None and self.CURRENT_PROCESS is not None and self.BPMN_FILE_PATH is not None and self.NUMBER_OF_ACTIVITIES is not None and self.MIN_RESOURCES_ON_ACTIVITY is not None and self.MAX_RESOURCES_ON_ACTIVITY is not None and self.COST_PER_ACTIVITY is not None and self.ACTIVITY_NAMES is not None and self.DURATION_DIST_ACT is not None and self.DURATION_INSTANCE_GEN_DIST is not None and self.WAITING_WEIGHTS is not None and self.NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC is not None:
            return True
        else:
            return False

    def run(self):
        if not os.path.exists("./gen_sim"):
            os.mkdir("./gen_sim")
        if not self.is_ready():
            raise Exception("Not all parameters have been set.")

        global BPMN_FILE_PATH
        global CURRENT_PROCESS
        global ACTIVITY_NAMES
        global DURATION_DIST_ACT
        global DURATION_INSTANCE_GEN_DIST
        global NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC
        global COST_PER_ACTIVITY
        global WAITING_WEIGHTS
        global NUMBER_OF_ACTIVITIES
        global POPSIZE
        global AMOUNT_RESOURCES_NEEDED_ACTIVITY
        BPMN_FILE_PATH = self.BPMN_FILE_PATH
        CURRENT_PROCESS = self.CURRENT_PROCESS
        ACTIVITY_NAMES = self.ACTIVITY_NAMES
        DURATION_DIST_ACT = self.DURATION_DIST_ACT
        DURATION_INSTANCE_GEN_DIST = self.DURATION_INSTANCE_GEN_DIST
        NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC = self.NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC
        COST_PER_ACTIVITY = self.COST_PER_ACTIVITY
        WAITING_WEIGHTS = self.WAITING_WEIGHTS
        NUMBER_OF_ACTIVITIES = self.NUMBER_OF_ACTIVITIES
        POPSIZE = self.POPSIZE
        AMOUNT_RESOURCES_NEEDED_ACTIVITY = self.AMOUNT_RESOURCES_NEEDED_ACTIVITY

        de_env = env_differential_evolution.Environment(objective=fitness_func,
                                                        cost=self.COST_PER_ACTIVITY,
                                                        waiting_weights=self.WAITING_WEIGHTS,
                                                        bounds=(self.MIN_RESOURCES_ON_ACTIVITY
                                                                , self.MAX_RESOURCES_ON_ACTIVITY),
                                                        popsize=self.POPSIZE,
                                                        max_it=1000,
                                                        crossover_prob=0.3,
                                                        amplification_factor=(0.2, 0.8))
        result = de_env.run()
        # summarize the result
        print("")
        print('Success : %s' % str(result.success))
        print('Message : %s' % result.message)
        print('Duration in sec : %d' % result.duration_s)
        print('Number of iterations/generations: %d' % result.nit)
        print('Total evaluations of fitness func: %d' % result.nfev)
        solution = result.solution
        evaluation = result.evaluation
        print('Solution: ' + str(solution) + ' = ' + str(evaluation))
        shutil.rmtree("./gen_sim")
        if os.path.exists('./result-plot.png'):
            os.remove('./result-plot.png')
        if DATA_STORING:
            x = range(0, len(record))
            plt.plot(x, record, alpha=0.5)
            plt.xlabel("No. fitness function evaluation")
            plt.ylabel("Result of fitness function evaluation")
            plt.savefig('./result-plot.png')
            print('You can find a plot of the evaluations over time here: ./result-plot.png')
