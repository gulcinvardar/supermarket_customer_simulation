
from math import floor
import pandas as pd
import numpy as np
import random

from pathlib import Path 
from datetime import datetime, timedelta

import customer_probs_matrix


class Customer:
    '''Manages the behavior of one customer'''

    def __init__(self, name, state):
        '''
        Instantiate the customer name and state. Name is customer no and state is customer location.
        Self states are all the sections of the supermarket
        '''
        self.name = name
        self.state = state
        self.states = ['checkout', 'dairy', 'drinks', 'fruit', 'spices']
        
    
    def initial_state(self):
        '''
        The first move of the customer based on random choice with calculated from checkout to other locations transition matrix.
        The transition matrix calculated in customer_probs_matrix.py.
        The transition from checkout to another location is representative of the next customers first appearance.
        '''
        self.state = random.choices(self.states, weights=customer_probs_matrix.probs['checkout'])[0]

    def next_state(self):
        '''
        The next moves of the customers based on the transition matrix calculated in customer_probs_matrix.py.
        '''
        self.state = random.choices(self.states, weights=customer_probs_matrix.probs[self.state])[0]

    def __repr__(self):
        return f'Customer {self.name} in {self.state}'


class Supermarket():
    '''Manages multiple Customer instances that are currently in the market.'''

    def __init__(self):
        '''
        Customers: list of customer objects. Time: current time, 
        last time: closing time of the market, last_id: number of last entered customer,
        minutes: minutes passed, hours: the hour of the day
        cus_range: random selection ranges of new entries
        columns: columns of final csv, df: df of final csv.
        '''         
        self.customers = []
        self.time = 0
        self.last_time = 0
        self.minutes = 0
        self.first_time = 7
        self.hours = 7
        self.last_id = 0
        self.cus_ranges = [1, 2, 3, 4]
        self.cus_range = 0
        self.columns = ['timestamp','customer_no','location']
        self.df = pd.DataFrame(columns = self.columns)

    def opening_time(self):
        '''
        Opening time in d/m/y HH:MM format
        '''
        time_str = '4/5/2022 7:0:0'
        date_format_str = '%d/%m/%Y %H:%M:%S'
        self.time = datetime.strptime(time_str, date_format_str)

        return self.time

    def closing_time(self):
        '''
        Closing time in d/m/y HH:MM format.
        '''
        time_str = '4/5/2022 21:0:0'
        date_format_str = '%d/%m/%Y %H:%M:%S'
        self.last_time = datetime.strptime(time_str, date_format_str)

        return self.last_time
    
    def next_minute(self):
        '''
        Streams the time and retrieves the hour of the day.
        '''
        self.time = self.time + timedelta(minutes=1)
        self.minutes = self.minutes + 1
        if self.hours < 21:
            self.hours = self.first_time + round(self.minutes/60)
        else:
            self.hours = self.first_time + floor(self.minutes/60)

        return self.time, self.hours
        
    def initial_customers(self):
        '''
        Creates 3 customers to start with.
        '''
        for i in range(1,4):
            customer = Customer(i, 'entrance')
            self.customers.append(customer)
            self.last_id += 1

        return self.customers, self.last_id


    def new_entry_prob(self):

        self.cus_range = random.choices(self.cus_ranges, weights=customer_probs_matrix.probs_time[self.hours])[0]

        return self.cus_range 

    def add_customers2(self):
        '''
        Randomly creates new customers.
        The number varies based on the hour of the day.
        '''
        self.cus_range = self.new_entry_prob()
        for i in range(self.cus_range):
            customer = Customer(self.last_id+1, 'entrance')
            self.customers.append(customer)
            self.last_id += 1
        
        return self.customers, self.last_id

    def remove_exiting_customers(self):
        '''
        Removes customers after they check-out.
        '''
        for customer in self.customers:
            if customer.state == 'checkout':
                self.customers.remove(customer)

        return self.customers

    def get_customer_list(self):
        '''
        Creates a dataframe with all customers, time, and location.
        '''
        timestamps = []
        customer_no =[]
        location = []
        
        for customer in self.customers:
            timestamps.append(self.time)
            customer_no.append(customer.name)
            location.append(customer.state)

        customer_list = pd.DataFrame(list(zip(timestamps, customer_no, location)), columns = self.columns)

        return customer_list
    
    def move_customers(self):
        '''
        Moves customers into a new location. Checked-out customers are removed.
        '''
        self.remove_exiting_customers()
        timestamp = self.next_minute()
        timestamps = []
        customer_no= []
        location = []
        for customer in self.customers:
            if customer.state == 'entrance':
                customer.initial_state()
            else:
                customer.next_state()
            timestamps.append(timestamp)
            customer_no.append(customer.name)
            location.append(customer.state)

    def concat_dataframe(self):
        '''
        Creates and updates the customer dataframe.
        '''
        self.df = pd.concat([self.df, self.get_customer_list()])
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        
        return self.df

    def print_customers(self):
        '''
        Writes the customer dataframe into csv and saves it into the designated folder.
        '''
        filepath = Path('/Users/gulcinvardar/Desktop/Data_Science_Bootcamp/stationary-sriracha-student-code/projects/week_8/customer_data') 
        self.df.to_csv(f'{filepath}/customer_simulation_time.csv', sep = ';', index=False)

    def operate(self):
        '''
        Runs the supermarket from opening to closing time.
        '''
        self.opening_time()
        self.closing_time()
        self.initial_customers()
        self.move_customers()
        self.concat_dataframe()
        while self.time < self.last_time: 
            self.add_customers2()
            self.move_customers()
            self.concat_dataframe()        
        self.print_customers()

        
    def __repr__(self):
        return f'Supermarket opens at {self.time}'
        
        
    

penny = Supermarket()
penny.operate()
