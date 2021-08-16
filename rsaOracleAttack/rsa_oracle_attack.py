from rsaOracle import rsaOracleServer,mod_exp
import math
from bnUtil import mod_exp,mod_inv_gcd

server = rsaOracleServer(64)
server.pf_keys()
ct1 = server.give_me_a_ct()
nkey,ekey = server.give_me_pk()
print(server.pkcs_padding_oracle(ct1))

def floor(a,b):
    #ans =  math.floor(a/b)
    ans = a//b
    return ans

def ceil(a,b):
    #ans = math.ceil(a/b)
    ans = a//b + (a%b >1)
    return ans

def crack_parity_oracle_debug(ct):
    upper,lower = nkey,0
    tmp = ct
    doubling = mod_exp(2,ekey,nkey)
    cnt = 0
    while upper - lower > 1:
        print("-" * 40)
        print("lower\t", hex(lower))
        print("upper\t", hex(upper))
        cnt += 1
        tmp = tmp * doubling % nkey
        if server.parity_oracle(tmp) == 0:
            upper = (upper + lower)//2
        else:
            lower = (upper + lower)//2
        print("oracle:",server.parity_oracle(tmp))
        print("lower\t", hex(lower))
        print("upper\t", hex(upper))
    print("cnt =",cnt)
    print(lower.to_bytes(server.bitlen//8,'big'))

def crack_parity_oracle(ct):
    upper,lower = nkey,0
    tmp = ct
    doubling = mod_exp(2,ekey,nkey)
    cnt = 0
    while upper - lower > 1:
        cnt += 1
        tmp = tmp * doubling % nkey
        if server.parity_oracle(tmp) == 0:
            upper = (upper + lower)//2
        else:
            lower = (upper + lower)//2
        if cnt%20 == 0:
            print("-" * 40)
            print("lower\t", hex(lower))
            print("upper\t", hex(upper))
    print("#choosen_ct",cnt)
    print(lower.to_bytes(server.bitlen//8,'big'))

def pkcs_oracle_searching(ct,beg_val, stop=None):
    #return (s_i, ct_i, cnt_of_try)
    s0,ct0 = beg_val,ct
    cnt = 0
    while True:
        if (stop is not None) and s0 == stop:
            return None
        cnt += 1
        coff = mod_exp(s0,ekey,nkey)
        tmp = ct0*coff % nkey
        if server.pkcs_padding_oracle(tmp):
            ct0 = tmp
            break
        s0 += 1
        if cnt > 0 and cnt%100000==0:
            print("[+] searching cnt=",cnt)
    return (s0,ct0,cnt)

def order_sets_add(sets,new):
    # sets is increasing ordered by the value of intervals
    # sets = [(a0,b0),(a1,b1),...,(ak_bk)], ai<=bi, b_i < a_(i+1)
    if new[1]<new[0]:
        return sets
    if len(sets) == 0:
        return [new]
    left_index, right_index = 0,0
    mid = new
    for k in range(len(sets)):
        ak,bk = sets[k]
        if mid[0] > bk:
            left_index = k+1
            right_index = k+1
            continue
        elif mid[1] < ak:
            right_index = k
            break
        else:
            mid[0] = min(mid[0],ak)
            mid[1] = max(mid[1],bk)
    return sets[0:left_index] + [mid] + sets[right_index:]

def doc_m_list(m_list,pt):
    rslt = "["
    for a,b in m_list:
        rslt += "[" + a.to_bytes(server.bitlen // 8, 'big').hex() +","
        rslt += b.to_bytes(server.bitlen // 8, 'big').hex() +"]"
        ishere = "<-" if (pt >= a and pt <= b) else "xx"
        rslt += ishere + "\n"
    rslt += "]"
    return rslt

def crack_bleichenbache_oracle(ct,logs):
    logs.write("nkey = "+hex(server.Nkey)+"\n")
    logs.write("ekey = " + hex(server.ekey) + "\n")
    logs.write("dkey = " + hex(server.dkey) + "\n")
    logs.write("ct = 0x"+ct.to_bytes(server.bitlen // 8, 'big').hex()+"\n")
    pt = mod_exp(ct,server.dkey,nkey)
    logs.write("pt = %d"%pt + "\n")
    mark = "\n"+"-"*40+"\n"
    s_lyst,m_lyst = [],[]
    B = 1 << (server.bitlen - 16)
    B2 = B <<1
    B3 = B2 + B
    cost = 0
    #step_1:blinding
    logs.write(mark)
    logs.write("step-1:blinding"+"\n")
    s0,ct0,cnt = pkcs_oracle_searching(ct,1)
    cost += cnt
    logs.write("after [%d] steps, ct0 found"%cnt+"\n")
    logs.write("s0 = %s"%hex(s0)+"\n")
    s_lyst.append(s0)
    m_lyst.append([B2,B3-1])
    logs.write("MList = "  + doc_m_list(m_lyst,pt)+ "\n")
    # step2 find si
    i = 0
    logs.write(mark)
    logs.write("adaptive chosen ciphertext attack"+"\n")
    while True:
        i += 1
        logs.write("===[i=%d]==" % i +"\n")
        print("step ",i)
        if i == 1:
            s_beg = math.ceil(nkey/B3)
            si,cti,cnt = pkcs_oracle_searching(ct0,s_beg)
            cost += cnt
            s_lyst.append(si)
        else:
            if len(m_lyst) == 0:
                print("[!]searching error, abort!")
                return None
            elif len(m_lyst)==1:
                if m_lyst[0][1] - m_lyst[0][0] < 0x100:
                    # br the results:
                    for testv in range(m_lyst[0][0], m_lyst[0][1] + 1):
                        if ct0 == mod_exp(testv, ekey, nkey):
                            m_lyst = [[testv, testv]]
                            break
                else:
                    a, b = m_lyst[0]
                    ri = floor(2 * (b * s_lyst[-1] - B2),nkey)
                    while True:
                        s_beg = ceil(B2 + ri * nkey, b)
                        s_end = ceil(B3 + ri * nkey,a)
                        ret = pkcs_oracle_searching(ct0, s_beg, stop=s_end)
                        if ret is not None:
                            si, cti, cnt = ret
                            cost += cnt
                            s_lyst.append(si)
                            break
                        else:
                            ri += 1
            else:
                s_beg = s_lyst[-1] + 1
                si, cti, cnt = pkcs_oracle_searching(ct0, s_beg)
                cost += cnt
                s_lyst.append(si)
        if len(m_lyst)==1 and m_lyst[0][0]==m_lyst[0][1]:
            break
        # step3: narrowing set
        tmp = []
        si = s_lyst[-1]
        logs.write("narrowing wirh si="+hex(si) + "\n")
        for a,b in m_lyst:
            rmin = math.ceil((a*si-3*B+1)/nkey)
            rmax = math.ceil((b*si-B2)/nkey)
            logs.write(f"[narrowing] rmin={rmin}, rmax={rmax}, a={a}, b={b}" + "\n")
            print("rmax - rmin = %d"%(rmax-rmin))
            for r in range(rmin, rmax+1):
                aa = ceil(B2+r*nkey,si)
                bb = floor(B3+r*nkey-1,si)
                item = [max(a, aa), min(b, bb)]
                tmp = order_sets_add(tmp, item)
        m_lyst = tmp
        logs.write("length of MList is %d"%len(m_lyst)+"\n")
        logs.write("MList = "+doc_m_list(m_lyst,pt)+"\n")
    #step4
    logs.write(mark)
    logs.write("step 4"+"\n")
    rslt = m_lyst[0][0]
    if s0 > 1:
        s0inv = mod_inv_gcd(s0,nkey)
        rslt = (rslt * s0inv) % nkey
    logs.write("rslt: "+str(rslt.to_bytes(server.bitlen // 8, 'big'))+"\n")
    print(rslt.to_bytes(server.bitlen // 8, 'big'))

if __name__ == "__main__":
    #crack_parity_oracle(ct1)
    with open("./pkcs_log.txt","w") as fin:
        crack_bleichenbache_oracle(ct1, fin)
