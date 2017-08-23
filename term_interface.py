"""Implementation of a simple terminal interface to the lattice navigation.

"""


from asyncio import coroutine
from termcolor import cprint
from context import Context
from navigation import find_concepts_interactively, pretty_nconcept


def term_interface(context:Context) -> tuple:
    """Return the final concept found by user using terminal interface.

    """
    concept_finder = find_concepts_interactively(context)
    # get context and constraints
    _, constraints = next(concept_finder)
    try:
        while True:
            _, constraints = concept_finder.send(_user_input(context, constraints))
    except StopIteration as last:
        return last.value


def _user_input(data:Context, constraints:dict) -> (int, str, str):
    """Return the dimension where the choosen element is,
    the choosen element itself, and the decision (in or out),
    based on stdin.

    Return on the found concept : the set of required elements
    for each dimension.

    """
    print('Pick a white one:')
    choosables = {}  # {element: dim index}
    for idx, dim in enumerate(data.sets):
        required, forbidden = constraints[idx]
        tochoose = dim - (required | forbidden)
        choosables.update({choosable: idx for choosable in tochoose})
        print('\t' + str(idx) + ':\t', end='')
        for elem in dim:
            color = 'white' if elem in tochoose else ('red' if elem in forbidden else 'green')
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


if __name__ == "__main__":
    context = Context(({'1', '2', '3'}, {'a', 'b', 'c'}),
                      {('1', 'a'), ('1', 'b'), ('2', 'b'), ('2', 'c'), ('3', 'c')})

    print(context)
    print('FINAL:', pretty_nconcept(term_interface(context)[1]))
