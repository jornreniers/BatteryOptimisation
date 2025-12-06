import pandas as pd
from src import Settings

"""
Read and preprocess the data

Due to the low complexity this is all in one function rather than an ETL pipeline.
"""


def preprocess_run() -> list[pd.DataFrame]:
    sets = Settings.Settings()

    dfs = []
    for i in range(len(sets.data_file_sheets)):
        df = pd.read_excel(
            sets.data_file,
            sheet_name=sets.data_file_sheets[i],
            parse_dates=[sets.data_file_colname_time],
        )

        # Rename columns to be easier to handle
        df.rename(
            columns={
                sets.data_file_colname_time: sets.data_struct_colname_time,
                sets.data_file_colname_prices[i]: sets.data_struct_colname_price,
            },
            inplace=True,
        )
        dfs.append(df)

    return dfs
