"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

"""
from numpy import random
import simpy


class QueueData:
    def __init__(self):
        self.times = []
        self.wait_times = []


def source(env, counter,  arrival_rate, capacity_server, data):
    """Source generates customers randomly"""
    # for i in range(number):
    i = 0
    while True:
        c = customer(env, 'Customer%02d' % i, counter, capacity_server, data)
        env.process(c)
        t = random.exponential(scale=1/arrival_rate, size=None)
        yield env.timeout(t)
        i += 1


def customer(env, name, counter, capacity_server, data):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    #print('%7.4f %s: Here I am' % (arrive, name))

    with counter.request() as req:
        yield req
        wait = env.now - arrive
        # We got to the counter
        #print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        data.times.append(arrive)
        data.wait_times.append(wait)

        # time of service
        tib = random.exponential(scale=1/capacity_server, size=None)
        yield env.timeout(tib)
        #print('%7.4f %s: Finished' % (env.now, name))


def run_queue_experiment(
        random_seed,
        time,
        arrival_rate,
        capacity_server,
        n_server=1,
        queueing_discipline="FIFO"):
    data = QueueData()

    # Setup and start the simulation
    print('DES start')
    print(queueing_discipline)
    random.seed(random_seed)
    env = simpy.Environment()

    # Start processes and run
    counter = simpy.Resource(env, capacity=n_server)
    env.process(source(env, counter, arrival_rate, capacity_server, data))
    env.run(until=time)

    return data
