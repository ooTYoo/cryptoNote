from Crypto.Util import number
from bnUtil import mod_exp

def gen_rsa_keypair(nbit=1024, e=0x10001):
    p = number.getPrime(nbit//2)
    q = number.getPrime(nbit//2)
    N = p*q
    d = number.inverse(e,(p-1)*(q-1))
    #N = 0x5a2ff1de51982c63
    #d = 0x14ff38963ccd83f1
    return (N,e,d)

class rsaOracleServer():
    def __init__(self,N):
        self.bitlen = N
        self.keys = gen_rsa_keypair(self.bitlen)
        self.Nkey, self.ekey, self.dkey = self.keys

    def pf_keys(self):
        print("N:",self.Nkey.to_bytes(self.bitlen//8,'big').hex())
        print("e:", self.ekey.to_bytes(self.bitlen // 8, 'big').hex())
        print("d:", self.dkey.to_bytes(self.bitlen // 8, 'big').hex())

    def give_me_pk(self):
        return (self.Nkey,self.ekey)

    def dec_mesg(self,ct_num):
        rslt = mod_exp(ct_num,self.dkey,self.Nkey)
        return rslt

    def enc_mesg(self,pt_num):
        rslt = mod_exp(pt_num,self.ekey,self.Nkey)
        return rslt

    def parity_oracle(self,ct):
        rslt = self.dec_mesg(ct)
        return rslt%2

    def pkcs_padding_oracle(self,ct):
        # a very weak pkcs padding check
        rslt = self.dec_mesg(ct)
        hexform = rslt.to_bytes(self.bitlen // 8, 'big').hex()
        return hexform[0:4]=='0002'

    def give_me_a_ct(self):
        raw = b'Mary had a little lamb'
        raw = b'test'
        pt_b = b'\x00\x02' + b'\xff'*(self.bitlen//8-len(raw)-3)+b'\x00'+raw
        assert (len(pt_b)==self.bitlen//8)
        pt = int.from_bytes(pt_b,'big')
        print("pt_b:\t\t",pt_b)
        print("pt:\t\t", hex(pt))
        ct = self.enc_mesg(pt)
        return ct


if __name__ == "__main__":
    server = rsaOracleServer(1024)
    server.pf_keys()
    pt = 5
    ct = server.enc_mesg(pt)
    assert (server.dec_mesg(ct)==pt)
    ct = server.give_me_a_ct()
    print("parity_padding:", server.parity_oracle(ct))
    print("pkcs#1.5 padding:", server.pkcs_padding_oracle(ct))