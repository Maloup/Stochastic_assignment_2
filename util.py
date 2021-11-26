from numpy.random import Generator, MT19937, SeedSequence

def initialize_parallel_rngs(n, seed):
    """
    Initializes `n` Mersenne Twister PRNGs and advance each PRGNS by 2^128 steps to avoid
    problems in parallel sampling as described in https://numpy.org/doc/stable/reference/random/bit_generators/mt19937.html#numpy.random.MT19937.

    Returns:
        List of PRNGs safe for parallel sampling use
    """
    sg = SeedSequence(seed)
    bit_generator = MT19937(sg)
    rngs = []
    for _ in range(n):
        rngs.append(Generator(bit_generator))
        bit_generator = bit_generator.jumped()

    return rngs
