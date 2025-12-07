"""
A constraint in the optimisation model

For now we only support basic constraints which are valid at each point in time
eg lower_lim <= a*x1[t] + b*x2[t] <= upper_lim
with constant values of lower_lim, upper_lim, a and b.

We do support variables at different time steps using the relative_time_step
property of a variable.
eg supose x2 has an hourly time step while x1 has an half-hourly.
In that case x2.relative_time_step = 2
lower_lim <= x1[t] + x2[floor(t / x2.relative_time_step)] <= upper_lim

We do not yet implement functionality for constraints that are different
at different points in time, or for constraints that rely on previous time
steps. This means the SoC constraint needs to be added manually.

As was the case with the settings-class, all fields are left as
public for simplicity. They could be made private and accessed through getters
"""


class OptimisationConstraint:
    def __init__(
        self,
        name: str,
        variable_factors: dict[str, float],
        lower_limit: float,
        upper_limit: float,
    ):
        self.name = name
        self.variable_factors = variable_factors

        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
