Documentation:


There are 4 Classes:

1) Elevator: Atomic class to represent a single elevator cart. Will only be called and handled by Otis
a) add:
--> To add a passenger in its pick_up dictionary when Otis allocates a request to the Elevator.
b) pickup:
--> When a passenger has been picked up. Handles moving the passenger into the current_passengers dict
c) dropoff:
--> When a passenger is dropped off at the destination.
d) update_direction:
--> To handle the direction of the elevator at any point in time.
--> This is where I have tried to implement the capacity + fairness feature (albeit not perfect).
e) update_state:
--> To handle the update of the Elevator's state and time, the opening and closing of elevator doors as well as unloading of passengers
--> pickup, dropoff, update_direction are nested in this function

2) Otis: Handles all 3 elevators 
a) process_request:
--> Allocates passenger requests to Elevators and is called in the Simulator function.
--> Criterion:
i) Pickup load: First by number of pickup requests using a heap
ii) Convenience: Dictated by whether the elevator is moving in the direction of the requested pick-up floor
b) update:
--> Handles the updating of all elevators and is called in the Simulator function

3) Simulator: Interface to run simulations
a) simulate_data:
--> to simulate data according to given parameters (not completed yet)
b) run:
--> main runner function
--> runner does these 4 things:
i) Get data
ii) Call the Otis class
iii) Transform the data into passenger requests which are then given to Otis for allocation to Elevators
iv) Continue running the simulation until all requests have been completed
c) fetch_summary_stats:
--> Aggregate stats per passenger and print out the summary table

4) Passenger: Contains information for lift request


Limitations/Assumptions:
- Simulation not configurable for now in terms of frequency per second
- Assume that once a query is received,  elevator immediately reacts to it.
- Passengers of the same query will enter the same elevator at the same time 
- In terms of Capacity + Fairness: Implementation is not perfect as only elevator direction will be influenced
- Optimization not perfect as passenger request's destination floor is not considered when being added to an elevevator
- Assume that to passenger, utility of waiting 1s for the elevator == utility of travelling 1s in the elevator
- Given that a lognormal dist for num_passengers must be in the range of (0,5], shall assume that the transformed normal distribution has mean = 0, sd =1 before its truncation to (-inf, log(5)] 

How to run:
-simulate: Whether to use simulation or custom data
-pick_up_mode: Method to calculate elevator pick-up load. 2 options: "requests", "num_passengers"
-length: Number of simulation data points to use if simulate is set to True
-verbose: Turn on extra logging
-seed: Random seed to use to ensure replicability
-lobby_prob: Probability lobby is chosen (Has to be less than 1)
-test_case: Custom test case to use if simulate is set to False

python3 test.py --simulate True --pick_up_mode requests --length 3 --verbose False --seed 0 --lobby_prob 0.5
