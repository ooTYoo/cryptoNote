from cbcOracle import VictimServer
from Crypto.Cipher import AES
server = VictimServer()
iv,ct = server.give_me_a_ct()

def break_one_block(ct,ct_prv):
    zero_out = [0] * AES.block_size
    ct_prv = list(ct_prv)
    for padding in range(1,16+1):
        this_padding = [i^padding for i in zero_out]
        for val in range(256+1):
            if val==256:
                raise Exception("no val found in padding-0x%0x"%padding)
            try_pad = ct_prv[:-padding] + [val] + this_padding[16-padding+1:]
            if server.cbc_oracle(ct,bytes(try_pad)) == "No":
                continue
            if padding == 0x1:
                try_pad[16-padding-1] ^= 0xff
                if server.cbc_oracle(ct,bytes(try_pad)) == "No":
                    continue
            break
        zero_out[16-padding] = val^padding
    pt = [zero_out[i]^ct_prv[i] for i in range(len(ct))]
    return bytes(pt)

def cbc_oracle_attack(iv,ct):
    if len(ct)%16>0:
        raise Exception("[-]wrong input ciphertext length, pleaz check")
    block_num = len(ct)//16
    ct_array = [iv] + [ct[16*i:16*i+16] for i in range(block_num)]
    rslt = b''
    for k in range(block_num):
        pt = break_one_block(ct_array[k+1],ct_array[k])
        rslt += pt
        print(rslt)
