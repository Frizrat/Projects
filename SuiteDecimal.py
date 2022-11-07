from decimal import *
from math import log10

def vn(v,n): return v+1+int(log10(n))
    
def wn(w, v, n): return w+n/Decimal(10**(v-1))

jusqua = int(input('Entrez jusqu\'à combien allez: '))
v = 1
w = 0
for n in range(1,jusqua+1):
    v = vn(v, n)
    getcontext().prec = v
    w = wn(w, v, n)
print(w)
