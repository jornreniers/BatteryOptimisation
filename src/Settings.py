"""
Settings of the project.

For simplicity, they are grouped into a single class.
This means ty recognises objects of the class,
knows which fields exists and you can auto-complete field name.

Due to time-constraints, the fields are left as public so they are easily accessible.
This means that some part of the code could change the values which would break the code.
A more thorough approach is to make the fields private and add a getter
for each to make the values readonly.
"""


class Settings:
    def __init__(
        self,
    ):
        # input data
        self.pmax_cha_MW = 2.0
        self.pmax_dis_MW = 2.0
        self.capacity_MWh = 4.0
        self.eta_cha = 0.95
        self.eta_dis = 0.95
        # assume over the 5000 cycles we need to write off the £50,000 cost
        # NOTE: happy to talk about better assumptions but I'm adding this in for now
        self.degradation_cost_gbpPerMWh = 500000 / 5000 / (2 * self.capacity_MWh)
        self.data_file = "Data/Attachment 2.xlsx"
        self.data_file_sheets = ["Half-hourly data", "Hourly data"]
        self.data_file_colname_time = "Unnamed: 0"
        self.data_file_colname_prices = [
            "Market 1 Price [£/MWh]",
            "Market 2 Price [£/MWh]",
        ]

        # processing
        self.data_struct_colname_time = "timestamp"
        self.data_struct_colname_price = "price"

        # model structure
        self.varname_halfhour_sell = "hh_sell"
        self.varname_halfhour_buy = "hh_buy"
        self.varname_hour_sell = "h_sell"
        self.varname_hour_buy = "h_buy"
        self.varname_power_sign = "sign"
        self.varname_soc = "soc"

        # assumptions
        self.soc_ini = 0.5  # initial SoC
