import re
from time import clock

# NOTE: Since Python uses eager evaluation, selection options should be wrapped in empty lambdas to
#       prevent execution of non-terminating recursive calls once the base case is reached.
#   eg. (<condition>)(lambda: <True case>)(lambda: <False case>)

def num(n):
    ''' Returns Church numeral representation of n. '''
    return '(#s:#x:{}x{})'.format('s(' * int(n), ')' * int(n))

def token(tok, string, arity=0):
    global tokens
    tokens[tok] = (string, arity)

def make_tokens(alt_pred=False):
    ''' Creates tokens for low-level functions. Setting alt_pred lengthens expression, but can speed
    up execution. '''
    # True & False
    token('T', '(#x:#y:x())')
    token('F', '(#x:#y:y())')

    # Boolean Operators
    token('~', '(#x:x(#:F)(#:T))') # Not
    token('&', '(#x:#y:x(#:y)(#:F))') # And
    token('|', '(#x:#y:x(#:T)(#:y))') # Or
    token('^', '(#x:#y:|(&(x)(~(y)))(&(~(x))(y)))') # Xor

    # Arithmetic Operators
    token('*', '(#x:#y:#z:x(y(z)))') # Multiply
    token('**', '(#x:#y:y(x))') # Exponentiate
    token('++', '(#x:#y:#z:y(x(y)(z)))') # Increment
    if alt_pred:
        token('PHI', '(#p:#x:x(#:++(p(T)))(#:p(T)))')
        token('--', '(#x:x(PHI)(#y:y(#:#s:#x:x)(#:#s:#x:x))(F))') # Decrement
    else: token('--', '(#n:#f:#x:n(#g:#h:h(g(f)))(#y:x)(#y:y))') # Decrement
    token('+', '(#x:#y:x(++)(y))') # Sum
    token('-', '(#x:#y:y(--)(x))') # Difference

    # Relational Operators
    token('Z', '(#x:x(#y:F)(T))') # Test for zero
    token('>=', '(#x:#y:Z(-(y)(x)))')
    token('<=', '(#x:#y:Z(-(x)(y)))')
    token('=', '(#x:#y:&(>=(x)(y))(>=(y)(x)))')
    token('>', '(#x:#y:~(Z(-(x)(y))))')
    token('<', '(#x:#y:~(Z(-(y)(x))))')

    # Recursion
    token('Y', '(#h:#f:f(#x:h(h)(f)(x)))(#h:#f:f(#x:h(h)(f)(x)))')

    # Div & Mod
    token('/', 'Y(#r:#x:#y:<(x)(y)(#:0)(#:++(r(-(x)(y))(y))))') # Div
    token('%', 'Y(#r:#x:#y:<(x)(y)(#:x)(#:r(-(x)(y))(y)))') # Mod

    # HCF & LCM
    token('HCF', 'Y(#r:#x:#y:Z(y)(#:x)(#:r(y)(%(x)(y))))')
    token('LCM', '(#x:#y:/(*(x)(y))(HCF(x)(y)))')

    # Rational Numbers
    token('FRAC', '(#x:#y:#p:p(#:x)(#:y))')
    token('SIMP', '(#p:#q:q(#:/(p(T))(HCF(p(T))(p(F))))(#:/(p(F))(HCF(p(T))(p(F)))))')
    token('+R', '(#p:#q:SIMP(#r:r(#:(*(p(T))(q(F)))(++)(*(q(T))(p(F))))(#:*(p(F))(q(F)))))')
    token('*R', '(#p:#q:SIMP(#r:r(#:*(p(T))(q(T)))(#:*(p(F))(q(F)))))')
    token('-R', '(#p:#q:SIMP(#r:r(#:(*(q(T))(p(F)))(--)(*(p(T))(q(F))))(#:*(p(F))(q(F)))))')
    token('/R', '(#p:#q:SIMP(#r:r(#:*(p(T))(q(F)))(#:*(p(F))(q(T)))))')

    # TODO Linked Lists
    #token('NULL', 'Null pointer (technically null element)')
    #token('NEWLIST', 'The definition of an empty list')
    #token('ISNULL', 'Test for null pointer')
    #token('APPEND', 'Take list {e1, {e2, {e3, ...}}} and element e0, and return {e0, {e1, {e2, {e3, ...}}}}')
    # "HEAD" of list l is just l(T) and "TAIL" of l is just l(F)
    # Define new (high-level) function "printList" to print elements of final list in order?
    #token('INDEX', 'Return index of element in list, numbered from 1 (0 meaning not found) - recursive definition')

def math_notation(exp):
    ''' Translates expanded Python expression into more compact mathematical notation. '''
    # TODO Variable names collide (implement alpha conversion)
    return exp.replace('lambda:','').replace('()','').replace(':', '.').replace('lambda ', chr(955))

def expand_lambda(exp):
    ''' Expands '#' to 'lambda'. Used only for compactness in implementation. '''
    return exp.replace('#:', 'lambda:').replace('#', 'lambda ')

def expand(exp, show_steps=False):
    ''' Expands all low-level functions in given expression, replacing # with 'lambda'. '''
    # TODO Implement arity and infix / postfix operators
    global tokens
    exp = expand_lambda(exp)

    chrs = '[A-Z0-9+\-*/%=<>~&|\^]'
    token_re = re.compile('\({0:}+\)|{0:}+'.format(chrs))
    if show_steps: print('Beginning Expansion of:\n\n' + exp + '\n')

    match = token_re.search(exp)
    while match:
        key = match.group(0)
        if key[0] == '(': key = key[1:-1]

        subst = expand_lambda(num(key) if key.isdigit() else tokens[key][0])
        exp = exp[:match.span()[0]] + subst + exp[match.span()[1]:]

        if show_steps: print('>>> Expanding {}:\n\n{}\n'.format(match.group(0), exp))
        match = token_re.search(exp)
    return exp

def execute(exp, *args, show_steps=False):
    ''' Executes given lambda expression with arguments and prints result. '''
    for arg in args: exp += '({})'.format(arg)
    exp = expand(exp, show_steps)
    math_exp = math_notation(exp)

    print('Python notation ({} characters):\n\n{}\n'.format(len(exp), exp))
    print('Mathematical notation ({} characters):\n\n{}\n'.format(len(math_exp), math_exp))

    start_time = clock()
    result = eval(exp)(lambda x: x+1)(0) # TODO Supposes numerical result. Extra functionality
    exec_time = round(clock() - start_time, 4)

    print('Execution Time: {} seconds\nResult: {}'.format(exec_time, result))

tokens = {}
make_tokens(alt_pred=False)

if __name__ == '__main__':
    # High-level functions
    FACT = 'Y(#r:#n:Z(n)(#:1)(#:*(n)(r(--(n)))))'
    FIB = 'Y(#r:#n:<=(n)(2)(#:1)(#:(r(--(n)))(++)(r(--(--(n))))))'
    ACK = 'Y(#r:#m:#n:Z(m)(#:++(n))(#:Z(n)(#:r(--(m))(1))(#:r(--(m))(r(m)(--(n))))))'

    execute(FIB, 8, show_steps=False)
    execute(FACT, 7)
    execute(ACK, 3, 4)
