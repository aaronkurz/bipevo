"""
# FOR NOW: normal differential evolution
# TODO LATER: Improved differential evolution:
The parameters of the improved algorithm were the number of individuals in the population
𝑁𝑃 = 30, maximum number of iterations 𝑀𝑎𝑥𝐼𝑡 = 1000,
crossover probability 𝑝𝐶𝑅 = 0.3 and amplification factor 𝐹 was uniformly distributed in the interval 0.2 and 0.8,
the probability of update 𝑝𝑢 =0.3,constants 𝑑0 =10 (initial distance between the individuals), 𝑡ℎ𝑁𝑃 = 100 and 𝑡ℎ𝐶𝑅 =1.
"""
from scipy.optimize import differential_evolution
from scipy.optimize import Bounds
from scipy.optimize import OptimizeResult
from datetime import datetime


class Environment:
    """ Execution interface of differential evolution

    Can be used from other packages/modules to set the execution parameters for the differential evolution and then
    actually execute it. Entry-point of this sub-package.
    """

    def __init__(self,
                 objective: callable,
                 cost: [int],
                 waiting_weights: [int],
                 bounds: ([int], [int]),
                 popsize: int,
                 max_it: int,
                 crossover_prob: float,
                 amplification_factor: (float, float)):
        """ Parameters of execution

        :param objective: fitness function
        :param cost: cost per activity
        :param bounds: tuple of bounds ordered by activity (lower_bounds, upper_bounds)
        :param popsize: 𝑁𝑃, number of individuals in the population
        :param max_it: 𝑀𝑎𝑥𝐼𝑡, maximum number of iterations; maxi num of gens over which the entire pop is evolved
        :param crossover_prob: 𝑝𝐶𝑅, crossover probability
        :param amplification_factor: 𝐹, in other literature known as mutation constant or differential weight
        """
        self.objective = objective
        self.bounds = bounds
        self.cost = cost
        self.waiting_weights = waiting_weights
        self.popsize = popsize
        self.max_it = max_it
        self.crossover_prob = crossover_prob
        self.amplification_factor = amplification_factor

    class DeResult:
        """ Return type for after the DE env has finished running """

        def __init__(self, success: bool,
                     message: str,
                     nit: int,
                     nfev: int,
                     solution: [int],
                     evaluation: float,
                     duration_s: float):
            self.success = success
            self.message = message
            self.nit = nit
            self.nfev = nfev
            self.solution = solution
            self.evaluation = evaluation
            self.duration_s = duration_s

    def reformat_bounds(self) -> Bounds:
        """ Turn input of bounds with type bounds: ([int], [int]) into scipy Bounds type.

        :return: scipy Bounds of upper and lower resource bounds on each activity i
        """
        return Bounds(lb=self.bounds[0], ub=self.bounds[1])

    def run(self) -> DeResult:
        """ Executes differential evolution optimization and prints results to console

        :return: None
        """
        start_time: datetime = datetime.now()
        max_iter_func = (self.max_it + 1) * self.popsize * len(self.bounds[0])
        print("Maximum number of function evaluations (with no polishing): " + str(max_iter_func))
        arg_tuple = ([self.cost, self.waiting_weights],)
        result: OptimizeResult = differential_evolution(func=self.objective,
                                                        bounds=self.reformat_bounds(),
                                                        args=arg_tuple,
                                                        maxiter=self.max_it,
                                                        mutation=self.amplification_factor,
                                                        recombination=self.crossover_prob,
                                                        popsize=self.popsize,
                                                        polish=False)
        end_time: datetime = datetime.now()
        # creating and returning result
        duration_s = (end_time - start_time).total_seconds()
        rounded_solution = [round(x) for x in result.x]
        return self.DeResult(success=result.success,
                             message=result.message,
                             nit=result.nit,
                             nfev=result.nfev,
                             solution=rounded_solution,
                             evaluation=self.objective(rounded_solution, ([self.cost, self.waiting_weights])),
                             duration_s=duration_s)

