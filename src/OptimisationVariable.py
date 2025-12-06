import numpy as np

"""
A variable in the optimisation model.

the name is used to access the variable in other locations.

the relative time step is an integer indicating how many base-time periods
are covered by one "row" of this variable. For instance, if the base time step
is half an hour and this variable exists once an hour, the value is 2.
"""


class OptimisationVariable:
    def __init__(
        self,
        name: str,
        rel_time_step: int,
        lower_limit: np.ndarray,
        upper_limit: np.ndarray,
        objective_function: np.ndarray,
    ):
        self.name = name
        self.relative_time_step = rel_time_step
        self.start_index = None  # set by the OptimisationModel
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.objective_function = objective_function

        assert len(lower_limit) == len(upper_limit), (
            "upper and lower limit must have the same length"
        )
        assert len(lower_limit) == len(objective_function), (
            "objective function must have the same length as the limit"
        )
