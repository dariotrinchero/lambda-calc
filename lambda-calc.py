import re
from time import clock

# NOTE: Since Python uses eager evaluation, selection options should be wrapped in empty lambdas to
#       prevent execution of non-terminating recursive calls once the base case is reached.
#   eg. (<condition>)(lambda: <True case>)(lambda: <False case>)

def num(n):
    ''' Returns the Church numeral equivalent of n '''
    return '(lambda s: lambda x: '+ 's('*int(n) + 'x' + ')'*int(n) + ')'

def initializeDict(altPred=False):
    ''' Initializes the identifier dictionary for low-level functions '''
    # NOTE: Setting altPred to True will lengthen the expression, but can sometimes speed up execution significantly
    global nameDict
    nameDict = {}

    # TRUE AND FALSE
    nameDict['T'] = '(lambda x: lambda y: x())'
    nameDict['F'] = '(lambda x: lambda y: y())'

    # BOOLEAN OPERATIONS
    nameDict['NOT'] = '(lambda x: x(lambda: F)(lambda: T))'
    nameDict['AND'] = '(lambda x: lambda y: x(lambda: y)(lambda: F))'
    nameDict['OR'] = '(lambda x: lambda y: x(lambda: T)(lambda: y))'
    nameDict['XOR'] = '(lambda x: lambda y: OR(AND(x)(NOT(y)))(AND(NOT(x))(y)))'

    # BASIC ARITHMETIC OPERATIONS
    nameDict['S'] = '(lambda x: lambda y: lambda z: y(x(y)(z)))'
    nameDict['M'] = '(lambda x: lambda y: lambda z: x(y(z)))'
    nameDict['POW'] = '(lambda x: lambda y: y(x))'
    if altPred:
        nameDict['PHI'] = '(lambda p: lambda x: x(lambda: S(p(T)))(lambda: p(T)))'
        nameDict['P'] = '(lambda x: x(PHI)(lambda y: y(lambda: lambda s: lambda x: x)(lambda: lambda s: lambda x: x))(F))'
    else: nameDict['P'] = '(lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda y: x)(lambda y: y))'

    # EQUALITIES AND INEQUALITIES
    nameDict['Z'] = '(lambda x: x(lambda y: F)(T))'
    nameDict['GTE'] = '(lambda x: lambda y: Z(x(P)(y)))'
    nameDict['LTE'] = '(lambda x: lambda y: Z(y(P)(x)))'
    nameDict['E'] = '(lambda x: lambda y: AND(GTE(x)(y))(GTE(y)(x)))'
    nameDict['GT'] = '(lambda x: lambda y: NOT(Z(y(P)(x))))'
    nameDict['LT'] = '(lambda x: lambda y: NOT(Z(x(P)(y))))'

    # RECURSION
    nameDict['Y'] = '(lambda h: lambda f: f(lambda x: h(h)(f)(x)))(lambda h: lambda f: f(lambda x: h(h)(f)(x)))'

    # DIV AND MOD
    nameDict['DIV'] = 'Y(lambda r: lambda x: lambda y: LT(x)(y)(lambda: 0)(lambda: S(r(y(P)(x))(y))))'
    nameDict['MOD'] = 'Y(lambda r: lambda x: lambda y: LT(x)(y)(lambda: x)(lambda: r(y(P)(x))(y)))'

    # HCF AND LCM
    nameDict['HCF'] = 'Y(lambda r: lambda x: lambda y: Z(y)(lambda: x)(lambda: r(y)(MOD(x)(y))))'
    nameDict['LCM'] = '(lambda x: lambda y: DIV(M(x)(y))(HCF(x)(y)))'

    # RATIONAL NUMBERS
    nameDict['FRAC'] = '(lambda x: lambda y: lambda p: p(lambda: x)(lambda: y))'
    nameDict['SIM'] = '(lambda p: lambda q: q(lambda: DIV(p(T))(HCF(p(T))(p(F))))(lambda: DIV(p(F))(HCF(p(T))(p(F)))))'
    nameDict['ADDR'] = '(lambda p: lambda q: SIM(lambda r: r(lambda: (M(p(T))(q(F)))(S)(M(q(T))(p(F))))(lambda: M(p(F))(q(F)))))'
    nameDict['MULTR'] = '(lambda p: lambda q: SIM(lambda r: r(lambda: M(p(T))(q(T)))(lambda: M(p(F))(q(F)))))'
    nameDict['SUBR'] = '(lambda p: lambda q: SIM(lambda r: r(lambda: (M(q(T))(p(F)))(P)(M(p(T))(q(F))))(lambda: M(p(F))(q(F)))))'
    nameDict['DIVR'] = '(lambda p: lambda q: SIM(lambda r: r(lambda: M(p(T))(q(F)))(lambda: M(p(F))(q(T)))))'

    # LINKED LISTS
    nameDict['NULL'] = 'Null pointer (technically null element)'
    nameDict['NEWLIST'] = 'The definition of an empty list'
    nameDict['ISNULL'] = 'Test for null pointer'
    nameDict['APPEND'] = 'Take list {e1, {e2, {e3, ...}}} and element e0, and return {e0, {e1, {e2, {e3, ...}}}}'
    # "HEAD" of list l is just l(T) and "TAIL" of l is just l(F)
    # Define new (high-level) function "printList" to print elements of final list in order?
    nameDict['INDEX'] = 'Return index of element in list, numbered from 1 (0 meaning not found) - recursive definition'

def removeSpaces(expression):
    ''' Removes unnecessary spaces from expression '''
    return expression.replace('lambda ', '#').replace(' ', '').replace('#', 'lambda ')

def mathNotation(expression):
    ''' Translates expanded Python expression into more compact mathematical notation '''
    return expression.replace('lambda:','').replace('()','').replace(':', '.').replace('lambda ', chr(955))

def expand(expression, showExpansion=False):
    ''' Expands all nameDict in a given expression '''
    newExpression = removeSpaces(expression[:])
    identifier = re.compile(r'\([A-Z0-9]+\)|[A-Z0-9]+') # One or more capital letters or numbers, possibly enclosed in parentheses
    if showExpansion: print('BEGINNING EXPANSION OF:\n\n' + newExpression + '\n')
    
    match = identifier.search(newExpression)
    while match:
        key = match.group(0)
        if key[0]=='(': key = key[1:-1]
        substitution = num(key) if key.isdigit() else nameDict[key]
        
        newExpression = newExpression[:match.span()[0]] + removeSpaces(substitution) + newExpression[match.span()[1]:]
        if showExpansion: print('>>> Expanding', match.group(0) + ':\n\n' + newExpression + '\n')
        
        match = identifier.search(newExpression)
    return newExpression

def execute(expression, *args, showExpansion=False):
    ''' Executes the given lambda expression with arguments and prints result '''
    for arg in args: expression = expression + '(' + str(arg) + ')'
    executable = expand(expression, showExpansion)
    mathExpression = mathNotation(executable)
    
    print('EXPANDED EXPRESSION - Python notation (' + str(len(executable)) + ' characters):\n\n' + executable + '\n')
    print('EXPANDED EXPRESSION - Mathematical notation (' + str(len(mathExpression)) + ' characters):\n\n' + mathExpression + '\n')

    start_time = clock()
    result = eval(executable)(lambda x: x+1)(0)
    time_elapsed = round(clock() - start_time, 4)
    
    print('EXECUTION TIME:', time_elapsed, 'seconds')
    print('NUMERICAL RESULT:', result, '\n')



# High-level functions

initializeDict(altPred=False)

FACT = 'Y(lambda r: lambda n: Z(n)(lambda: 1)(lambda: M(n)(r(P(n)))))'
FIB = 'Y(lambda r: lambda n: LTE(n)(2)(lambda: 1)(lambda: (r(P(n)))(S)(r(P(P(n))))))'
ACK = 'Y(lambda r: lambda m: lambda n: Z(m)(lambda: S(n))(lambda: Z(n)(lambda: r(P(m))(1))(lambda: r(P(m))(r(m)(P(n))))))'

execute(FIB, 8, showExpansion=False)
#execute(FACT, 7)
#execute(ACK, 3, 4)
