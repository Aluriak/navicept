"""Implementation of the lattice navigation, using coroutine to allow one
to plug easily user interaction to lattice exploration.


"""


from asyncio import coroutine
from collections import namedtuple

from termcolor import cprint

import nconcept
from context import Context


@coroutine
def find_concepts_interactively(context):
    """Coroutine implementing an interactive n-concept finding algorithm.

    Yield (context, constraints) 2-uplet,
    receive (idx, choosen, decision) 3-uplet.

    Parameters:
        context -- the working context (remains unchanged)

    Received during execution:
        idx -- dimension index in context where is the targeted object
        choosen -- the object choosen by user to be changed
        decision -- the new choosen object state, 'in', 'out' or 'unknow'

    Yield at each execution:
        constraints -- constraints sets by user
        induced_constraints -- constraints induced from user constraints

    Constraints are always encoded as {dimension idx: {required}, {forbidden}}.

    Return:
        concept -- the only concept remaining meeting all the constraints

    This is basically an encapsulation around (1) constraints initialization,
    (2) search loop stop condition and (3) constraint update.

    """
    dimensions = context.sets
    constraints = {idx: (set(), set()) for idx in range(len(dimensions))}
    induced_constraints = propagate(context, constraints)

    while not all_relations_are_decided(context, induced_constraints):
        user_pick = (yield constraints, induced_constraints)
        constraints = update_constraints(constraints, *user_pick)
        induced_constraints = propagate(context, constraints)

    return constraints, induced_constraints

# for idx, dim in enumerate(context.sets):
    # for elem in context
    # if induced_constraints[idx][0]

def propagate(data:Context, constraints:dict) -> dict:
    """Return {dimid: {required}, {forbidden}} populated with given
    constraints and any constraint induced from data.

    """
    propagated = {dim: (set(val[0]), set(val[1]))
                  for dim, val in constraints.items()}
    change = True
    while change:
        change = False
        for idx, dim in enumerate(data.sets):
            required, forbidden = propagated[idx]
            for elem in dim - (required | forbidden):

                # If, once added, elem avoid any concept creation,
                #  it should be added to forbidden.
                required.add(elem)
                if not nconcept.have_concept(data, propagated):
                    forbidden.add(elem)
                    change = True
                required.remove(elem)

                if elem in forbidden: continue

                # If, once deleted, elem avoid any concept creation,
                #  it should be added to required.
                forbidden.add(elem)
                if not nconcept.have_concept(data, propagated):
                    required.add(elem)
                    change = True
                forbidden.remove(elem)

    return propagated


def all_relations_are_decided(data:Context, constraints:dict):
    if not constraints: return False
    for idx, dim in enumerate(data.sets):
        required, forbidden = constraints[idx]
        if dim != (required | forbidden):
            return False
    return True


def update_constraints(constraints:tuple, dimension, item, update:str or None) -> tuple:
    """Return constraints modified in-place, with given item in given dimension
    that will be marked as *update* (required, forbidden or None)

    """
    assert update in {'in', 'out'} or not update
    assert dimension in range(len(constraints))

    requireds, forbiddens = constraints[dimension]

    if update == 'in':
        if item in forbiddens:
            forbiddens.remove(item)
        requireds.add(item)
    elif update == 'out':
        if item in requireds:
            requireds.remove(item)
        forbiddens.add(item)
    elif not update:
        assert item in (requireds | forbiddens)
        (requireds if item in requireds else forbiddens).remove(item)

    return constraints


def pretty_nconcept(constraints:tuple) -> str:
    """Pretty print of n-concept"""
    concept = tuple(reqs for reqs, _ in constraints.values())
    print('FINAL INDUCED:', concept)
    return '{' + '} × {'.join(','.join(_) for _ in concept) + '}'
