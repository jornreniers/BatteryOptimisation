import numpy as np
from enum import Enum

"""
A variable in the optimisation model.

The key reason for this class is to store
the location of the variable in the arrays and matrices in the model.
Eg we will always find the value at the second time step, ie xi[1]
on index start_index+1, ie x[start_index+i].
This makes the code modular because it allows us to add variables
without having to update previous code.

the name is used to access the variable in other locations
as key in dictionaries.

the relative time step is an integer indicating how many base-time periods
are covered by one "row" of this variable. For instance, if the base time step
is half an hour and this variable exists once an hour, the value is 2.
It is used to "align" variables at the same time
see the Constraint-class for an example.
"""


class VariableType(Enum):
    CONTINUOUS = 0
    INTEGER = 1


class OptimisationVariable:
    def __init__(
        self,
        name: str,
        rel_time_step: int,
        lower_limit: np.ndarray,
        upper_limit: np.ndarray,
        objective_function: np.ndarray,
        variable_type: VariableType,
    ):
        self.name = name
        self.relative_time_step = rel_time_step
        self.start_index = (
            -99
        )  # set by the OptimisationModel, set an integer to placate the type checking
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.objective_function = objective_function
        self.variable_type = variable_type

        assert len(lower_limit) == len(upper_limit), (
            "upper and lower limit must have the same length"
        )
        assert len(lower_limit) == len(objective_function), (
            "objective function must have the same length as the limit"
        )
