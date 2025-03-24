#!/usr/bin/env python3

import re
from time import perf_counter
from typing import Union

# NOTE: Since Python uses eager evaluation, selection options must be wrapped in empty lambdas to
#       prevent execution of non-terminating recursive calls once base case is reached.
#   eg. (<condition>)(lambda: <True case>)(lambda: <False case>)

def num(n: int) -> str:
    ''' Returns Church numeral representation of n. '''
    return '(lambda s:lambda x:{}x{})'.format('s(' * int(n), ')' * int(n))

def python_notation(exp: str) -> str:
    ''' Expands 'λ' to 'lambda' & inserts missing lambdas to curry n-adic functions. '''
    exp = re.sub('λ([a-z]+)\.', lambda m: 'λ' + '.λ'.join(m.group(1)) + '.', exp)
    return exp.replace('λ.', 'lambda:').replace('λ', 'lambda ').replace('.', ':')

def token(tok: str, exp: str, exchange_arg: bool = False) -> None:
    ''' Add token with symbol 'tok' and expression 'exp' to dictionary. 'exchange_arg' indicates whether
    token is an operator which should precede its first argument. '''
    global tokens
    if exp[0] != '(' or exp[-1] != ')': exp = '(' + exp + ')' # wrap in parentheses if needed
    tokens[tok] = (python_notation(exp), exchange_arg)

def make_tokens(alt_pred: bool = False) -> None:
    ''' Creates tokens for low-level functions. Setting alt_pred lengthens expression, but can speed
    up execution. '''
    global tokens
    tokens = {} # type Dict[str, Tuple[str, bool]]

    # true & false
    token('T', 'λxy.x()') # T: true literal
    token('F', 'λxy.y()') # F: false literal

    # boolean operators
    token('~', 'λx.x(λ.F)(λ.T)')                      # ~(x): not
    token('&', 'λxy.x(λ.y)(λ.F)',               True) # (x)&(y): and
    token('|', 'λxy.x(λ.T)(λ.y)',               True) # (x)|(y): or
    token('^', 'λxy.((x)&(~(y)))|((~(x))&(y))', True) # (x)^(y): xor

    # arithmetic operators
    token('*',       'λxyz.x(y(z))',                         True) # (x)*(y): multiply
    token('**',      'λxy.y(x)',                             True) # (x)**(y): exponentiate
    token('++',      'λxyz.y(x(y)(z))',                      True) # (x)++: increment, (x)(++)(y): add
    if alt_pred:
        token('PHI', 'λpx.x(λ.(p(T))++)(λ.p(T))')                  # helper method
        token('--',  'λx.x(PHI)(λy.y(λ.λsx.x)(λ.λsx.x))(F)', True) # (x)--: decrement
    else:
        token('--',  'λnfx.n(λgh.h(g(f)))(λy.x)(λy.y)',      True) # (x)--: decrement
    token('-',       'λxy.y(--)(x)',                         True) # (x)-(y): subtract

    # relational operators
    token('Z',  'λx.x(λy.F)(T)')                   # Z(x): zero test
    token('>=', 'λxy.Z((y)-(x))',            True) # (x)>=(y): greater than or equal to
    token('<=', 'λxy.Z((x)-(y))',            True) # (x)<=(y): less than or equal to
    token('=',  'λxy.((x)>=(y))&((y)>=(x))', True) # (x)=(y): equal to
    token('>',  'λxy.~(Z((x)-(y)))',         True) # (x)>(y): greater than
    token('<',  'λxy.~(Z((y)-(x)))',         True) # (x)<(y): less than

    # recursion
    token('Y', 'λhf.f(λx.h(h)(f)(x)))(λhf.f(λx.h(h)(f)(x))') # Y(λr....): Y combinator

    # div & mod
    token('/', 'Y(λrxy.(x)<(y)(λ.0)(λ.(r((x)-(y))(y))++))', True) # (x)/(y): div
    token('%', 'Y(λrxy.(x)<(y)(λ.x)(λ.r((x)-(y))(y)))',     True) # (x)%(y): mod

    # HCF & LCM
    token('HCF', 'Y(λrxy.Z(y)(λ.x)(λ.r(y)((x)%(y))))') # HCF(x)(y): highest common factor
    token('LCM', 'λxy.((x)*(y))/(HCF(x)(y))')          # LCM(x)(y): lowest common multiple

    # rational numbers
    token('FRAC', 'λxyp.p(λ.x)(λ.y)') # FRAC(x)(y): rational number x/y (ordered pair)
    token('SIMP', 'λpq.q(λ.(p(T))/(HCF(p(T))(p(F))))(λ.(p(F))/(HCF(p(T))(p(F))))')
    token('+R',   'λpq.SIMP(λr.r(λ.((p(T))*(q(F)))(++)((q(T))*(p(F))))(λ.(p(F))*(q(F))))')
    token('*R',   'λpq.SIMP(λr.r(λ.(p(T))*(q(T)))(λ.(p(F))*(q(F))))')
    token('-R',   'λpq.SIMP(λr.r(λ.((q(T))*(p(F)))(--)((p(T))*(q(F))))(λ.(p(F))*(q(F))))')
    token('/R',   'λpq.SIMP(λr.r(λ.(p(T))*(q(F)))(λ.(p(F))*(q(T))))')

def math_notation(exp: str) -> str:
    ''' Translates expanded Python expression into more compact mathematical notation. '''
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
    ''' Expands all higher-level functions in given expression. '''
    global tokens
    chrs = '[A-Z0-9+\-*/%=<>~&|\^]'
    token_re = re.compile('(\({0:}+\)|{0:}+)'.format(chrs))
    if show_steps: print('Beginning Expansion of:\n\n' + exp + '\n')

    m = token_re.search(exp)
    while m:
        key = m.group(1)
        parenthesized = key[0] == '('
        if parenthesized: key = key[1:-1]
        subst = num(key) if key.isdigit() else tokens[key][0]

        span = m.span()
        if key.isdigit() or parenthesized or not tokens[key][1]:
            exp = exp[:span[0]] + subst + exp[span[1]:]
        else:
            op = opening_paren(exp, span[0] - 1)
            exp = exp[:op] + subst + exp[op:span[0]] + exp[span[1]:]

        if show_steps: print('>>> Expanding {}:\n\n{}\n'.format(m.group(1), exp))
        m = token_re.search(exp)
    return exp

def execute(exp: str, *args: Union[str, int], show_steps: bool = False) -> None:
    ''' Executes given lambda expression with arguments and prints result. '''
    for arg in args: exp += '({})'.format(arg)
    exp = expand(python_notation(exp), show_steps)
    math_exp = math_notation(exp)

    print('Python notation ({} characters):\n\n{}\n'.format(len(exp), exp))
    print('Mathematical notation ({} characters):\n\n{}\n'.format(len(math_exp), math_exp))

    start_time = perf_counter()
    result = eval(exp)(lambda x: x+1)(0) # TODO Add argument 'return_type' and change this accordingly
    exec_time = round(perf_counter() - start_time, 4)

    print('Execution Time: {} seconds\nResult: {}'.format(exec_time, result))

make_tokens(alt_pred=False)

if __name__ == '__main__':
    # High-level functions
    FACT = 'Y(λrn.Z(n)(λ.1)(λ.(n)*(r((n)--))))'
    FIB = 'Y(λrn.(n)<=(2)(λ.1)(λ.(r((n)--))(++)(r(((n)--)--))))'
    ACK = 'Y(λrmn.Z(m)(λ.(n)++)(λ.Z(n)(λ.r((m)--)(1))(λ.r((m)--)(r(m)((n)--)))))'

    execute(FIB, 8, show_steps=False)
    #execute(FACT, 7)
    #execute(ACK, 3, 4)
