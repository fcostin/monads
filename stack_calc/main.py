"""
monad stack calculator demo

XXX TODO: make it actually useable as an interactive calculator

rfc sept 2012
"""

# 1. define the "explicit" verson of our monadic return operator

__ret = lambda stk, *ys : (stk, tuple(ys))

# 2. define "explicit" versions of simple stack operators

_push = lambda stk, x : __ret([x] + list(stk)) # one arg, no result
_pop = lambda stk : __ret(stk[1:], stk[0]) # no arg, one result

#   -- machinery for defining explicit unary and binary stack operators with no arguments or results
__unary_op = lambda f : (lambda stk : __ret([f(stk[0])] + list(stk[1:])))
__binary_op = lambda f : (lambda stk : __ret([f(stk[0], stk[1])] + list(stk[2:])))

import operator
_add = __binary_op(operator.add)
_sub = __binary_op(operator.sub)
_mul = __binary_op(operator.mul)
_div = __binary_op(operator.div)
_neg = __unary_op(operator.neg)

# 3. define "implicit" partially applied / lazy versions of stack operators

__partial = lambda _f : (lambda *xs : (lambda stk : _f(stk, *xs)))


ret = __partial(__ret) # our genuine monadic return operator (?)
push = __partial(_push)
pop = __partial(_pop)
add = __partial(_add)
sub = __partial(_sub)
mul = __partial(_mul)
div = __partial(_div)
neg = __partial(_neg)


def bind2(f, g):
    """(x -> my) -> (y -> mz) -> (x -> mz)"""
    def _f_bind2_g(stk, *x):
        stk_prime, y = f(*x)(stk)
        stk_prime_prime, z = g(*y)(stk_prime)
        return __ret(stk_prime_prime, *z)
    return __partial(_f_bind2_g)


# n.b. ret is left-identity of bind2, that is, bind2(ret, f) equals f
# so it is used in the fold here as the initial value. this is
# algebraically pleasing and suggests we're not totally wrong.

chain = lambda *fs : reduce(bind2, fs, ret)


def make_program():
    """make a pure functional stack calculator program ready for evaluation"""

    # 1.    define DUP : stack op [x] -> {x}[x]
    dup = bind2(
        pop,
        lambda x : bind2(
            lambda : push(x),
            lambda : push(x),
        )()
    )

    # 2.    define SQUARE : stack op [x] -> [x*x]
    square = bind2(dup, mul)

    # 3.    define PROGRAM
    program = chain(
        push,
        lambda : push(5),
        add,
        square,
        pop,
    )

    return program


def read_int_from_stdin():
    """stdin is a rich source of integers"""
    while True:
        try:
            print 'please enter an integer>',
            return int(raw_input())
        except ValueError:
            pass


def evaluate_stack_program(program):
    """evaluation harness"""

    x = read_int_from_stdin()
    initial_arguments = (x, )
    initial_stk = []

    final_stk, final_results = program(*initial_arguments)(initial_stk)

    print 'final stack: %s' % str(final_stk)
    print 'final result(s): %s' % str(final_results)


if __name__ == '__main__':
    evaluate_stack_program(make_program())

