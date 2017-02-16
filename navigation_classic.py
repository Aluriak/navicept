"""Implementation of the lattice navigation, as described
in Rudolph and ali. article *Membership constraints in Formal Concept Analysis*.

"""

from collections import namedtuple

from termcolor import cprint
from pyasp import asp


ASP_FILES = {'sofa.lp'}
# ASP_FILES = {'simple.lp'}  # simpler version


# Define a constraint on a dimension for concept search.
Constraint = namedtuple('Constraint', 'required, forbidden')
Constraint.__new__.__defaults__ = (frozenset(), frozenset())
Context = namedtuple('Context', 'sets, relations')


def have_concept(context, constraints) -> bool:
    """True if given context and constraints yields concepts."""
    solver = asp.Gringo4Clasp(clasp_options='-n 1')

    atoms = set()
    for idx, constraint in enumerate(constraints, start=1):
        for elem in constraint.required:
            atoms.add('required({},{})'.format(idx, elem))
        for elem in constraint.forbidden:
            atoms.add('forbidden({},{})'.format(idx, elem))
    for idx, dim in enumerate(context.sets, start=1):
        for elem in dim:
            atoms.add('set({},{})'.format(idx, elem))
    for idx, relations in enumerate(context.relations, start=1):
        atoms.add('rel({},{})'.format(*relations))

    atoms = '.'.join(sorted(atoms)) + ('.' if atoms else '')
    # print(atoms, end='')

    for answer in solver.run(programs=list(ASP_FILES), additionalProgramText=atoms):
        # print('\tOK')
        return True
    # print('\tNOPE')
    return False



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
                if not have_concept(context, tested_constraints):
                    constraints[idx] = Constraint(constraints[idx].required, constraints[idx].forbidden | {elem})
                    change = True

                # If, once deleted, elem avoid any concept creation,
                #  it should be added to required.
                tested_constraints = list(Constraint(*c) for c in constraints)
                tested_constraints[idx] = Constraint(constraint.required, constraint.forbidden | {elem})
                if not have_concept(context, tested_constraints):
                    constraints[idx] = Constraint(constraints[idx].required | {elem}, constraints[idx].forbidden)
                    change = True

    return constraints


def find_concepts_interactively(context):
    """Interactive n-concept finding algorithm"""
    constraints = [Constraint() for _ in range(len(context.sets))]
    constraints = propagate(context, constraints)

    def while_stop_condition():
        for idx, dim in enumerate(context.sets):
            if dim != (constraints[idx].required | constraints[idx].forbidden):
                return True

    while while_stop_condition():
        # choice of an element to take or discards
        idx, choosen, decision = user_choose_one(context, constraints)

        constraint = constraints[idx]
        if decision == 'in':
            constraints[idx] = Constraint(constraint.required | {choosen}, constraint.forbidden)
        else:
            assert decision == 'out', "Unexpected decision: {}".format(decision)
            constraints[idx] = Constraint(constraint.required, constraint.forbidden | {choosen})
        constraints = propagate(context, constraints)
    return tuple(constraint.required for constraint in constraints)


def user_choose_one(context, constraints) -> (int, str, str):
    """Return the dimension where the choosen element is, the choosen element
    itself, and the decision (in or out).

    """
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
    return choosables[choosen], choosen, decision


def pretty_nconcept(concept:(frozenset, ...)) -> str:
    """Pretty print of given n-concept"""
    return '{' + '}×{'.join(','.join(_) for _ in concept) + '}'


if __name__ == "__main__":
    context = Context(({'1', '2', '3'}, {'a', 'b', 'c'}),
                      {('1', 'a'), ('1', 'b'), ('2', 'b'), ('2', 'c')})

    print('FINAL:', pretty_nconcept(find_concepts_interactively(context)))
