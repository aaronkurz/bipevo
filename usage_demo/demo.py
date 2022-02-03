from scipy import stats
import bipevo

bipevo_env = bipevo.Environment()

# setting parameters of process model
bipevo_env.CURRENT_PROCESS = "credit-check.bpmn"
bipevo_env.BPMN_FILE_PATH = "resources/credit-check.bpmn"
bipevo_env.NUMBER_OF_ACTIVITIES = 7
bipevo_env.MIN_RESOURCES_ON_ACTIVITY = [1, 1, 1, 1, 1, 3, 1]  # alpha in paper
bipevo_env.MAX_RESOURCES_ON_ACTIVITY = [10, 10, 10, 10, 10, 5, 10]  # beta in paper
bipevo_env.COST_PER_ACTIVITY = [1500, 2000, 2000, 2000, 1500, 3000, 1500]
bipevo_env.ACTIVITY_NAMES = ["Acceptance of requests",
                             "Collection of Documents",
                             "Completeness Check",
                             "Credit Worthiness Check",
                             "Collateral Check",
                             "Credit Committee",
                             "Requirements Review"]
bipevo_env.WAITING_WEIGHTS = [2, 2, 1, 1, 1, 1, 0]
bipevo_env.POPSIZE = 1
bipevo_env.AMOUNT_RESOURCES_NEEDED_ACTIVITY = [1, 1, 1, 1, 1, 1, 1]


# setting parameters of simulation model
def d1():
    value = stats.uniform.rvs(loc=9.017, scale=10.95)
    return value if value > 0 else 0


def d2():
    value = stats.weibull_min.rvs(c=98.708, scale=3.290)
    return value if value > 0 else 0


def d3():
    value = stats.uniform.rvs(loc=45.85, scale=(89.933 - 45.85))
    return value if value > 0 else 0


def d4():
    value = stats.norm.rvs(loc=82.813, scale=7.548)
    return value if value > 0 else 0


def d5():
    value = stats.uniform.rvs(loc=20.133, scale=(74.383 - 20.133))
    return value if value > 0 else 0


def d6():
    value = stats.norm.rvs(loc=3.796, scale=0.436)
    return value if value > 0 else 0


def d7():
    value = stats.uniform.rvs(loc=5.033, scale=(14.917 - 5.033))
    return value if value > 0 else 0


bipevo_env.DURATION_DIST_ACT = [d1,
                                d2,
                                d3,
                                d4,
                                d5,
                                d6,  # should be lognorm but bpmsim had a problem with that
                                d7]


def d0():
    value = stats.norm.rvs(loc=1.136, scale=1.089)
    return value if value > 0 else 0


bipevo_env.DURATION_INSTANCE_GEN_DIST = d0
bipevo_env.NUMBER_OF_SIMULATIONS_PER_FITNESS_FUNC = 5

# running optimization
bipevo_env.run()
