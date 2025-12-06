import numpy as np
from scipy import optimize
from src import OptimisationVariable as ov


class OptimisationModel:
    def __init__(self):
        self.variables = []
        self.objective_function = np.array([])
        self.lower_limit = np.array([])
        self.upper_limit = np.array([])

    def add_variable(self, v: ov.OptimisationVariable):
        k = 0
        for v in self.variables:
            k = k + len(v.lower_limit)
        v.start_index = k
        self.variables.append(v)
        self.objective_function = np.concat(
            [self.objective_function, v.objective_function]
        )
        self.lower_limit = np.concat([self.lower_limit, v.lower_limit])
        self.upper_limit = np.concat([self.upper_limit, v.upper_limit])

    def optimise(self) -> optimize.OptimizeResult:
        return optimize.milp(
            c=self.objective_function,
            bounds=optimize.Bounds(lb=self.lower_limit, ub=self.upper_limit),
        )
