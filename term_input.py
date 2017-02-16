"""Implementation of a simple terminal interface to the lattice navigation."""


from asyncio import coroutine
from termcolor import cprint


def user_choice_term(concept_finder:coroutine) -> (int, str, str):
    """Yield the dimension where the choosen element is,
    the choosen element itself, and the decision (in or out),
    based on stdin.

    Return on the found concept : the set of required elements
    for each dimension.

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
