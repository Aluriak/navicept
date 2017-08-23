"""Implementation of search for n-ary concepts.

"""


from pyasp import asp


ASP_FILES = {'simple.lp'}


def have_concept(context, constraints) -> bool:
    """True if given constraints allows existance of at least one concept
    in the given context.

    """
    solver = asp.Gringo4Clasp(clasp_options='-n 1')

    atoms = set()
    for idx, dim in enumerate(context.sets):
        required, forbidden = constraints[idx]
        for elem in required:
            atoms.add('required({},"{}")'.format(idx+1, elem))
        for elem in forbidden:
            atoms.add('forbidden({},"{}")'.format(idx+1, elem))
        for elem in dim:
            atoms.add('set({},"{}")'.format(idx+1, elem))

    for relations in context.relations:
        atoms.add('rel("{}")'.format('","'.join(relations)))

    asp_constraints = ''.join(dimension_dependant_constraints(len(context.sets)))
    asp_atoms = '.'.join(sorted(atoms)) + ('.' if atoms else '')

    answers = solver.run(programs=list(ASP_FILES), additionalProgramText=asp_atoms + asp_constraints)
    for answer in answers:
        return True
    return False


def dimension_dependant_constraints(nb_dimension:int) -> str:
    """Yield ASP constraints that allow to handle up to nb_dimension
    dimensions in the data.

    Designed to be added to solver.lp.

    >>> next(dimension_dependant_constraints(2))
    'out(1,X1):- set(1,X1) ; in(2,X2) ; not rel(X1,X2).'

    >>> next(dimension_dependant_constraints(3))
    'out(1,X1):- set(1,X1) ; in(2,X2) ; in(3,X3) ; not rel(X1,X2,X3).'

    """
    dimensions = range(1, nb_dimension+1)
    template = 'out({dim},X{dim}):- set({dim},X{dim}) ; {in_atoms} ; not rel({xdims}).'
    for dim in dimensions:
        in_atoms = ' ; '.join('in({dim},X{dim})'.format(dim=dim) for dim in set(dimensions) - {dim})
        yield template.format(
            dim=dim,
            xdims=','.join('X'+str(dim) for dim in dimensions),
            in_atoms=in_atoms,
        )
