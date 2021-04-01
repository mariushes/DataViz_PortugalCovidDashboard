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