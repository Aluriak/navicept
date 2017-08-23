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
        # NB: tuple is important: order must be kept in order to get
        #  consistant ASP program.
        relations = (tuple(rel) for rel in itertools.product(*dimensions)
                     if random.random() < density)
        return Context(dimensions, frozenset(relations))


    def __str__(self) -> str:
        return self.__pretty_print() if len(self.sets) == 2 else repr(self)

    def __pretty_print(self) -> str:
        ones, twos = self.sets
        twos = tuple(twos)
        out = '   ' + '  '.join(twos) + '\n'
        for one in ones:
            out += one + '  ' + '  '.join('×' if (one, two) in self.relations else ' ' for two in twos) + '\n'
        return out


