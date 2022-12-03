"""
simple script to test queued background processes
https://superfastpython.com/thread-triggered-background-task/

We'll loop 100 times, with some variance in timing.
In each loop, we'll do something, and send something unique to a queue,
monitored by a background process
The ordering of the processing is important - 1,2,3,4 etc
this is to prove that we can essentially have process A perform a series of
steps, and have 'linked,ordered' steps performed by a background thread,
without tying up the main process.
The real world example is where an API request will issue 'next' tokens to
paginate the output - BUT - to get the real output, we need to request (with
the same tokens) the data in a different content-type.
Calls with the 'wanted' content type, don't send back pagination info

simulate 100 'pages' of data

"""

from random import randrange
import time
from threading import Thread
from queue import SimpleQueue

# The principle here is that we're trying to keep this as simple as possible - so I'm 'not' keeping track of how 'many' items we're dealing with
# I'm merely keeping track of two things...
# 1. whether the controlling process is 'done' - i.e. it's got all its pages
# 2. whether the 'queue' written to by the controlling process, and consumed by the background process - is empty.  
# If both are true, then the background process can complete
# This leaves one more question, of how the main thread will know when to complete (because it will likely complete its work, before the background thread).  Options:
# 1. Keep track of what the background thread is doing / callbacks / status etc - or.. simpler... 
# 2. join the daemon thread.  This will block on the main thread until the daemon is done - so... we realistically need to create another foregound thread to run each 'job'

job = {}


def is_job_queuing_finished(job_number):

    return job[job_number] == True


def job_queueing_started(job_number):

    job[job_number] = False


def job_queuing_finished(job_number):

    job[job_number] = True


def background_csv_task(msg_queue, job_number):
    """This is the function that will be called in a background (daemon) thread

    Args:
        msg_queue (Queue): the queue we'll use to communicate between controller/consumer
        job_number (int): job number (this is just theoretical at this stage, to imply we may have multiple 'jobs' going in parallel)
    """
    while is_job_queuing_finished(job_number) == False or not msg_queue.empty():
        message = msg_queue.get()
        print(f"Job : {job_number} : background csv message : {message}")

        #generate some random 'request latency' - so we don't fall into any assumption traps on completion
        time_to_sleep = randrange(10)
        time.sleep(time_to_sleep)

    print("background csv thread finished")


def orchestrate_work(queue_depth):
    """This is the function that controls the job/s, and creates a new thread for each

    Args:
        queue_depth (int): The number of pages to cycle through.  This is convenient for us to know up front, as the process does 'not' :)
    """
    global job_count
    job_count += 1
    job_number = job_count
    thread = Thread(target=process_work, args=(
        queue_depth, job_number), name="CostReport")
    print(f"starting report thread for job : {job_number}")
    thread.start()
    # print("main thread join")
    # thread.join() (if you want each job to block)
    print("orderstrate work finished")


def process_work(queue_depth, job_number):
    """Process a job (a client request)

    Args:
        queue_depth (int): how many requests to simulate
        job_number (int): the unique number of this job (request)
    """
    msg_queue = SimpleQueue()
    job_number = job_number
    print(f"Job : {job_number} : started")
    print(f"Job : {job_number} : starting background task....")
    #Keep track of the fact we've started this job
    job_queueing_started(job_number)
    #create the thread, and pass in the queue / job_number
    daemon = Thread(target=background_csv_task, args=(
        msg_queue, job_number), daemon=True, name='Background')
    daemon.start()

    # While we're performing a for loop here - in reality we'd be doing 'while 'next page' is populated' or something like that
    for json_page in range(queue_depth):
        print(f"Job : {job_number} : page {json_page}")

        message = f"Job_{job_number}_Page_{json_page}"
        msg_queue.put(message)
        # enqueue

        # sleep for a random period between 1 and 5 seconds (to simulate latency)
        time_to_sleep = randrange(5)
        time.sleep(time_to_sleep)

    # wait and check for background to finish

    #signal that we are done pushing to the queue
    job_queuing_finished(job_number)
    print(f"Job : {job_number} : queueing finished")
    print(f"Job : {job_number} : waiting on main thread....")
    daemon.join()
    print(f"Job : {job_number} : process job finished")


job_count = 0

#Create 4 jobs
for i in range(4):
    orchestrate_work(10)

print("Finished on main process")