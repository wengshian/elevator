from runner import *
import argparse

#Each request is given by a tuple: (pick_up_floor, drop_off_floor, time of request, number of passengers)
test_case_1 = [(1,100,5,2)] #Test one simple case
test_case_2 = [(1,100,5,2), (1,100,5,2), (1,100,5,2)] #Test similar cases to make sure it takes the same amount of time as test_case 1
test_case_3 = [(2,10, i, 5) for i in range(1,4)] #Test case where there are exactly 3 different elevator requests that are the same
test_case_4 = [(3, 4, 1, 5), (4,10,2,5), (4,10,3,5), (4,10,4,5) , (4,10,5,5)] #Test pick up and drop-off at the same floor
test_case_5 = [(2,10,1,5), (3,10,2,5), (4,5,3,5), (6,2,6,5), (8,2,7,5), (3,5,8,5),(4,8,9,5), (7,32,15,1)] #Test with a small sample 
test_case_6 = [(1,100,5,2), (1,100,7,2), (1,100,8,2)]
test_case_7 = [(1,100,1,2), (100,1,10,5), (1,100,18,2)]
test_case_8 = [(2,10, 10, 5) for i in range(12)] #Test case with all queries coming in at the same time
test_case_9 = [(2,10, 1, 5) for i in range(12)] +  [(8,11, 3, 5) for i in range(12)]+  [(9,12, 5, 5) for i in range(3)] #Test case with all queries coming in at the same time
test_case_10 = [(2,10, 1, 5) for i in range(12)] +  [(8,11, 3, 5) for i in range(6)]+  [(12,9, 7, 5) for i in range(3)] #Test case with all queries coming in at the same time

def test_custom(test_case = "1", pick_up_mode = "requests",verbose = True, lobby_prob = 0.2):
    #Test using custom data
    print("Testing test case {}... \n".format(test_case))
    simulator = Simulator(verbose = True, test_data = eval("test_case_{}".format(test_case)), pick_up_mode = pick_up_mode, lobby_prob = lobby_prob)
    simulator.run("test")
    simulator.fetch_summary_stats()
    print("\n")
    print(simulator.summary_df.round(decimals = 2))
    print("\n")

def test_random(request_length = 30, pick_up_mode = "requests", verbose = False, random_seed = 1, lobby_prob = 0.2):
    #Tests using simulated data
    print("Testing simulation {}... \n".format(random_seed))
    simulator = Simulator(request_length = request_length, pick_up_mode = pick_up_mode, verbose = verbose, random_seed = random_seed, lobby_prob = lobby_prob)
    simulator.run("simulate")
    simulator.fetch_summary_stats()
    print("\n")
    print(simulator.summary_df.round(decimals = 2))
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", dest = "sim", default = True, help = "Whether to simulate or use custom data")
    parser.add_argument("--pick_up_mode", dest = "pick_up_mode", default = "requests", help = "Pick-up metric to decide request allocation. Takes in 2 values: requests, num_passengers")
    parser.add_argument("--length", dest = "length", default = 30, help = "Length of Simulation data")
    parser.add_argument("--verbose", dest = "verbose", default = False)
    parser.add_argument("--seed", dest = "seed", default = 1, help = "Which random seed to use")
    parser.add_argument("--lobby_prob", dest = "prob", default = 0.2, help = "Probability of lobby being chosen. Has to be less than 1")
    parser.add_argument("--test_case", dest = "test_case", default = "1", help = "Which custom data test case to use")

    args = parser.parse_args()

    if args.sim in ["1", "0", "true", "True"]:
        sim = True
    else:
        sim = False

    if args.verbose in ["1", "0", "true", "True"]:
        verbose = True
    else:
        verbose = False
    
    if sim:
        #Test using simulated data
        test_random(request_length = int(args.length), pick_up_mode = args.pick_up_mode, verbose = verbose, random_seed = int(args.seed), lobby_prob = float(args.prob))
    else:
        #Test using custom data
        test_custom(test_case = args.test_case, pick_up_mode = args.pick_up_mode, verbose = verbose, lobby_prob = float(args.prob))
