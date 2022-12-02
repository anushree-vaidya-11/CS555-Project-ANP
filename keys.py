#Project Part I - El Gamal implementation and input file creation
#Author: Anushree Vaidya
#Date: 12/1/2022

import elgamal
import math
import random
from math import ceil
from decimal import Decimal
from random import randint
 
FIELD_SIZE = 10**5

def generation():
    keys = elgamal.generate_keys() #returns a dictionary {'privateKey': privateKeyObject, 'publicKey': publicKeyObject, 'p': p, 'g': g, 'x': x}
    publicKey = keys['publicKey']
    privateKey = keys['privateKey']
    c1 = elgamal.encrypt(publicKey, "m1") #Generating the cipher text to be shared with the parties
    c2 = elgamal.encrypt(publicKey, "m2")
    c3 = elgamal.encrypt(publicKey, "m3")
    #print(privateKey.iNumBits)
    #print(elgamal.decrypt(privateKey, c1))
    #print(plaintext)
    #print(type(publicKey))
    # (3,5) sharing scheme
    t, n = 3, 3  #n is number of parties and the polynomial will be of degree (t-1)
    secret = (privateKey.iNumBits)
    #print(f'Secret Key: {secret}')
 
    # Phase I: Generation of shares
    shares = generate_shares(n, t, secret)
    #shares = _make_shares(secret, random=random)

    #print(f'Shares: {", ".join(str(share) for share in shares)}')
    
    p = keys['p']
    g = keys['g']
    x = keys['x']
    file1 = open('ip.txt', 'w')
    file1.write(str(secret)+ '\n')
    file1.write(c1+ '\n')
    file1.write(c2+ '\n')
    file1.write(c3+ '\n')
    for share in shares:
      #print(type(share))
      file1.write(str(share)+ '\n')
    file1.write(str(p)+ '\n')
    file1.write(str(g)+ '\n')
    file1.write(str(x)+ '\n')
    file1.close()

    file1 = open('ip.txt', 'r')
    print(file1.read())
    file1.close()

def polynom(x, coefficients):
    """
    This generates a single point on the graph of given polynomial
    in `x`. The polynomial is given by the list of `coefficients`.
    """
    point = 0
    # Loop through reversed list, so that indices from enumerate match the
    # actual coefficient indices
    for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
        point += x ** coefficient_index * coefficient_value
    return point


def coeff(t, secret):
    """
    Randomly generate a list of coefficients for a polynomial with
    degree of `t` - 1, whose constant is `secret`.
 
    For example with a 3rd degree coefficient like this:
        3x^3 + 4x^2 + 18x + 554
 
        554 is the secret, and the polynomial degree + 1 is
        how many points are needed to recover this secret.
        (in this case it's 4 points).
    """
    coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
    coeff.append(secret)
    return coeff


def generate_shares(n, m, secret):
    """
    Split given `secret` into `n` shares with minimum threshold
    of `m` shares to recover this `secret`, using SSS algorithm.
    """
    coefficients = coeff(m, secret)
    shares = []
 
    for i in range(1, n+1):
        x = random.randrange(1, FIELD_SIZE)
        shares.append((x, polynom(x, coefficients)))
 
    return shares

generation()