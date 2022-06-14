import pandas as pd
import numpy as np
import random
import seaborn as sns
import matplotlib.pyplot as plt


def read_csv():
    '''
    Reads the csvs one by one and retrives them sorted with the customer number for each day and the timestamp.  
    Adds an extra column for unique customer id produced by shopping day info and daily customer no.
    '''
    df = pd.DataFrame()
    for df_name in df_names:
        df_day = pd.read_csv(f'/Users/gulcinvardar/Desktop/Data_Science_Bootcamp/stationary-sriracha-student-code/projects/week_8/customer_data/{df_name}.csv', sep = ';', parse_dates=True).sort_values(['customer_no', 'timestamp']).set_index('timestamp')
        df_day['shopping_day'] = df_name [0:2]
        df = pd.concat([df, df_day])
        df['customer_id'] = df['shopping_day'] + '_' + df['customer_no'].astype('str')
        df['next_location'] = df['location'].shift(-1)

    return df


def clean_data(df):
    '''Removes the customers who never checked out'''
    df = df.iloc[ : 24875].reset_index()
    df_all = df.copy()
    for i in range(len(df) - 2):
        if df['customer_id'][i+1] != df['customer_id'][i]:
            if df['location'][i] != 'checkout':
                df_all = df_all.drop(df_all[df_all['customer_id'] == df['customer_id'].iloc[i]].index)
    df_all = df_all.set_index('timestamp')

    return df_all


def transition_matrix(df):
    '''Calculates the transition probabilities among supermarket locations and retrieves it as a dictionary'''
    P = pd.crosstab(
        df['location'], 
        df['next_location'], normalize='index')
    probs = P.to_dict(orient='index')
    for key in probs.keys():
        probs[key] = list(probs[key].values())

    return probs

def groupby_location(df):
    df_eda = pd.DataFrame(df.groupby(['timestamp', 'location'])['customer_id'].count()).unstack(1)
    df_eda.columns = df_eda.columns.get_level_values(-1)
    df_eda.index = pd.DatetimeIndex(df_eda.index)
    df_eda['hour'] = df_eda.index.hour
    df_eda['day'] = df_eda.index.day
    df_eda['day_name'] = df_eda.index.day_name()
    
    return df_eda

def time_cus_probabilty(df):
    '''Calculates the probaibility of the number of customer(1,2,3,or 4) based on time.
    It's a rough estimation.
    '''
    P_time = pd.crosstab(
        df['hour'], 
        df['checkout'], normalize='index')
    nameslist = ['A','B','C','D', 'E', 'F', 'G', 'H', 'I']
    P_time.columns = nameslist
    P_time[0]= P_time['A']
    P_time[1]= P_time['B'] + P_time['C'] + P_time['D']
    P_time[2]= P_time['E'] + P_time['F'] + P_time['G']
    P_time[3]= P_time['H'] + P_time['I']
    P_time = P_time.drop(columns = nameslist)
    probs_time = P_time.to_dict(orient='index')
    for key in probs_time.keys():
        probs_time[key] = list(probs_time[key].values())

    return probs_time
    






df_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
df = read_csv()
df_all = clean_data(df)
df_eda = groupby_location(df_all)
probs = transition_matrix(df_all)
probs_time = time_cus_probabilty(df_eda)



