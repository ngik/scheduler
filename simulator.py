'''
CS5250 Assignment 4, Scheduling policies simulator
Author: Vincent Ngik
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''

import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self._remaining_burst_time = burst_time
        self._last_worked_time = arrive_time
        self._predicted_burst_time = 5
    #enddef

    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))
    #enddef
    
    @property
    def last_worked_time(self):
        return self._last_worked_time
    #enddef
    @last_worked_time.setter
    def last_worked_time(self, last_worked_time):
        self._last_worked_time = last_worked_time
    #enddef
    
    @property
    def remaining_burst_time(self):
        return self._remaining_burst_time
    #enddef
    
    @property
    def predicted_burst_time(self):
        return self._predicted_burst_time
    #enddef
    @predicted_burst_time.setter
    def predicted_burst_time(self, predicted_burst_time):
        self._predicted_burst_time = predicted_burst_time
    #enddef
    
    def is_process_completed(self):
        return self._remaining_burst_time == 0
    
    #return actual time spent on process
    def work_done_on_process(self, burst_time):
        #return time spent
        if (self._remaining_burst_time > burst_time):
            self._remaining_burst_time = self._remaining_burst_time - burst_time
            return burst_time
        else:
            time_spent = self._remaining_burst_time
            self._remaining_burst_time = 0
            return time_spent
        #endif
    #enddef
#endclass


#start of helper functions

#return (current_process, waiting_time)
def do_pre_compute_bookkeeping(current_process, working_process_queue, schedule, current_time, waiting_time):
    #get process to work on and do some recording
    if (not current_process):
        #handle initial state where current_process is None
        current_process = working_process_queue.pop(0)
        schedule.append((current_time,current_process.id))
    else:
        old_process_id = current_process.id
        current_process = working_process_queue.pop(0)
        #record only if switching to a new process
        if (old_process_id != current_process.id):
            schedule.append((current_time,current_process.id))
        #endif
    #endif
    waiting_time = waiting_time + (current_time - current_process.last_worked_time)
    return (current_process, waiting_time)
#enddef

#return (current_time, time_spent)
def do_compute_bookkeeping(current_process, time_quantum, current_time):
    #doing work
    time_spent = current_process.work_done_on_process(time_quantum)
    
    #time has passed
    current_time = current_time + time_spent
    current_process.last_worked_time = current_time
    
    return (current_time, time_spent)
#enddef

#return current_time
def do_post_compute_bookkeeping(current_process, working_process_queue, incoming_process_queue, current_time):
    #add back current_process if not completed 
    if (not current_process.is_process_completed()):
        working_process_queue.append(current_process)
    #endif
    
    #fast forward iff no task in working_process_queue
    if (len(working_process_queue) == 0 and len(incoming_process_queue) > 0):
        current_process = incoming_process_queue.pop(0)
        working_process_queue.append(current_process)
        current_time = current_process.arrive_time
    #endif

    return current_time
#enddef

#end of helper functions

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        #endif
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    #endfor
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time
#enddef

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    #store the (switching time, proccess_id) pair
    schedule = []
    #setting up of variables
    RR_process_list = copy.deepcopy(process_list)
    active_queue = []
    current_time = 0
    waiting_time = 0
    current_process = None
    
    #adding first task
    active_queue.append(RR_process_list.pop(0))
    
    while (len(active_queue) > 0):
        (current_process, waiting_time) = do_pre_compute_bookkeeping(current_process, active_queue, schedule, current_time, waiting_time)
        
        (current_time, time_spent) = do_compute_bookkeeping(current_process, time_quantum, current_time)
        
        #adding new tasks which have arrived during computation
        while (len(RR_process_list) > 0 and current_time >= RR_process_list[0].arrive_time):
            active_queue.append(RR_process_list.pop(0))
        #endwhile
        
        current_time = do_post_compute_bookkeeping(current_process, active_queue, RR_process_list, current_time)
    #endwhile
    
    average_waiting_time = waiting_time/float(len(process_list))
    return (schedule, average_waiting_time)
#enddef

def SRTF_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    #setting up of variables
    SRTF_process_list = copy.deepcopy(process_list)
    active_queue = []
    current_time = 0
    waiting_time = 0
    current_process = None
    
    #adding first task
    active_queue.append(SRTF_process_list.pop(0))
    
    while (len(active_queue) > 0):
        #sort the active_queue by remaining_burst_time
        active_queue = sorted(active_queue, key=lambda process: process.remaining_burst_time)
        
        if (len(SRTF_process_list) > 0):
            time_to_interrupt = SRTF_process_list[0].arrive_time
        else:
            time_to_interrupt = float('inf')
        #endif
        
        (current_process, waiting_time) = do_pre_compute_bookkeeping(current_process, active_queue, schedule, current_time, waiting_time)
        
        #compute how long to work before checking for re-schedule
        time_quantum = min(current_process.remaining_burst_time, time_to_interrupt - current_time)
        
        (current_time, time_spent) = do_compute_bookkeeping(current_process, time_quantum, current_time)
        
        if (len(SRTF_process_list) > 0 and current_time == SRTF_process_list[0].arrive_time):
            active_queue.append(SRTF_process_list.pop(0))
        #endif
        
        current_time = do_post_compute_bookkeeping(current_process, active_queue, SRTF_process_list, current_time)
    #endwhile
    
    average_waiting_time = waiting_time/float(len(process_list))
    return (schedule, average_waiting_time)
#enddef

def SJF_scheduling(process_list, alpha):
    #store the (switching time, proccess_id) pair
    schedule = []
    #setting up of variables
    SJF_process_list = copy.deepcopy(process_list)
    active_queue = []
    current_time = 0
    waiting_time = 0
    current_process = None
    history = dict()
    
    #adding first task
    active_queue.append(SJF_process_list.pop(0))
    
    while (len(active_queue) > 0):
        #sort the active_queue by predicted_burst_time
        for id, past_predicted_burst_time in history.items():
            matching_ids = list(filter(lambda process: process.id == id, active_queue))
            if (len(matching_ids) > 0):
                matching_ids[0].predicted_burst_time = past_predicted_burst_time
            #endif
        #endfor
        active_queue = sorted(active_queue, key=lambda process: process.predicted_burst_time)
        
        (current_process, waiting_time) = do_pre_compute_bookkeeping(current_process, active_queue, schedule, current_time, waiting_time)
        
        time_quantum = current_process.remaining_burst_time
        
        (current_time, time_spent) = do_compute_bookkeeping(current_process, time_quantum, current_time)
        
        current_process.predicted_burst_time = alpha * time_spent + (1 - alpha) * current_process.predicted_burst_time
        history[current_process.id] = current_process.predicted_burst_time
        
        #adding new tasks which have arrived during computation
        while (len(SJF_process_list) > 0 and current_time >= SJF_process_list[0].arrive_time):
            active_queue.append(SJF_process_list.pop(0))
        #endwhile
        
        current_time = do_post_compute_bookkeeping(current_process, active_queue, SJF_process_list, current_time)
    #endwhile
    
    average_waiting_time = waiting_time/float(len(process_list))
    return (schedule, average_waiting_time)
#enddef

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            #endif
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
        #endfor
    return result
#enddef

def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        #endfor
        f.write('average waiting time %.2f \n'%(avg_waiting_time))
#enddef

def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    #endfor
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    #looping for a simple search on optimal solution
    optimal_solution = [0, float('inf')]
    for i in range(1, 101):        
        i = 9 + i * 2 / 100
        RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = i)
        #write_output('RR' + str(i) + '.txt', RR_schedule, RR_avg_waiting_time )
        print(str(i) + " has solution of " + str(RR_avg_waiting_time))
        if (optimal_solution[1] > RR_avg_waiting_time):
            #print(str(optimal_solution[0]) + " has solution of " + str(optimal_solution[1]))
            #print(str(i) + " has better solution of " + str(RR_avg_waiting_time))
            optimal_solution[0] = i
            optimal_solution[1] = RR_avg_waiting_time
        #endif
    #endfor
    print(optimal_solution)
    '''
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    '''
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )

    print ("simulating SJF ----")
    #looping for a simple search on optimal solution
    optimal_solution = [0, float('inf')]
    for i in range(1, 101):
        i = i / 100
        #i = 0.49 + i * 2 / 10000
        SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = i)
        #write_output('SJF' + str(i) + '.txt', SJF_schedule, SJF_avg_waiting_time )
        #print(str(i) + " has solution of " + str(SJF_avg_waiting_time))
        if (optimal_solution[1] > SJF_avg_waiting_time):
            #print(str(optimal_solution[0]) + " has solution of " + str(optimal_solution[1]))
            #print(str(i) + " has better solution of " + str(SJF_avg_waiting_time))
            optimal_solution[0] = i
            optimal_solution[1] = SJF_avg_waiting_time
        #endif
    #endfor
    print(optimal_solution)
    '''
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
    '''
#enddef

if __name__ == '__main__':
    main(sys.argv[1:])
#endif