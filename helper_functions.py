import datetime
import numpy as np
import pandas as pd

def date_range(date1, date2):
    date1 = datetime.date.fromisoformat(date1)
    date2 = datetime.date.fromisoformat(date2)
    dates = []
    for n in range(int ((date2 - date1).days)+1):
        dates.append((date1 + datetime.timedelta(n)).isoformat())
    return dates


def color_interval_nonoverlap(df, start, end, color):
    zero_index = 0
    last_date = df.columns.tolist()[-2]
    first_date = df.columns.tolist()[0]
    for i in range(len(start)):
        date_list = date_range(start[i], end[i])

        # get time interval values
        values = df.loc[zero_index, date_list]

        # fill up new trace
        nan_array = np.empty(len(df.columns))
        nan_array[:] = np.NaN
        new_position = len(df.index)
        df.loc[new_position] = nan_array
        df.loc[new_position, date_list] = values
        df.loc[new_position, "color"] = color[i]

        date_list_from_start = date_range(start[i], last_date)
        date_list_from_end = date_range((datetime.date.fromisoformat(end[i]) + datetime.timedelta(1)).isoformat(),
                                        last_date)

        nan_array = np.empty(len(date_list_from_start))
        nan_array[:] = np.NaN
        values = df.loc[zero_index, date_list_from_end]
        zero_color = df.at[zero_index, "color"]
        df.loc[zero_index, date_list_from_start] = nan_array
        zero_index = len(df.index)
        df.loc[zero_index, date_list_from_end] = values
        df.at[zero_index, "color"] = zero_color

    return df

def color_interval(df,start, end, color):
    date_list = date_range(start, end)
    values = df.loc[0,date_list]
    nan_array = np.empty(len(date_list))
    nan_array[:] = np.NaN
    #df.loc[0,date_list] = nan_array
    nan_array = np.empty(len(df.columns))
    nan_array[:] = np.NaN
    new_position = len(df.index)
    df.loc[new_position] = nan_array
    df.loc[new_position,date_list] = values
    df.loc[new_position,"color"] = color
    return df