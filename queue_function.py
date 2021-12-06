"""
Code is based on the following SimPy example:
    https://simpy.readthedocs.io/en/latest/examples/bank_renege.html
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


def tib_exponential(rng, capacity_server):
    return rng.exponential(scale=1/capacity_server, size=None)


def tib_deterministic(_, capacity_server):
    return 1/capacity_server


def tib_hyp_exponential(rng, capacity_server):
    if rng.uniform() < 0.75:
        tib = rng.exponential(scale=1/capacity_server, size=None)
    else:
        tib = rng.exponential(scale=1/(capacity_server*5), size=None)
    return tib


def source(env, counter,  arrival_rate, capacity_server, data, rng, tib_func):
    """Source generates customers randomly"""

    i = 0
    while True:
        tib = tib_func(rng, capacity_server)
        c = customer(
            env, counter, data, tib)
        env.process(c)
        t = rng.exponential(scale=1/arrival_rate, size=None)
        yield env.timeout(t)
        i += 1


def customer(env, counter, data, tib):
    """Customer arrives, is served and leaves."""
    arrive = env.now

    if isinstance(counter, simpy.PriorityResource):
        # SPTF code
        prio = tib
        with counter.request(priority=prio) as req:
            yield req
            wait = env.now - arrive
            data.times.append(arrive)
            data.wait_times.append(wait)
            data.n_queue.append(len(counter.queue))

            yield env.timeout(tib)
    elif isinstance(counter, simpy.Resource):
        # FIFO code
        with counter.request() as req:
            yield req
            wait = env.now - arrive
            data.times.append(arrive)
            data.wait_times.append(wait)
            data.n_queue.append(len(counter.queue))

            yield env.timeout(tib)


def run_queue_experiment(
    rng,
    time,
    arrival_rate,
    capacity_server,
    n_server=1,
    queueing_discipline="FIFO",
    tib_func=tib_exponential

):
    data = QueueData()
    env = simpy.Environment()

    if queueing_discipline.upper() == "FIFO":
        counter = simpy.Resource(env, capacity=n_server)
    elif queueing_discipline.upper() == "SPTF":
        counter = simpy.PriorityResource(env, capacity=n_server)
    else:
        raise Exception("Not a correct discipline. Check again.")

    env.process(source(env, counter, arrival_rate,
                capacity_server, data, rng, tib_func))
    env.run(until=time)
    return data


def vary_t_worker(q, d, rng, arrival_rate, capacity_server, n_server,
                  queueing_discipline, tib_func):
    while True:
        try:
            t, i = q.get_nowait()
        except queue.Empty:
            break

        queue_data = run_queue_experiment(rng, t, arrival_rate, capacity_server,
                                          n_server=n_server,
                                          queueing_discipline=queueing_discipline, tib_func=tib_func)
        mean_wait_time = np.mean(queue_data.wait_times)
        d[i].append(mean_wait_time)


def vary_rho_worker(q, d, rng, t, capacity_server, n_server):
    while True:
        try:
            rho, i = q.get_nowait()
        except queue.Empty:
            break

        queue_data = run_queue_experiment(rng, t, rho*capacity_server*n_server,
                                          capacity_server, n_server=n_server)
        mean_wait_time = np.mean(queue_data.wait_times)
        d[i].append(mean_wait_time)


def expected_waiting_time(lambda_, mu, c):
    rho = lambda_/(c*mu)

    def B(c, rho):
        if c == 0:
            return 1
        b = B(c - 1, rho)
        return (rho*b)/(c + rho*b)

    b = B(c - 1, c*rho)
    Pi_W = (rho*b)/(1 - rho + rho * b)
    return Pi_W * (1/((c*mu)*(1 - rho)))
