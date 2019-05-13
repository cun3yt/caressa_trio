import random


def check_event_uniform_distribution(probability) -> bool:
    """
    Generate a sample and check if the uniform distribution event happens
    for the given probability, which is in the range of [0,1] (both side inclusive)

    :param probability: probability of an event happening, it is the [0, 1]
    :return: bool True if event happened with the given probability
    """
    assert (0 <= probability <= 1), (
        "Argument probability must be in the range of [0, 1] (inclusive)."
    )

    return random.randint(0, 100) < (probability * 100)
