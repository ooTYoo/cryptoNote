from myUtil.bnCalc import *
from operator import mul
from functools import reduce
from collections import Counter


prime_numbers = [2, 3, 5, 7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def brute_factoring(num):
    # factoring num < 100
    remainder = num
    rslt = []
    for a in prime_numbers:
        if a > remainder:
            return rslt
        if remainder % a > 0 :
            continue
        cnt = 0
        while remainder % a ==0:
            remainder /= a
            cnt += 1
        rslt.append((a,cnt))

def calc_eular_factoring(raw_list):
    cnt = Counter()
    for a in raw_list:
        cnt[a[0]] += a[1]-1
        rslt = brute_factoring(a[0]-1)
        for b in rslt:
            cnt[b[0]] += b[1]
    b = []
    for a in sorted(cnt.keys()):
        tmp = cnt.get(a)
        if tmp > 0:
            b.append((a,tmp))
    #b = [(a,cnt.get(a)) for a in sorted(cnt.keys())]
    #print(b)
    return b

def gen_para():
    #genreate N and \phi(N)
    #return (N,factoring(\phi(N))=[(p_i,e_i)])
    raw = [(31,1),(59,5),(89,7)]
    b = map(lambda x: x[0]**x[1],raw)
    N = reduce(mul, list(b))
    factor = calc_eular_factoring(raw)
    return N,factor

def chinese_remainder_calc(mlyst):
    # mlyst = [(a1,n1),...,(ar,nr)]
    # return the x
    factor = [a[1] for a in mlyst]
    total_N = reduce(mul,factor)
    Ni = [total_N//a[1] for a in mlyst]
    Mi = []
    for a,b in zip(factor, Ni):
        d, x, y = extendGcd(b,a)
        if d != 1:
            print("[*] error, please input")
        Mi.append(x)
    total = 0
    for i in range(len(mlyst)):
        total += Mi[i] * Ni[i] * mlyst[i][0]

    # self check
    # for a in mlyst:
    #    print(total%a[1] == a[0],end=' ')
    return total

def baby_step_gaint_step(a,b,N):
    # solve simple discrete log problem
    # return x, s.t. a^x = b on G, with |G| = n
    # focused on G = Z_N over p^k
    # m = math.ceil(math.sqrt(n))

    # general baby-step hashmap
    m = 300
    plist, tmp = {},1
    for i in range(m):
        plist[tmp] = i
        tmp = tmp * a % N
        if tmp in plist.keys():
            break

    # calc a^-m
    ainv = mod_inv_gcd(a,N)
    A = mod_exp(ainv,m, N)

    # searching ...
    R = b
    for i in range(N//m+1):
        if R in plist.keys():
            return i*m + plist[R]
        R = R * A % N
    return -1

def pohlig_hellman(a,b,N,factor):
    # solve a^x = b over GF(N)
    # factor = [(p1,e1),...,(pk,ek)] is factoring of |G|
    # return x
    n = reduce(mul,[a[0]**a[1] for a in factor])
    mlyst = []
    for pi,ei in factor:
        subfactor = pi**ei
        cofactor = n//subfactor
        a1 = mod_exp(a,cofactor,N)
        b1 = mod_exp(b,cofactor,N)
        sol_over_subgroup = baby_step_gaint_step(a1,b1,N)
        mlyst.append((sol_over_subgroup,subfactor))
    print(mlyst)
    rslt = chinese_remainder_calc(mlyst)
    rslt = rslt % n
    checking = mod_exp(a,rslt,N)
    print(checking==b)
    print(rslt)
    return rslt

def main():
    N,factor = gen_para()
    print(factor)
    a = 7
    key = 32
    b = mod_exp(a,key, N)
    subfactor = [a[0]**a[1] for a in factor]
    sol = [key % item for item in subfactor]
    print("subgroup with order ",subfactor)
    print("sol over subgroup is", sol)
    ans = pohlig_hellman(a,b,N,factor)


if __name__ == "__main__":
    main()
