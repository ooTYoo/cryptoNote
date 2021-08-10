# ecc related defines
from ecc_domain_para import ecc_para_sec2
import bnCalc

def str2bn(hexstr):
    return int(hexstr.replace(" ",""),16)

class EccPoint():
    def __init__(self,x=None,y=None,inf=False):
        self.x = x
        self.y = y
        self.inf = inf

    def is_inf(self):
        return self.inf

class EccDomain():
    def __init__(self,k=256):
        if k==256:
            curve = "secp256k1"
            self.klen = 256
            self.p = str2bn(ecc_para_sec2[curve]["p"])
            self.a = str2bn(ecc_para_sec2[curve]["a"])
            self.b = str2bn(ecc_para_sec2[curve]["b"])
            self.n = str2bn(ecc_para_sec2[curve]["n"])
            self.h = str2bn(ecc_para_sec2[curve]["h"])
            self.G = EccPoint(x=str2bn(ecc_para_sec2[curve]["Gx"]), y=str2bn(ecc_para_sec2[curve]["Gy"]))

    def on_curve(self,eccp):
        if eccp.inf:
            return True
        rslt = eccp.x * eccp.x * eccp.x + self.a * eccp.x + self.b
        rslt = rslt - eccp.y*eccp.y
        rslt = rslt % self.p
        return rslt==0

    def eqs(self, eccpa, eccpb):
        if eccpa.inf and eccpb.inf:
            return True
        if eccpa.inf == eccpb.inf:
            return (eccpa.x - eccpb.x)%self.p ==0 and (eccpa.y - eccpb.y)%self.p ==0
        return False

    def pf(self,eccp):
        if eccp.inf:
            print("inf point")
            return
        print("x",eccp.x.to_bytes(self.klen//8,byteorder='big', signed=False).hex())
        print("y",eccp.y.to_bytes(self.klen//8,byteorder='big', signed=False).hex())


    def point_add(self, eccpa,eccpb):
        if eccpa.inf:
            return eccpb
        if eccpb.inf:
            return eccpa
        if (eccpa.y + eccpb.y) % self.p == 0:
            return EccPoint(inf=True)
        if self.eqs(eccpa, eccpb):
            s = (3*eccpa.x*eccpa.x + self.a) % self.p
            s = s * bnCalc.mod_inv_gcd((2*eccpa.y)%self.p, self.p) % self.p
            xr = (s*s - 2*eccpa.x) % self.p
            yr = (eccpa.y + s * (xr - eccpa.x)) % self.p
            yr = self.p - yr
            return EccPoint(x=xr, y=yr)
        else:
            s = (eccpa.y -eccpb.y) % self.p
            s = s * bnCalc.mod_inv_gcd((eccpa.x - eccpb.x)%self.p, self.p) % self.p
            xr = (s*s - eccpa.x -eccpb.x) % self.p
            yr = (eccpa.y + s*(xr - eccpa.x)) % self.p
            yr = self.p - yr
            return EccPoint(x=xr, y=yr)

    def point_mult(self, scalar, eccp=None):
        #calc scalar* eccP on curve
        if eccp is None:
            eccp = self.G
        bins = bin(scalar)[2:]
        rslt = EccPoint(inf=True)
        for x in bins:
            rslt = self.point_add(rslt, rslt)
            if x=='1':
                rslt = self.point_add(rslt, eccp)
        return rslt


if __name__ == "__main__":
    ecc = EccDomain(256)
    print(ecc.on_curve(ecc.G))
    eccp = ecc.point_add(ecc.G,ecc.G)
    eccp2 = ecc.point_mult(2, ecc.G)
    eccp3 = ecc.point_mult(ecc.n,ecc.G)
    ecc.pf(eccp3)
    print(ecc.eqs(eccp,eccp2))
    ecc.pf(eccp2)