"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

"""
import numpy as np
from numpy import random
import queue
import simpy


class QueueData:
    def __init__(self):
        self.times = []
        self.wait_times = []
        self.n_queue = []


def source(env, counter,  arrival_rate, capacity_server, data, rng):
    """Source generates customers randomly"""
    # for i in range(number):
    i = 0
    while True:
        tib = rng.exponential(scale=1/capacity_server, size=None)
        c = customer(
                env, counter, data, tib)
        env.process(c)
        t = rng.exponential(scale=1/arrival_rate, size=None)
        yield env.timeout(t)
        i += 1


def customer(env, counter, data, tib):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    #print('%7.4f %s: Here I am' % (arrive, name))


    if isinstance(counter, simpy.Resource):
        #FIFO code
        with counter.request() as req:
            yield req
            wait = env.now - arrive
            # We got to the counter
            #print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
            data.times.append(arrive)
            data.wait_times.append(wait)
            data.n_queue.append(len(counter.queue)) #amount of people in queue

            # time of service
            yield env.timeout(tib)
            #print('%7.4f %s: Finished' % (env.now, name))
    
    elif isinstance(counter, simpy.PriorityResource):
         #SPTF code
         prio = int(tib*1e4)
         with counter.request(priority=prio) as req:
            yield req
            wait = env.now - arrive
            # We got to the counter
            #print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
            data.times.append(arrive)
            data.wait_times.append(wait)
            data.n_queue.append(len(counter.queue)) #amount of people in queue

            # time of service
            yield env.timeout(tib)
            #print('%7.4f %s: Finished' % (env.now, name))



def run_queue_experiment(
    rng,
    time,
    arrival_rate,
    capacity_server,
    n_server=1,
    queueing_discipline="FIFO"
):
    data = QueueData()
    env = simpy.Environment()

    if queueing_discipline.upper() == "FIFO": 
        counter = simpy.Resource(env, capacity=n_server)
    elif queueing_discipline.upper() == "SPTF":
        counter = simpy.PriorityResource(env, capacity=n_server)
    else: 
        raise Exception("Not a correct discipline. Check again.")

    env.process(source(env, counter, arrival_rate, capacity_server, data, rng))
    env.run(until=time)
    return data


def vary_t_worker(q, d, rng, arrival_rate, capacity_server, n_server):
    while True:
        try:
            t, i = q.get_nowait()
        except queue.Empty:
            break

        queue_data = run_queue_experiment(rng, t, arrival_rate, capacity_server,
                                          n_server=n_server)
        mean_wait_time = np.mean(queue_data.wait_times)
        d[i].append(mean_wait_time)


def vary_rho_worker(q, d, rng, t, capacity_server, n_server):
    while True:
        try:
            rho, i = q.get_nowait()
        except queue.Empty:
            break

        queue_data = run_queue_experiment(rng, t, rho*capacity_server, capacity_server,
                                          n_server=n_server)
        mean_wait_time = np.mean(queue_data.wait_times)
        d[i].append(mean_wait_time)