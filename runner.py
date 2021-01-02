from elevator import Otis
from passenger import *
import pandas as pd
import numpy as np
import random, math
from scipy.stats import truncnorm

class Simulator:
    """
    This class will handle the main simulation. It will handle:
    1) Simulation of input data
    2) Calling of the Otis class
    3) Running the simulation with Otis
    4) Getting the summary stats
    """
    def __init__(self, request_length = 3, pick_up_mode = "requests", verbose = False, test_data = None, random_seed = 1, lobby_prob = 0.2):
        #Elevator/Otis configuration
        self.verbose = verbose
        self.pick_up_mode = pick_up_mode
        #Test Data configuration
        self.test_data = test_data #Test data for custom mode
        self.request_length = request_length #Length of simulation mode data
        self.random_seed = random_seed #Random seed
        self.lobby_prob = lobby_prob #Probability of lobby being chosen


    def simulate_data(self):
        random.seed(self.random_seed)
        data_list = []
        min_t = 1
        #Generate num_passengers
        random_func = truncnorm(-math.inf, math.log(5)) #Given lognormal with bounds (0,5] --> equivalent to a truncated normal (-inf, ln5]
        random_passengers = np.ceil(math.e**(random_func.rvs(size = self.request_length, random_state= self.random_seed)))

        for i in range(self.request_length):
            lobby_test = random.uniform(0,1)
            #lobby_prob chance of lobby being chosen
            pickup_floor = 1 if lobby_test < (self.lobby_prob ) else random.randrange(2,100)
            dropoff_floor = pickup_floor
            time = random.randint(min_t, min_t + 4) #Randomly choosing if current timestamp has a request. Could make this more flexible
            while dropoff_floor == pickup_floor:
                #Have to make sure dropoff and pickup are different
                lobby_test = random.uniform(0,1)
                dropoff_floor = 1 if lobby_test < (self.lobby_prob) else random.randrange(2,100)
            data_list.append((pickup_floor, dropoff_floor, int(time), int(random_passengers[i])))
            min_t = time
        if self.verbose:
            print("Random Data Set ..., \n")
            print(data_list)
        return data_list


    def run(self, mode = "simulate"):
        #Main runner function to run simulation.

        #1) Get data
        if mode == "test":
            data = self.test_data
        elif mode == "simulate":
            data = self.simulate_data()
        
        #Transform it into a dataframe for faster processing
        data = pd.DataFrame(data)
        data = data.rename(columns = {0: "pick-up", 1:"drop-off", 2:"time", 3:"num_passengers" })
        data_time = data.groupby("time")
        self.all_passengers = []

        #2) Call Otis Class
        self.test_otis = Otis(verbose = self.verbose, pick_up_mode = self.pick_up_mode)

        #3) Transform data into passenger requests
        for time, points in data_time:
            while time > self.test_otis.current_time:
                print("t = {}s...".format(self.test_otis.current_time))
                self.test_otis.update()
            print("t = {}s...".format(self.test_otis.current_time))
            for _, point in points.iterrows():
                passenger = Passenger(point.loc["pick-up"], point.loc["drop-off"], point.loc["time"], point.loc["num_passengers"])
                self.test_otis.process_request(passenger)
                self.all_passengers.append(passenger)
            self.test_otis.update()

        #4) Continue running simulation until all requests have been completed
        while not self.test_otis.all_idle:
            print("t = {}s...".format(self.test_otis.current_time))
            self.test_otis.update()
    
    def fetch_summary_stats(self):
        #Stats per passenger
        #For time statistics, we have average as well as standard deviation to track performance of Elevator/Otis algo
        total_wait_time = np.array([])
        total_elevator_time = np.array([])
        total_time = np.array([])
        total_passengers = 0
        total_queries = 0
        for passenger in self.all_passengers:
            wait_time = passenger.wait_time
            elevator_time = passenger.travel_time
            trip_time = wait_time + elevator_time
            num_passengers = passenger.num
            if self.verbose:
                print("Wait Time: ", wait_time, "Travel Time: ", elevator_time, "Trip Time: ", trip_time, "Start Time: ", passenger.start_time, "Depart Floor: ", passenger.depart, "Dest Floor: ", passenger.to)

            total_wait_time = np.append(total_wait_time, [wait_time] * num_passengers)
            total_elevator_time = np.append(total_elevator_time, [elevator_time] * num_passengers)
            total_time = np.append(total_time, [trip_time] * num_passengers)
            total_passengers += num_passengers
            total_queries += 1
        
        pd.options.display.max_columns = None
        if total_passengers == 0:
            self.summary_df = pd.DataFrame({"Average Wait Time": [0], "Variance Wait Time": [0], \
                "Average Travel Time": [0], "SD Travel Time": [0],\
                    "Average Total Time": [0], "SD Total Time": [0],\
                        "Total Passengers": [0], \
                            "Total Queries": [0]}, index = ["Summary"])
        else:
            self.summary_df = pd.DataFrame({"Average Wait Time": [np.sum(total_wait_time)/total_passengers],
            "SD Wait Time": [(np.sum(total_wait_time**2)/total_passengers - (np.sum(total_wait_time)/total_passengers)**2)**0.5],
            "Average Travel Time": [np.sum(total_elevator_time)/total_passengers],
            "SD Travel Time": [(np.sum(total_elevator_time**2)/total_passengers - (np.sum(total_elevator_time)/total_passengers)**2)**0.5],
            "Average Total Time": [np.sum(total_time)/total_passengers],
            "SD Total Time": [(np.sum(total_time**2)/total_passengers - (np.sum(total_time)/total_passengers)**2)**0.5],
            "Total Passengers": [total_passengers],
            "Total Queries": [total_queries]}, index = ["Summary"])

