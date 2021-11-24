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


RANDOM_SEED = 42
NEW_CUSTOMER = 100  # Total number of customers
ARRIVAL_RATE = 10
CAPACITY_SERVER = 10
N_SERVERS = 1
QUEING_DISCIPLINE = "FIFO"


def source(env, counter):
    """Source generates customers randomly"""
    #for i in range(number):
    i = 0
    while True:
        c = customer(env, 'Customer%02d' % i, counter)
        env.process(c)
        t = random.exponential(scale=1/ARRIVAL_RATE, size=None)
        yield env.timeout(t)
        i +=1


def customer(env, name, counter):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print('%7.4f %s: Here I am' % (arrive, name))

    with counter.request() as req:
        yield req
        wait = env.now - arrive
        # We got to the counter
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))

        #time of service
        tib = random.exponential(scale=1/CAPACITY_SERVER, size=None)
        yield env.timeout(tib)
        print('%7.4f %s: Finished' % (env.now, name))


# Setup and start the simulation
print('DES start')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=N_SERVERS)
env.process(source(env, counter))
env.run(until=15)
