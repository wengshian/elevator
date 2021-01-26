from passenger import *
from collections import defaultdict, OrderedDict
import heapq

#Global Variables that can be changed
OPENTIME = 5 #Time it takes for elevator doors to open at any floor
LOBBYTIME = 30 #Time it takes for elevator doors to open at lobby

class Elevator:
    """
    This class represents an individual elevator and just figures out how to load and unload passengers.
    This class will only interact with the Otis class and nothing else.
    """
    def __init__(self, start, id, max_passengers = 10, verbose = False, pick_up_mode = "requests"):
        self.current = start #current floor elevator is on
        self.id = id #Unique id for elevator
        self.time = 0 #current time (Each unit is in seconds)
        self.num_passengers = 0 #Number of passengers
        self.verbose = verbose #Verbose mode for more exact logs
        self.max_passengers = max_passengers
        self.current_state = "idle" #Different states:
        #idle: Elevator has no direction 
        #moving: Elevator is moving
        #transferring: Elevator is either dropping off or picking up passengers
        
        #To keep track of current passengers in elevator
        self.current_passengers = defaultdict(list) #Map of destination to passenger
        self.dest_floors = set() #set of destinations of existing passengers

        #To keep track of which passengers to pick up
        self.pick_up = defaultdict(list) #Map of pick up floor to passenger
        self.pick_up_floors = set() #set of floors to pick up passengers from
        self.pick_up_metric = 0 #Pick-up metric for elevator to determine how busy elevator is
        self.pick_up_mode = pick_up_mode #Metric mode to figure out how many pickups elevator has

        #To keep track of passengers who have been waiting when the elevator was full
        self.priority = OrderedDict() #Will be used as an OrderedSet to put passengers in it

        #To keep track of direction of elevator
        self.direction = 0 #Direction of elevator( 0: idle, 1: going up, -1: going down)
        self.prev_direction = 0 #Keep track of previous direction before direction change

        self.current_log = "Elevator {} is at {} with dir {}".format(self.id, self.current, self.direction) #Current log line
        self.all_logs = defaultdict(list) #Logs to save all states
    
    def add(self, passenger):
        #Adding the passenger to be picked up
        self.pick_up[passenger.depart].append(passenger)
        self.pick_up_floors.add(passenger.depart)
        self.mod_pick_up_metric(passenger, add = True)
    
    def pickup(self):
        #When passenger/s has been picked up
        picked_up_passengers = self.pick_up[self.current]
        self.pick_up[self.current] = []
        self.pick_up_floors.remove(self.current)
        #Add new passengers
        for new_passenger in picked_up_passengers:
            if self.num_passengers + new_passenger.num <= self.max_passengers:
                self.num_passengers += new_passenger.num #Add to elevator number of passengers
                self.current_passengers[new_passenger.to].append(new_passenger)
                self.dest_floors.add(new_passenger.to)
                self.mod_pick_up_metric(new_passenger, add = False) #Reduce pick-up metric since passenger has been picked up
                new_passenger._pickup(self.time) #Update passenger info
                if new_passenger in self.priority:
                    self.priority.pop(new_passenger) #Remove passenger from priority queue
            else:
                self.pick_up[self.current].append(new_passenger) #Add it back into the pick-up queue
                self.pick_up_floors.add(self.current) #Add it back into pick-up floors set
                if new_passenger not in self.priority:
                    self.priority[new_passenger] = self.time #Add it into the priority ordered set

    def mod_pick_up_metric(self, passenger, add = True):
        #Function to change the pick_up metric to be used in the Otis allocator
        #There are 2 ways each elevator's pick-up load can be calculated:
        #1) requests: Number of pickup passenger requests (default)
        #2) num_passengers: Total number of passengers to pickup
        multiplier = 1 if add else -1
        if self.pick_up_mode == "requests":
            self.pick_up_metric += multiplier*1
        elif self.pick_up_mode == "num_passengers":
            self.pick_up_metric += multiplier*passenger.num

    def dropoff(self):
        #Drop off the passenger
        drop_off_passengers = self.current_passengers[self.current]
        self.current_passengers[self.current] = []
        self.dest_floors.remove(self.current) #Remove destination
        for old_passenger in drop_off_passengers:
            self.num_passengers -= old_passenger.num #Reduce current lift passengers
            old_passenger._complete(self.time)
    
    def update_state(self):
        #Elevator update state and direction of elevator
        self.current = self.current + self.direction #Update floor of elevator

        #Check if pick-up or dropoff and also handle the time buffer of opening and closing of elevator
        if self.current in self.dest_floors or self.check_pick_up():
            #Need to buffer for opening/closing of elevator doors
            if self.current_state != "transferring":
                self.current_state = "transferring"
                if self.current == 1: #Account for lobby
                    self.buffer_time = LOBBYTIME
                else:
                    self.buffer_time = OPENTIME
                self.prev_direction = self.direction
                self.direction = 0
                if self.current in self.dest_floors:
                    self.current_log = "Action (Elevator {}): Dropping-off passengers at floor {} at t= {}s with {}s left \n".format(self.id, self.current, self.time, self.buffer_time)
                else:
                    self.current_log = "Action (Elevator {}): Picking up passengers at floor {} at t= {}s with {}s left \n".format(self.id, self.current, self.time, self.buffer_time)
            else:
                if self.buffer_time == 0:
                    if self.current in self.dest_floors and self.check_pick_up():
                        self.dropoff()
                        self.pickup()
                        self.current_log = "Action (Elevator {}): Dropped-off and picked up passengers at floor {} at t= {}s \n".format(self.id, self.current, self.time)
                    elif self.check_pick_up():
                        self.pickup()
                        self.current_log = "Action (Elevator {}): Picked-up passengers at floor {} at t= {}s \n".format(self.id, self.current, self.time)
                    else:
                        self.dropoff()
                        self.current_log = "Action (Elevator {}): Dropped-off passengers at floor {} at t= {}s \n".format(self.id, self.current, self.time)
                    self.update_direction()
                    
                else:
                    self.current_log = "Action (Elevator {}): Waiting for doors to open with {}s left at floor {} at t= {}s \n".format(self.id, self.buffer_time, self.current, self.time-1)
                    self.buffer_time -=1
        else:
            #Update current state and direction
            self.update_direction()
            self.current_log = "Action (Elevator {}): Current Direction {}, at floor {} at t= {}s \n".format(self.id, self.direction, self.current,self.time)
        
        self.print_log_actions()
        if self.verbose:
            print(self.current_log)
        self.time += 1

    def check_pick_up(self):
        #To check if elevator can pick up at current floor.
        if self.current not in self.pick_up_floors:
            return False #No pick ups to be made on floor
        #1)Unload passengers on floor first to check capacity
        capacity = self.num_passengers
        for unload in self.current_passengers[self.current]:
            capacity -= unload.num

        #2)To make sure that capacity + fairness feature gets implemented
        #Elevator continues to travel until it reaches the request that has waited the longest 
        if len(self.priority) >0:
            top =  next(iter(self.priority))
            if self.current != top.depart:
                return False
            else:
                return True
        
        #3)Then check if passengers on floor can be loaded. As long as one query can be fufilled --> return True
        for pickup in self.pick_up[self.current]:
            new_capacity = capacity + pickup.num
            if new_capacity <= self.max_passengers:
                return True
        for pickup in self.pick_up[self.current]:
            self.priority[pickup] = self.time
        return False
                  
    def update_direction(self):
        if len(self.pick_up_floors) + len(self.dest_floors) == 0:
            self.direction = 0 #Elevator currently has no pending requests.
            self.current_state ="idle"
        elif self.current > max(self.pick_up_floors | self.dest_floors) or self.current == 100:
            self.direction = -1 #Elevator has reached max request floors or is currently at the highest floor
            self.current_state = "moving"
        elif self.current < min(self.pick_up_floors | self.dest_floors) or self.current == 1:
            self.direction = 1 #Elevator has reached min request floors or is at lobby
            self.current_state = "moving"
        else:
            if self.direction == 0:
                #Elevator was either idle or was transferring passengers
                #This is where self.priority can influence the direction
                if self.priority:
                    #There are passengers who haven't been able to get on the elevator due to capacity constraints
                    top = next(iter(self.priority))
                    if self.num_passengers + top.num <= self.max_passengers:
                        self.direction = -1 if top.depart < self.current else 1 #Direct elevator to passenger 
                    else:
                        self.direction = self.prev_direction
                else:
                    self.direction = self.prev_direction
            else:
                self.direction = self.direction #Continue with previous direction
            self.current_state = "moving"
    
    def print_log_actions(self):
        #Add states into elevator log
        self.all_logs["floor"].append(self.current)
        self.all_logs["num_passengers"].append(self.num_passengers)
        self.all_logs["state"].append(self.current_state)
        self.all_logs["direction"].append(self.direction)
        self.all_logs["time"].append(self.time)
        print("Elevator ID: ",self.id, "Time:",  self.time, "Floor: ", self.current, "num_passengers: ", self.num_passengers, "Direction: ", self.direction, "State: ", self.current_state,"Dest: ", list(self.dest_floors), "Pick up: ", list(self.pick_up_floors))

class Otis:
    """
    This class (named after one of the largest elevators in the world) will handle all the elevators.
    This is the elevator interface that will interact with any simulations.
    It will decide how to allocate passenger requests. 
    """

    def __init__(self, verbose = False, elevator_num = 3, pick_up_mode = "requests"):
        self.time_idx = [] #List to keep track of time idx
        self.current_time = 0 #Current time
        self.all_idle = True #True when all elevators handled by Otis are idle. Idle initially since no requests yet.
        self.verbose = verbose
        self.elevator_num = elevator_num
        self.pick_up_mode = pick_up_mode
        self.__init_elevators()
    
    def __init_elevators(self):
        self.elevators = [] #To store elevators
        self.elevator_heap = [] #Shall use an elevator heap to keep track of priority. Used to prevent over-complication of Elevator Class
        for elevator_num in range(self.elevator_num):
            new_elevator = Elevator(1, id = elevator_num, verbose = self.verbose, pick_up_mode = self.pick_up_mode)
            heapq.heappush(self.elevator_heap, (0, new_elevator.id)) #Priority based on num passengers to pick-up
            self.elevators.append(new_elevator)
        self.valid_elevators = self.elevators

    def process_request(self,passenger):
        #Allocation of passenger request to elevators

        #Logic: Request will be allocated based on how many pick-up floors each elevator has.
        #Criterion: 
        #1) First by pick-up load (Not total number of passengers in pick-up floor)
        #2) Convenience: Which is dictated by whether the elevator is moving in the direction of the requested pick-up floor
        temp_heap = []
        allocated = False
        while self.elevator_heap:
            _, elevator_id = heapq.heappop(self.elevator_heap)
            curr_elevator = self.elevators[elevator_id]
            if allocated:
                heapq.heappush(temp_heap, (curr_elevator.pick_up_metric, elevator_id))
            else:
                curr_elevator_dir = curr_elevator.direction
                if passenger.to == curr_elevator.current and curr_elevator.num_passengers + passenger.num <= curr_elevator.max_passengers:
                    #Since elevator is already at floor, just add it
                    curr_elevator.add(passenger)
                    allocated = True
                elif passenger.to < curr_elevator.current:
                    if curr_elevator_dir == -1 or curr_elevator_dir == 0:
                        curr_elevator.add(passenger)
                        allocated = True
                elif passenger.to > curr_elevator.current:
                    if curr_elevator_dir == 1 or curr_elevator_dir == 0:
                        curr_elevator.add(passenger)
                        allocated = True
                if allocated:
                    print("Added passenger query to elevator {}. Passenger info-> Pick-up: {} Dest: {} Num Passengers: {}, Start Time: {}".format(elevator_id, passenger.depart, passenger.to, passenger.num, passenger.start_time))
                heapq.heappush(temp_heap, (curr_elevator.pick_up_metric, elevator_id))
        if not allocated:
            #Add to the first elevator. The best we can do for now
            _, min_elevator_id = heapq.heappop(temp_heap)
            min_elevator = self.elevators[min_elevator_id]
            min_elevator.add(passenger)
            print("Added passenger query to elevator {}. Passenger info->  Pick-up Floor: {} Dest Floor: {} Num Passengers: {}, Start Time: {}".format(min_elevator_id, passenger.depart, passenger.to, passenger.num, passenger.start_time))
            heapq.heappush(temp_heap, (curr_elevator.pick_up_metric, min_elevator_id))
        self.elevator_heap = temp_heap

    def update(self):
        #Update individual elevators as well as the logs
        idle_list = []
        temp_heap = []
        for elevator_i in range(len(self.elevators)):
            elevator = self.elevators[elevator_i]
            elevator.update_state()
            heapq.heappush(temp_heap, (elevator.pick_up_metric, elevator_i)) #Update the elevator pick-up heap
            if elevator.current_state == "idle":
                idle_list.append(True)
            else: 
                idle_list.append(False)
        self.all_idle = all(idle_list) #To check if all requests have been completed.
        self.current_time += 1
        self.time_idx.append(self.current_time)
        self.elevator_heap = temp_heap #Update pick-up heap





    
