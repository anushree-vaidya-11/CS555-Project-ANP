#Project Part II - Dealer implementation where the Private Key is reconstructed and messages are decrypted
#Author: Anushree Vaidya
#Date: 12/2/2022

import random
from math import ceil
from decimal import Decimal
import ast
import elgamal
from elgamal import PrivateKey

def reconstruct_sk(shares):
    """
    Combines individual shares (points on graph)
    using Lagranges interpolation.
 
    `shares` is a list of points (x, y) belonging to a
    polynomial with a constant of our key.
    """
    sums = 0
    prod_arr = []
 
    for j, share_j in enumerate(shares):
        xj, yj = share_j
        prod = Decimal(1)
 
        for i, share_i in enumerate(shares):
            xi, _ = share_i
            if i != j:
                prod *= Decimal(Decimal(xi)/(xi-xj))
 
        prod *= yj
        sums += Decimal(prod)
 
    return int(round(Decimal(sums), 0))

def dealer(data):
    p1 = {'c1': data[1].replace('\n', ''),'sk1':data[4].replace('\n', '')}
    p2 = {'c2': data[2].replace('\n', ''),'sk2':data[5].replace('\n', '')}
    p3 = {'c3':data[3].replace('\n', ''), 'sk3':data[6].replace('\n', '')}
    sk1 = p1['sk1']
    sk2 = p2['sk2']
    sk3 = p3['sk3']
    p = int(data[7].replace('\n', ''))
    g = int(data[8].replace('\n', ''))
    x = int(data[9].replace('\n', ''))
    sk1 = eval(sk1)
    sk2 = eval(sk2)
    sk3 = eval(sk3)
    print(sk1)
    shares =[sk1, sk2, sk3]
    #print(shares)
    t=3
    pool = random.sample(shares, t)
    #print(f'Combining shares: {", ".join(str(share) for share in pool)}')
    #print(f'Reconstructed secret: {reconstruct_sk(pool)}')
    sk = reconstruct_sk(pool)
    #print(sk)
    privateKey = PrivateKey(p, g, x, iNumBits=sk)

    c1 = p1['c1']
    c2 = p2['c2']
    c3 = p3['c3']
    print(type(c1))
    #print(type(c1))
    m1 = elgamal.decrypt(privateKey,c1)
    m2 = elgamal.decrypt(privateKey,c2)
    m3 = elgamal.decrypt(privateKey,c3)
    print(m1)

if __name__ == "__main__":
    MOD = 10001112223334445556667778889991
    with open('ip.txt', 'r') as f:
        data = f.readlines()
    print(data)

    num_iter = len(data)
    dealer(data)
    #check(data,num_iter,MOD)