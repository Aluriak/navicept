"""Definition of the context class as a namedtuple,
and definitions laying around.

"""


import random
import itertools
from collections import namedtuple


class Context(namedtuple('ContextBase', 'sets, relations')):


    @staticmethod
    def with_random_relations(dimensions:tuple, density:float=0.5):
        """Return a new Context instance where relations are randomly choosen,
        with a density roughly equal to given ratio.

        """
        assert 0. <= density <= 1.
        relations = (tuple(rel) for rel in itertools.product(*dimensions)
                     if random.random() < density)
        return Context(dimensions, frozenset(relations))
