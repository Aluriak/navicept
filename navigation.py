"""

usage:

    navigation.py <solver.lp> <instance.lp>


"""


from asyncio import coroutine
from collections import namedtuple

from termcolor import cprint

import nconcept
import term_input
from context import Context


# Define a constraint on a dimension for concept search.
Constraint = namedtuple('Constraint', 'required, forbidden')
Constraint.__new__.__defaults__ = (frozenset(), frozenset())


def propagate(context, constraints):
    """Propagation of client decisions.

    Modify given constraints in place.

    """
    change = True
    while change:
        change = False
        for idx, (dim, constraint) in enumerate(zip(context.sets, constraints)):
            for elem in dim - (constraint.required | constraint.forbidden):

                # If, once added, elem avoid any concept creation,
                #  it should be added to forbidden.
                tested_constraints = list(Constraint(*c) for c in constraints)
                tested_constraints[idx] = Constraint(constraint.required | {elem}, constraint.forbidden)
                if not nconcept.have_concept(context, tested_constraints):
                    constraints[idx] = Constraint(constraints[idx].required, constraints[idx].forbidden | {elem})
                    change = True

                # If, once deleted, elem avoid any concept creation,
                #  it should be added to required.
                tested_constraints = list(Constraint(*c) for c in constraints)
                tested_constraints[idx] = Constraint(constraint.required, constraint.forbidden | {elem})
                if not nconcept.have_concept(context, tested_constraints):
                    constraints[idx] = Constraint(constraints[idx].required | {elem}, constraints[idx].forbidden)
                    change = True

    return constraints


def user_choice_term(concept_finder:coroutine) -> (int, str, str):
    """Yield the dimension where the choosen element is,
    the choosen element itself, and the decision (in or out),
    based on stdin.

    """
    # get context and constraints
    context, constraints = next(concept_finder)

    while True:
        print('Pick a white one:')
        choosables = {}
        for idx, dim in enumerate(context.sets):
            requireds = constraints[idx].required
            forbiddens = constraints[idx].forbidden
            tochoose = dim - (requireds | forbiddens)
            choosables.update({choosable: idx for choosable in tochoose})
            print('\t' + str(idx) + ':\t', end='')
            for elem in dim:
                color = 'white' if elem in tochoose else ('red' if elem in forbiddens else 'green')
                cprint(elem + ' ', color, end='')
            print()

        choosen = None
        while choosen not in choosables:
            choosen = input('> ')
        decision = None
        while decision not in {'in', 'out'}:
            decision = input('[in/out]> ')

        assert choosen in choosables
        try:
            context, constraints = concept_finder.send((choosables[choosen], choosen, decision))
        except StopIteration:
            break
    return tuple(constraint.required for constraint in constraints)


@coroutine
def find_concepts_interactively(context):
    """Interactive n-concept finding algorithm.

    Yield (context, constraints) 2-uplet,
    receive (idx, choosen, decision) 3-uplet.

    context -- the working context (remains unchanged)
    constraints -- constraints updated at each step
    idx -- dimension index in context where is the targeted object
    choosen -- the object choosen by user to be changed
    decision -- the new choosen object state, 'in', 'out' or 'unknow'

    This is basically an encapsulation around (1) constraints initialization,
    (2) search loop stop condition and (3) constraint update.

    """
    constraints = [Constraint() for _ in range(len(context.sets))]
    constraints = propagate(context, constraints)

    def while_stop_condition():
        for idx, dim in enumerate(context.sets):
            if dim != (constraints[idx].required | constraints[idx].forbidden):
                return True

    while while_stop_condition():
        # choice of an element to take or discards
        idx, choosen, decision = (yield context, constraints)

        constraint = constraints[idx]
        if decision == 'in':
            constraints[idx] = Constraint(constraint.required | {choosen}, constraint.forbidden)
        elif decision == 'out':
            constraints[idx] = Constraint(constraint.required, constraint.forbidden | {choosen})
        else:  # remove the constraint on choosen
            constraints[idx] = Constraint(constraint.required - {choosen}, constraint.forbidden - {choosen})
        constraints = propagate(context, constraints)

    # return the found concept itself
    return tuple(constraint.required for constraint in constraints)


def pretty_nconcept(concept:(frozenset, ...)) -> str:
    """Pretty print of given n-concept"""
    return '{' + '} × {'.join(','.join(_) for _ in concept) + '}'


if __name__ == "__main__":
    context = Context(({'1', '2', '3'}, {'a', 'b', 'c'}),
                      {('1', 'a'), ('1', 'b'), ('2', 'b'), ('2', 'c')})

    cor = find_concepts_interactively(context)
    print('FINAL:', pretty_nconcept(term_input.user_choice_term(cor)))
