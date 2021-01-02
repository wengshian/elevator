# Documentation:


There are 4 Classes:

1) **Elevator**: Atomic class to represent a single elevator cart. Will only be called and handled by Otis <br/>
a) `add':<br/>
--> To add a passenger in its pick_up dictionary when Otis allocates a request to the Elevator.<br/>
b) `pickup':<br/>
--> When a passenger has been picked up. Handles moving the passenger into the current_passengers dict<br/>
c) `dropoff':<br/>
--> When a passenger is dropped off at the destination.<br/>
d) `update_direction':<br/>
--> To handle the direction of the elevator at any point in time.<br/>
--> This is where I have tried to implement the capacity + fairness feature (albeit not perfect).<br/>
e) `update_state':<br/>
--> To handle the update of the Elevator's state and time, the opening and closing of elevator doors as well as unloading of passengers<br/>
--> pickup, dropoff, update_direction are nested in this function<br/>

2) **Otis**: Handles all 3 elevators<br/>
a) 'process_request':<br/>
--> Allocates passenger requests to Elevators and is called in the Simulator function.<br/>
--> Criterion:<br/>
i) Pickup load: First by number of pickup requests using a heap<br/>
ii) Convenience: Dictated by whether the elevator is moving in the direction of the requested pick-up floor<br/>
b) 'update':<br/>
--> Handles the updating of all elevators and is called in the Simulator function<br/>

3) **Simulator**: Interface to run simulations<br/>
a) 'simulate_data':<br/>
--> to simulate data according to given parameters (not completed yet)<br/>
b) 'run':<br/>
--> main runner function<br/>
--> runner does these 4 things:<br/>
i) Get data<br/>
ii) Call the Otis class<br/>
iii) Transform the data into passenger requests which are then given to Otis for allocation to Elevators<br/>
iv) Continue running the simulation until all requests have been completed<br/>
c) 'fetch_summary_stats':<br/>
--> Aggregate stats per passenger and print out the summary table<br/>

4) **Passenger**: Contains information for lift request<br/>


## Limitations/Assumptions:
- Simulation not configurable for now in terms of frequency per second
- Assume that once a query is received,  elevator immediately reacts to it.
- Passengers of the same query will enter the same elevator at the same time 
- In terms of Capacity + Fairness: Implementation is not perfect as only elevator direction will be influenced
- Optimization not perfect as passenger request's destination floor is not considered when being added to an elevevator
- Assume that to passenger, utility of waiting 1s for the elevator == utility of travelling 1s in the elevator
- Given that a lognormal dist for num_passengers must be in the range of (0,5], shall assume that the transformed normal distribution has mean = 0, sd =1 before its truncation to (-inf, log(5)] 

## How to run:
- `simulate`: Whether to use simulation or custom data
- `pick_up_mode`: Method to calculate elevator pick-up load. 2 options: "requests", "num_passengers"
- `length`: Number of simulation data points to use if simulate is set to True
- `verbose`: Turn on extra logging
- `seed`: Random seed to use to ensure replicability
- `lobby_prob`: Probability lobby is chosen (Has to be less than 1)
- `test_case`: Custom test case to use if simulate is set to False
- Sample command to run:
`python3 test.py --simulate True --pick_up_mode requests --length 3 --verbose False --seed 0 --lobby_prob 0.5`

## Output format:
- `Elevator ID`: Elevator being logged
- `Time` : Current time stamp
- `Floor` : Floor elevator is on
- `num_passengers` : Number of passengers in elevator
- `Direction`: Direction of elevator, 1 for going up, -1 for going down and 0 for being idle
- `Dest`: Destination floors of passengers in elevator
- `Pick up`: Floors of passengers to pick-up
