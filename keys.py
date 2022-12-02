#Project Part I - El Gamal implementation and input file creation
#Author: Anushree Vaidya
#Date: 12/1/2022

import elgamal
import math
import random
from math import ceil
from decimal import Decimal
 
FIELD_SIZE = 10**5

'''
def toBinary(a):
  l,m=[],[]
  for i in a:
    l.append(ord(i))
  for i in l:
    m.append(int(bin(i)[2:]))
  return m

m1 = toBinary("messageone")
m3 = toBinary("messagetwo")
m4 = toBinary("messagethree")
'''

def generation():
    keys = elgamal.generate_keys() #returns a dictionary {'privateKey': privateKeyObject, 'publicKey': publicKeyObject}
    publicKey = keys['publicKey']
    privateKey = keys['privateKey']
    c1 = elgamal.encrypt(publicKey, "m1") #Generating the cipher text to be shared with the parties
    c2 = elgamal.encrypt(publicKey, "m2")
    c3 = elgamal.encrypt(publicKey, "m3")
    #print(c1)
    plaintext = elgamal.decrypt(privateKey, c1)
    #print(plaintext)
    #print(type(publicKey))
    # (3,5) sharing scheme
    t, n = 3, 3  #n is number of parties and the polynomial will be of degree (t-1)
    secret = id(privateKey)
    #print(f'Secret Key: {secret}')
 
    # Phase I: Generation of shares
    shares = generate_shares(n, t, secret)

    #print(f'Shares: {", ".join(str(share) for share in shares)}')
    

    file1 = open('ip.txt', 'w')
    file1.write(c1+ '\n')
    file1.write(c2+ '\n')
    file1.write(c3+ '\n')
    for share in shares:
      file1.write(str(share)+ '\n')
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