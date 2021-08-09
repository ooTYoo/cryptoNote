# ecc related defines
class EccPoint():
    def __init__(self,x=None,y=None,inf=False):
        self.x = x
        self.y = y
        self.inf = inf

    def is_inf(self):
        return self.inf


class EccDomainPara():
    def __init__(self):
        self.inner_dict = {
            256:{
                'p':0,
                'h':0,
                'n':0,
                'a':0,
                'b':0,
                'G':EccPoint()
            }
        }

class EccDomain():
    def __init__(self,domain_para):
        self.para = domain_para

    def eqs(self,eccpa,eccpb):
        if eccpa.inf and eccpb.inf:
            return True
        if self.inf == eccp.inf:
            return (eccpa.x - eccpb.x)%self.para.p ==0 and (eccpa.y - eccpb.y)%self.para.p ==0
        return False

    def point_add(self, eccpa,eccpb):
        if eccpa.inf:
            return eccpb
        if eccpb.inf:
            return eccpa
        if (eccpa.y + eccpb.y) % self.para.p == 0:
            return EccPoint(inf=True)
        if self.eqs(eccpa,eccpb):
            pass #p_double
        pass #p_add


