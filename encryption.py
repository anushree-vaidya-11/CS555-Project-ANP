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
    #print(data)
    p1 = {'c1': data[0].replace('\n', ''),'sk1':data[3].replace('\n', '')}
    p2 = {'c2': data[1].replace('\n', ''),'sk2':data[4].replace('\n', '')}
    p3 = {'c3':data[2].replace('\n', ''), 'sk3':data[5].replace('\n', '')}
    sk1 = p1['sk1']
    sk2 = p2['sk2']
    sk3 = p3['sk3']
    p = int(data[6].replace('\n', ''))
    g = int(data[7].replace('\n', ''))
    x = int(data[8].replace('\n', ''))
    sk1 = eval(sk1)
    sk2 = eval(sk2)
    sk3 = eval(sk3)
    #print(sk1)
    shares =[sk1, sk2, sk3]

    #print(shares)
    t=3
    pool = random.sample(shares, t)
    sk = reconstruct_sk(pool)

    #print(sk)
    privateKey = PrivateKey(p, g, x, iNumBits=sk)

    c1 = p1['c1']
    c2 = p2['c2']
    c3 = p3['c3']

    m1 = elgamal.decrypt(privateKey,c1)
    m2 = elgamal.decrypt(privateKey,c2)
    m3 = elgamal.decrypt(privateKey,c3)

    return (m1,m2,m3)