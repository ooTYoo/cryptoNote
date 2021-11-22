from attack_demo import *

def testcase_chinese_remainder_calc():
    n = reduce(mul,prime_numbers[1:20])
    m = n//3
    print("n =",n.to_bytes(length=20,byteorder='big').hex())
    print("m =",m.to_bytes(length=20,byteorder='big').hex())
    m_lyst = [(m%prime_numbers[i],prime_numbers[i]) for i in range(1,20)]
    mm = chinese_remainder_calc(m_lyst)
    print("m =", mm.to_bytes(length=20, byteorder='big').hex())


def testcase_baby_step_gaint_step():
    N = prime_numbers[-1] **5
    #N = prime_numbers[-1]
    #n = (prime_numbers[-1]**4) * (prime_numbers[-1]-1)
    #n = prime_numbers[-1] - 1
    key = N//4
    a = 3
    b = mod_exp(a,key,N)
    ans = baby_step_gaint_step(a,b,N)
    print("N = ",N)
    print("a = ",a)
    print("b = ",b)
    print("key = ",key)
    print("ans = ",ans)


if __name__ == "__main__":
    #print(len(prime_numbers))
    #testcase_chinese_remainder_calc()
    testcase_baby_step_gaint_step()
