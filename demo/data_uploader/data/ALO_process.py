#!/usr/bin/env python3

import pandas

# daily resampling
##################

df = pandas.read_csv('ALO.csv', index_col='valid')
df.index.rename('ts', inplace=True)  # rename datetime field to 'ts'
df.index = pandas.to_datetime(df.index)  # convert it to datetime

rs = df.resample('1D').mean()  # resample the data to daily averages

# earlier dates contain very large periods of missing data, so we will only
# consider the date since March 1960
rs = rs.loc['1960-03-01':]
rs.to_csv('ALO_daily.csv')

# weekly resampling
###################

df = pandas.read_csv('ALO.csv', index_col='valid')
df.index.rename('ts', inplace=True)  # rename datetime field to 'ts'
df.index = pandas.to_datetime(df.index)  # convert it to datetime

# w = df.resample('W-MON', label='left') # can be used so that the timestamp is at the start of the week
w = df.resample('W-MON')  # resample the data to daily averages
rs = w.mean()

# earlier dates contain very large periods of missing data, so we will only
# consider the date since March 1960
rs = rs.loc['1960-03-01':]
rs.to_csv('ALO_weekly.csv')

# filter missing values
#######################

df = pandas.read_csv('ALO.csv', index_col='valid')
df.index.rename('ts', inplace=True)  # rename datetime field to 'ts'
df.index = pandas.to_datetime(df.index)  # convert it to datetime

# drop missing values
df.dropna()

# earlier dates contain very large periods of missing data, so we will only
# consider the date since March 1960
df = df.loc['1960-03-01':]
df.to_csv('ALO_filtered.csv')
