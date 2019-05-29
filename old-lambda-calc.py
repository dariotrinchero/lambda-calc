# Dario Trinchero

# CHURCH NUMERALS

def nums(n):
    ''' Generates a list of Church numerals from 0 to n '''
    num = (lambda s: lambda x: x)
    for i in range(n):
        yield num
        num = (lambda x: lambda y: lambda z: y(x(y)(z)))(num)
N = list(nums(50)) 

def printnum(n):
    ''' Prints the decimal equivalent of a Church numeral n '''
    print(n(lambda x: x+1)(0))

# TRUE AND FALSE

T = (lambda x: lambda y: x()) # TRUE. T(lambda: x)(lambda: y) returns x
F = (lambda x: lambda y: y()) # FALSE. F(lambda: x)(lambda: y) returns y

# BOOLEAN OPERATIONS

NOT = (lambda x: x(lambda: F)(lambda: T))
NOTL = (lambda x: x()(lambda: F)(lambda: T)) # Arguments must be wrapped in a lambda function (for Z function) eg. NOTL(lambda: T)
AND = (lambda x: lambda y: x(lambda: y)(lambda: F))
OR = (lambda x: lambda y: x(lambda: T)(lambda: y))
XOR = (lambda x: lambda y: OR(AND(x)(NOT(y)))(AND(NOT(x))(y)))

# BASIC ARITHMETIC OPERATIONS

S = (lambda x: lambda y: lambda z: y(x(y)(z))) # S(x)=x+1. y(S)(x)=x+y
M = (lambda x: lambda y: lambda z: x(y(z))) # M(x)(y)=x*y
POW = (lambda x: lambda y: y(x))

PHI = (lambda p: lambda x: x(lambda: S(p(T)))(lambda: p(T))) # Takes a pair (n, n-1) and returns (n+1, n)
P = (lambda x: x(PHI)(lambda y: y(lambda: lambda s: lambda x: x)(lambda: lambda s: lambda x: x))(F)) # P(x)=x-1. y(P)(x)=x-y
# Pairs are represented in lambda calculus as p=(lambda z: z(a)(b)). p(T)=a, and p(F)=b
# P Works by applying PHI x times to the pair 00 and extracting the second number, x-1

# EQUALITIES AND INEQUALITIES

Z = (lambda x: x(F)(NOTL)(lambda: F)) # x==0 ?
GTE = (lambda x: lambda y: Z(x(P)(y))) # x>=y ? 
E = (lambda x: lambda y: AND(GTE(x)(y))(GTE(y)(x))) # x==y ?
LT = (lambda x: lambda y: NOT(GTE(x)(y))) # x<y ?
GT = (lambda x: lambda y: AND(GTE(x)(y))(NOT(E(x)(y)))) # x>y ?
LTE = (lambda x: lambda y: OR(LT(x)(y))(E(x)(y))) # x<=y ?

# RECURSION

Y = (lambda h: lambda f: f(lambda x: h(h)(f)(x)))(lambda h: lambda f: f(lambda x: h(h)(f)(x)))

# DIV AND MOD

DIV = Y(lambda r: lambda x: lambda y: LT(x)(y)(lambda: N[0])(lambda: S(r(y(P)(x))(y))))
MOD = Y(lambda r: lambda x: lambda y: LT(x)(y)(lambda: x)(lambda: r(y(P)(x))(y)))

# HCF AND LCM

HCF = Y(lambda r: lambda x: lambda y: Z(y)(lambda: x)(lambda: r(y)(MOD(x)(y))))
LCM = (lambda x: lambda y: DIV(M(x)(y))(HCF(x)(y)))

# RATIONAL NUMBERS

FRAC = (lambda x: lambda y: lambda p: p(lambda: x)(lambda: y))
SIM = (lambda p: lambda q: q(lambda: DIV(p(T))(HCF(p(T))(p(F))))(lambda: DIV(p(F))(HCF(p(T))(p(F)))))
SR = (lambda p: lambda q: SIM(lambda r: r(lambda: (M(p(T))(q(F)))(S)(M(q(T))(p(F))))(lambda: M(p(F))(q(F)))))
MR = (lambda p: lambda q: SIM(lambda r: r(lambda: M(p(T))(q(T)))(lambda: M(p(F))(q(F)))))
PR = (lambda p: lambda q: SIM(lambda r: r(lambda: (M(q(T))(p(F)))(P)(M(p(T))(q(F))))(lambda: M(p(F))(q(F)))))
DR = (lambda p: lambda q: SIM(lambda r: r(lambda: M(p(T))(q(F)))(lambda: M(p(F))(q(T)))))
# Rational a/b is encoded as a pair using FRAC

# OTHER FUNCTIONS

FACT = Y(lambda r: lambda n: Z(n)(lambda: N[1])(lambda: M(n)(r(P(n)))))

FIB = Y(lambda r: lambda n: LT(n)(N[3])(lambda: N[1])(lambda: (r(P(n)))(S)(r(P(P(n))))))

FIB2 = (lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda r:lambda n:(lambda x:lambda y:(lambda x:x(lambda:(lambda x:\
lambda y:y()))(lambda:(lambda x:lambda y:x())))((lambda x:lambda y:(lambda x:x(lambda x:lambda y:y())(lambda x:x()(lambda:(lambda x:lambda y:y()))(lambda:\
(lambda x:lambda y:x())))(lambda:(lambda x:lambda y:y())))(x(lambda x:x(lambda p:lambda x:x(lambda:(lambda x:lambda y:lambda z:y(x(y)(z)))(p(lambda x:lambda y:\
x())))(lambda:p(lambda x:lambda y:x())))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))(lambda x:lambda y:y()))(y)))(x)(y)))(n)(lambda s:\
lambda x: s(s(s(x))))(lambda:(lambda s: lambda x: s(x)))(lambda:(r((lambda x:x((lambda p:lambda x:x(lambda:(lambda x:lambda y:lambda z:y(x(y)(z)))(p(lambda x:\
lambda y:x())))(lambda:p(lambda x:lambda y:x()))))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))(lambda x:lambda y:y()))(n)))(lambda x:\
lambda y:lambda z:y(x(y)(z)))(r((lambda x:x((lambda p:lambda x:x(lambda:(lambda x:lambda y:lambda z:y(x(y)(z)))(p(lambda x:lambda y:x())))(lambda:p(lambda x:\
lambda y:x()))))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))(lambda x:lambda y:y()))((lambda x:x((lambda p:lambda x:x(lambda:(lambda x:\
lambda y:lambda z:y(x(y)(z)))(p(lambda x:lambda y:x())))(lambda:p(lambda x:lambda y:x()))))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))\
(lambda x:lambda y:y()))(n))))))
printnum(FIB2(N[8]))
# Expanded Fibonacci

GIFTS = (lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda r:lambda n:(lambda x:x(lambda x:lambda y:y())\
(lambda x:x()(lambda:(lambda x:lambda y:y()))(lambda:(lambda x:lambda y:x())))(lambda:(lambda x:lambda y:y())))(n)(lambda:(lambda s:lambda x:x))(lambda:\
((lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda h:lambda f:f(lambda x:h(h)(f)(x)))(lambda r:lambda n:(lambda x:x(lambda x:lambda y:y())((lambda x:x()\
(lambda:(lambda x:lambda y:y()))(lambda:(lambda x:lambda y:x()))))(lambda:(lambda x:lambda y:y())))(n)(lambda:(lambda s:lambda x:x))(lambda:(n)(lambda x:\
lambda y:lambda z:y(x(y)(z)))(r((lambda x:x((lambda p:lambda x:x(lambda:(lambda x:lambda y:lambda z:y(x(y)(z)))(p((lambda x:lambda y:x()))))(lambda:\
p((lambda x:lambda y:x())))))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))((lambda x:lambda y:y())))(n)))))(n))(lambda x:lambda y:\
lambda z:y(x(y)(z)))(r((lambda x:x((lambda p:lambda x:x(lambda:(lambda x:lambda y:lambda z:y(x(y)(z)))(p((lambda x:lambda y:x()))))(lambda:p((lambda x:\
lambda y:x())))))(lambda y:y(lambda:lambda s:lambda x:x)(lambda:lambda s:lambda x:x))((lambda x:lambda y:y())))(n)))))
# Number of gifts my true love gave to me by a given day of Christmas
