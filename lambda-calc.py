#!/usr/bin/env python3

import re
from time import clock
from typing import Any

# NOTE: Since Python uses eager evaluation, selection options must be wrapped in empty lambdas to
#       prevent execution of non-terminating recursive calls once base case is reached.
#   eg. (<condition>)(lambda: <True case>)(lambda: <False case>)

def num(n: int) -> str:
    ''' Returns Church numeral representation of n. '''
    return '(lambda s:lambda x:{}x{})'.format('s(' * int(n), ')' * int(n))

def expand_lambda(exp: str) -> str:
    ''' Expands '#' to 'lambda'. Used only for compactness in implementation. '''
    return exp.replace('#:', 'lambda:').replace('#', 'lambda ')

def token(tok: str, exp: str, exchange_arg: bool = False) -> None:
    ''' Add token with symbol 'tok' and expression 'exp' to dictionary. 'swap_arg' indicates whether
    token is an operator which should precede its first argument. '''
    global tokens
    tokens[tok] = (expand_lambda(exp), exchange_arg)

def make_tokens(alt_pred: bool = False) -> None:
    ''' Creates tokens for low-level functions. Setting alt_pred lengthens expression, but can speed
    up execution. '''
    global tokens
    tokens = {} # type Dict[str, Tuple[str, bool]]

    # True & False
    token('T', '(#x:#y:x())') # T: true literal
    token('F', '(#x:#y:y())') # F: false literal

    # Boolean Operators
    token('~', '(#x:x(#:F)(#:T))') # ~(x): not
    token('&', '(#x:#y:x(#:y)(#:F))', True) # (x)&(y): and
    token('|', '(#x:#y:x(#:T)(#:y))', True) # (x)|(y): or
    token('^', '(#x:#y:((x)&(~(y)))|((~(x))&(y)))', True) # (x)^(y): xor

    # Arithmetic Operators
    token('*', '(#x:#y:#z:x(y(z)))', True) # (x)*(y): multiply
    token('**', '(#x:#y:y(x))', True) # (x)**(y): exponentiate
    token('++', '(#x:#y:#z:y(x(y)(z)))', True) # (x)++: increment, (x)(++)(y): add
    if alt_pred:
        token('PHI', '(#p:#x:x(#:(p(T))++)(#:p(T)))') # PHI(x): helper method
        token('--', '(#x:x(PHI)(#y:y(#:#s:#x:x)(#:#s:#x:x))(F))', True) # (x)--: decrement
    else: token('--', '(#n:#f:#x:n(#g:#h:h(g(f)))(#y:x)(#y:y))', True) # (x)--: decrement
    token('-', '(#x:#y:y(--)(x))', True) # (x)-(y): subtract

    # Relational Operators
    token('Z', '(#x:x(#y:F)(T))') # Z(x): zero test
    token('>=', '(#x:#y:Z((y)-(x)))', True) # (x)>=(y): greater than or equal to
    token('<=', '(#x:#y:Z((x)-(y)))', True) # (x)<=(y): less than or equal to
    token('=', '(#x:#y:((x)>=(y))&((y)>=(x)))', True) # (x)=(y): equal to
    token('>', '(#x:#y:~(Z((x)-(y))))', True) # (x)>(y): greater than
    token('<', '(#x:#y:~(Z((y)-(x))))', True) # (x)<(y): less than

    # Recursion
    token('Y', '(#h:#f:f(#x:h(h)(f)(x)))(#h:#f:f(#x:h(h)(f)(x)))') # Y(#r:...): Y combinator

    # Div & Mod
    token('/', 'Y(#r:#x:#y:(x)<(y)(#:0)(#:(r((x)-(y))(y))++))', True) # (x)/(y): div
    token('%', 'Y(#r:#x:#y:(x)<(y)(#:x)(#:r((x)-(y))(y)))', True) # (x)%(y): mod

    # HCF & LCM
    token('HCF', 'Y(#r:#x:#y:Z(y)(#:x)(#:r(y)((x)%(y))))') # HCF(x)(y): highest common factor
    token('LCM', '(#x:#y:((x)*(y))/(HCF(x)(y)))') # LCM(x)(y): lowest common multiple

    # Rational Numbers
    token('FRAC', '(#x:#y:#p:p(#:x)(#:y))') # FRAC(x)(y): rational number x/y (ordered pair)
    token('SIMP', '(#p:#q:q(#:(p(T))/(HCF(p(T))(p(F))))(#:(p(F))/(HCF(p(T))(p(F)))))')
    token('+R', '(#p:#q:SIMP(#r:r(#:((p(T))*(q(F)))(++)((q(T))*(p(F))))(#:(p(F))*(q(F)))))')
    token('*R', '(#p:#q:SIMP(#r:r(#:(p(T))*(q(T)))(#:(p(F))*(q(F)))))')
    token('-R', '(#p:#q:SIMP(#r:r(#:((q(T))*(p(F)))(--)((p(T))*(q(F))))(#:(p(F))*(q(F)))))')
    token('/R', '(#p:#q:SIMP(#r:r(#:(p(T))*(q(F)))(#:(p(F))*(q(T)))))')

    # TODO Linked Lists
    #token('NULL', 'Null pointer (technically null element)')
    #token('NEWLIST', 'The definition of an empty list')
    #token('ISNULL', 'Test for null pointer')
    #token('APPEND', 'Take list {e1, {e2, {e3, ...}}} and element e0, and return {e0, {e1, {e2, {e3, ...}}}}')
    # "HEAD" of list l is just l(T) and "TAIL" of l is just l(F)
    # Define new (high-level) function "printList" to print elements of final list in order?
    #token('INDEX', 'Return index of element in list, numbered from 1 (0 meaning not found) - recursive definition')

def math_notation(exp: str) -> str:
    ''' Translates expanded Python expression into more compact mathematical notation. '''
    # TODO Variable names collide (implement alpha conversion)
    return exp.replace('lambda:','').replace('()','').replace(':', '.').replace('lambda ', chr(955))

def opening_paren(exp: str, closing_index: int) -> int:
    ''' Given string and index of closing parenthesis, returns index of corresponding opening
    parenthesis, or 0 if none exists. '''
    layers = 1
    for j in range(closing_index - 1, -1, -1):
        if exp[j] == ')': layers += 1
        elif exp[j] == '(': layers -= 1
        if layers == 0: return j
    return 0

def expand(exp: str, show_steps: bool = False) -> str:
    ''' Expands all low-level functions in given expression, replacing # with 'lambda'. '''
    global tokens
    chrs = '[A-Z0-9+\-*/%=<>~&|\^]'
    token_re = re.compile('(\({0:}+\)|{0:}+)'.format(chrs))
    if show_steps: print('Beginning Expansion of:\n\n' + exp + '\n')

    match = token_re.search(exp)
    while match:
        key = match.group(1)
        parenthesized = key[0] == '('
        if parenthesized: key = key[1:-1]
        subst = num(key) if key.isdigit() else tokens[key][0]

        span = match.span()
        if key.isdigit() or parenthesized or not tokens[key][1]:
            exp = exp[:span[0]] + subst + exp[span[1]:]
        else:
            op = opening_paren(exp, span[0] - 1)
            exp = exp[:op] + subst + exp[op:span[0]] + exp[span[1]:]

        if show_steps: print('>>> Expanding {}:\n\n{}\n'.format(match.group(1), exp))
        match = token_re.search(exp)
    return exp

def execute(exp: str, *args: Any, show_steps: bool = False) -> None:
    ''' Executes given lambda expression with arguments and prints result. '''
    for arg in args: exp += '({})'.format(arg)
    exp = expand(expand_lambda(exp), show_steps)
    math_exp = math_notation(exp)

    print('Python notation ({} characters):\n\n{}\n'.format(len(exp), exp))
    print('Mathematical notation ({} characters):\n\n{}\n'.format(len(math_exp), math_exp))

    start_time = clock()
    result = eval(exp)(lambda x: x+1)(0) # TODO Supposes numerical result - expand
    exec_time = round(clock() - start_time, 4)

    print('Execution Time: {} seconds\nResult: {}'.format(exec_time, result))

make_tokens(alt_pred=False)

if __name__ == '__main__':
    # High-level functions
    FACT = 'Y(#r:#n:Z(n)(#:1)(#:(n)*(r((n)--))))'
    FIB = 'Y(#r:#n:(n)<=(2)(#:1)(#:(r((n)--))(++)(r(((n)--)--))))'
    ACK = 'Y(#r:#m:#n:Z(m)(#:(n)++)(#:Z(n)(#:r((m)--)(1))(#:r((m)--)(r(m)((n)--)))))'

    execute(FIB, 8, show_steps=False)
    execute(FACT, 7)
    execute(ACK, 3, 4)
