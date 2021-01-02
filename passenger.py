class Passenger:
    
    """
    Passenger class to make it easy to keep track of passengers
    """
    def __init__(self, depart, to, start_time, num):
        self.depart = depart #Floor to pick passenger from
        self.num = num #Number of passengers in query
        self.to = to #Floor to drop passenger off
        self.start_time = start_time #Time when passenger makes a request
        self.state = 0 #State of passenger.

    def _pickup(self, current_time):
        self.pick_up = current_time #Time that passenger is picked up
    
    def _complete(self, current_time):
        self.complete = current_time

        #Compute passenger stat 
        self.wait_time = self.pick_up - self.start_time #Time passenger has to wait
        self.travel_time = self.complete - self.pick_up #Time passenger travelled in elevator
        
        