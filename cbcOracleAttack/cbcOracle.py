from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class VictimServer():
    def __init__(self):
        self.aes_key = b'+++You Can Not See Me++++'[0:AES.block_size]
        #self.iv = get_random_bytes(16)
        self.aes_engine_enc = AES.new(self.aes_key, AES.MODE_CBC, iv=self.iv)
        self.aes_engine_dec = AES.new(self.aes_key, AES.MODE_CBC, iv=self.iv)

    def enc(self,pt):
        return self.aes_engine_enc.encrypt(Padding.pad(pt,block_size=AES.block_size,style='pkcs7'))

    def dec(self,ct):
        try:
            pt = self.aes_engine_dec.decrypt(ct)
            return pt
        except Exception as e:
            print(e)
            return None

    def cbc_oracle(self,ct,iv):
        try:
            aes_engine = AES.new(self.aes_key, AES.MODE_CBC, iv)
            pt = aes_engine.decrypt(ct)
            pt = Padding.unpad(pt, block_size=AES.block_size, style='pkcs7')
            return "Yes"
        except :
            return "No"

    def give_me_a_ct(self):
        data = b'Mary had a little lamb, Its fleece was white as snow, And every where that Mary went, The lamb was sure to go'
        ct = self.enc(data)
        return self.iv,ct
