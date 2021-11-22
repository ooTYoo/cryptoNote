def gcd(a,b):
    if a < b:
        return gcd(b,a)
    if b==0:
        return a
    else:
        return gcd(b,a%b)

def extendGcd(a,b):
    # a*x + b*y = d
    if a < b:
        d,x1,y1 = extendGcd(b,a)
        return (d,y1,x1)
    if b==0:
        return (a,1,0)
    else:
        d,x1,y1 = extendGcd(b,a%b)
        return (d,y1,x1-(a//b)*y1)

def mod_inv_gcd(a,n):
    d,x,y = extendGcd(a,n)
    if d != 1:
        print("error,gcd(a,n)!=1")
        return None
    return x%n

def mod_exp(a,b,n):
    #return a^b mod n
    bins = bin(b)[2:]
    rslt = 1
    for x in bins:
        rslt *= rslt
        if x=='1':
            rslt *= a
        rslt = rslt %n
    return rslt
