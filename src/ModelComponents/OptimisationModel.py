import math
import numpy as np
from scipy import optimize
from src.ModelComponents import OptimisationVariable as ov
from src.ModelComponents import OptimisationConstraint as oc


class OptimisationModel:
    def __init__(self):
        # variable definition
        self.variables = dict[str, ov.OptimisationVariable]()
        self.objective_function = np.array([])
        self.lower_limit = np.array([])
        self.upper_limit = np.array([])
        self.integrality = np.array([])

        # constraint definition
        self.constraint_matrix = np.array([np.array])
        self.constraint_lower_bound = np.array([])
        self.constraint_upper_bound = np.array([])

    """
    Add an optimisation variable to the optimisation model
    this automatically extends the arrays and matrices of the model.
    The constraints are padded with 0s for this variable
    """

    def add_variable(self, v: ov.OptimisationVariable):
        # Tell the variable where in the array it sits
        k = 0
        for vprev in self.variables.values():
            k = k + len(vprev.lower_limit)
        v.start_index = k

        # add it to the model
        self.variables[v.name] = v
        self.objective_function = np.concat(
            [self.objective_function, v.objective_function]
        )
        self.lower_limit = np.concat([self.lower_limit, v.lower_limit])
        self.upper_limit = np.concat([self.upper_limit, v.upper_limit])

        # scipy milp has 0 for continuous, 1 for integers
        # No other types are supported for now
        itype = 0 if v.variable_type == ov.VariableType.CONTINUOUS else 1
        self.integrality = np.concat(
            [self.integrality, np.ones_like(v.lower_limit) * itype]
        )

        # Extend the constraint matrix by adding columns of 0
        if len(self.constraint_lower_bound) > 0:
            self.constraint_matrix = np.hstack(
                [
                    self.constraint_matrix,
                    np.zeros(shape=(len(self.constraint_matrix), len(v.lower_limit))),
                ]
            )

    """
    We provide two ways to add constraints.

    The simplest one is using the OptimisationConstrant class.
    If you have a constraint that is not identical at each point in time
    you can add it manually using the second function.
    However, then you have to make sure the columns are correct.
    """

    def add_constraint(self, c: oc.OptimisationConstraint, N: int):
        for i in range(N):
            a = np.zeros_like(self.lower_limit)
            for varname in c.variable_factors.keys():
                # support variables with larger time steps
                relindex = math.floor(i / self.variables[varname].relative_time_step)
                a[self.variables[varname].start_index + relindex] = c.variable_factors[
                    varname
                ]
            self.add_constraint_manual(arow=a, lb=c.lower_limit, ub=c.upper_limit)

    def add_constraint_manual(self, arow: np.ndarray, lb: float, ub: float):
        assert len(arow) == len(self.lower_limit), (
            "The constraint must have the same number of columns as there are variables in the model"
        )

        if len(self.constraint_lower_bound) > 0:
            self.constraint_matrix = np.vstack([self.constraint_matrix, arow])
            self.constraint_lower_bound = np.append(self.constraint_lower_bound, lb)
            self.constraint_upper_bound = np.append(self.constraint_upper_bound, ub)
        else:
            self.constraint_matrix = arow
            self.constraint_lower_bound = np.array([lb])
            self.constraint_upper_bound = np.array([ub])

    def optimise(self) -> optimize.OptimizeResult:
        return optimize.milp(
            c=self.objective_function,
            bounds=optimize.Bounds(lb=self.lower_limit, ub=self.upper_limit),
            constraints=optimize.LinearConstraint(
                A=self.constraint_matrix,
                lb=self.constraint_lower_bound,
                ub=self.constraint_upper_bound,
            ),
            integrality=self.integrality,
        )
