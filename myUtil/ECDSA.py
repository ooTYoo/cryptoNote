from eccUtil import EccPoint,EccDomain
from Cryptodome.Random import get_random_bytes
from Cryptodome.Hash import SHA256
import bnCalc

Ecc = EccDomain(256)

def generate_kpair():
    dk = 0
    while dk==0 or dk == (Ecc.n-1):
        dk = get_random_bytes(Ecc.klen//8)
        dk = int.from_bytes(dk, byteorder="big", signed=False)
        dk = dk % Ecc.n
    pk = Ecc.point_mult(dk, Ecc.G)
    return (dk, pk)

def ecc_sign(mesg, sk):
    hash = SHA256.new()
    hash.update(mesg)
    m = int.from_bytes(hash.digest(),byteorder="big", signed=False)
    z = bin(m)[0:len(bin(Ecc.n))]
    z = int(z,2)
    r,s =0,0
    while r==0 or s==0:
        r, s, k = 0, 0, 0
        while k==0 or k == (Ecc.n-1):
            k = get_random_bytes(Ecc.klen//8)
            k = int.from_bytes(k, byteorder="big", signed=False)
            k = k % Ecc.n
        eccp = Ecc.point_mult(k, Ecc.G)
        r = eccp.x % Ecc.n
        if r==0:
            continue
        s = bnCalc.mod_inv_gcd(k, Ecc.n)
        s = s*(z + r* sk) % Ecc.n
    return (r, s)

def ecc_verfy(mesg, pk, sign):
    if pk.inf:
        return False
    if not Ecc.on_curve(pk):
        return False
    if not Ecc.point_mult(Ecc.n, pk).inf:
        return False
    r,s = sign
    if r==0 or r >= Ecc.n or s==0 or s >= Ecc.n:
        return False

    hash = SHA256.new()
    hash.update(mesg)
    m = int.from_bytes(hash.digest(),byteorder="big", signed=False)
    z = bin(m)[0:len(bin(Ecc.n))]
    z = int(z,2)
    invs = bnCalc.mod_inv_gcd(s, Ecc.n)
    u1 = z * invs % Ecc.n
    u2 = r * invs % Ecc.n
    eccp1 = Ecc.point_mult(u1,Ecc.G)
    eccp2 = Ecc.point_mult(u2,pk)
    eccp3 = Ecc.point_add(eccp1, eccp2)
    if eccp3.inf:
        return False
    return (eccp3.x - r) % Ecc.n == 0


if __name__ == "__main__":
    dk, pk = generate_kpair()
    mesg = b'hello, world'
    sign1 = ecc_sign(mesg,dk)
    print(ecc_verfy(mesg, pk,sign1))